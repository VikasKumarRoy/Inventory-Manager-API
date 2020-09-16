from django.db.models import ObjectDoesNotExist, Count
from django.db import transaction
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters
from datetime import datetime
from base.tasks import send_email
from item.filters import ItemHistoryFilter
from item.models import Item, ItemGroup, RequestedItem, ApprovedItem, ItemHistory
from item.permissions import IsAdminOrManagerActions, IsAdminOrManager
from item.serializers import (ItemGroupSerializer, ItemSerializer,
                              RequestedItemSerializer, ApprovedItemSerializer,
                              MyRequestStatsSerializer, MyApproveStatsSerializer,
                              ItemHistorySerializer)
from item import exceptions as item_exception
from django.template import loader
from utils import constants


class ItemGroupView(viewsets.ModelViewSet):
    """
    View to CRUD ItemGroup
    Permissions: Only ADMIN and MANAGERS are allowed WRITE OPERATIONS
                 USERS can LIST and RETRIEVE
    Filters: ?is_accessory={Boolean} (optional)
    """
    permission_classes = (IsAdminOrManagerActions,)
    serializer_class = ItemGroupSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    search_fields = ('item_name',)
    filterset_fields = ('is_accessory',)

    lookup_field = 'id'

    def get_queryset(self):
        """
        Filters ItemGroups of currentUser's organization
        :return: Filtered QuerySet
        """
        user = self.request.user
        return ItemGroup.objects.filter(organization=user.organization)

    def perform_destroy(self, instance):
        """
        Check if all items of type RETURNABLE/SHAREABLE of this group are returned
        :param instance: Item group to be deleted
        :return: default
        """
        assigned_item_count = instance.items.filter(is_assigned=True).exclude(
            type=constants.ITEM_TYPE.PERMANENT).count()
        if assigned_item_count != 0:
            raise item_exception.InvalidItemGroupDelete
        return super(ItemGroupView, self).perform_destroy(instance)


class ItemView(viewsets.ModelViewSet):
    """
    View to CRUD Items in a ItemGroup
    Permissions: Only ADMIN and MANAGERS are allowed WRITE OPERATIONS
                 USERS can LIST and RETRIEVE
    Filters: ?is_assigned={Boolean}&type={item_type}
    item_type:  SHAREABLE=13,
                RETURNABLE=14,
                PERMANENT=15
    """
    permission_classes = (IsAdminOrManagerActions,)
    serializer_class = ItemSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    search_fields = ('attributes__attribute_name', 'attributes__attribute_value',)
    filterset_fields = ('type', 'is_assigned',)
    lookup_field = 'id'

    def get_queryset(self):
        """
        Filters Items of a particular ItemGroup
        :return: Filtered QuerySet
        """
        item_group_id = self.kwargs['item_group_id']
        user = self.request.user
        return Item.objects.select_related('item_group').filter(item_group__organization=user.organization,
                                                                item_group__id=item_group_id)

    def get_serializer_context(self):
        """
        Adds ItemGroupID to serializer context
        """
        item_group_id = self.kwargs['item_group_id']
        return {'item_group_id': item_group_id, 'request': self.request}

    def perform_destroy(self, instance):
        """
        Check if item is assigned to some user, user has to return it before delete.
        :param instance: Item to be deleted
        :return: default
        """
        if instance.is_assigned and instance.type != constants.ITEM_TYPE.PERMANENT:
            raise item_exception.InvalidItemDelete
        super(ItemView, self).perform_destroy(instance)

    @action(methods=['GET'], detail=False)
    def user(self, request, item_group_id):
        """
        Method returns items which should be shown to user when its approving a request
        :param request: default
        :param item_group_id: ItemGroup ID of the request being approved
        :return: List of items
        """
        item_ids = ApprovedItem.objects.select_related('approved_item__item_group').filter(
            approved_to=request.user, status=constants.ACKNOWLEDGE_STATUS.ACKNOWLEDGED,
            approved_item__item_group__id=item_group_id,
            approved_item__type=constants.ITEM_TYPE.SHAREABLE
        ).values_list('approved_item__id', flat=True)

        qs = self.get_queryset().filter(id__in=item_ids)
        item_serializer = ItemSerializer(qs, many=True)
        return Response(data=item_serializer.data, status=status.HTTP_200_OK)


class ItemHistoryView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAdminOrManagerActions,)
    serializer_class = ItemHistorySerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ItemHistoryFilter
    lookup_field = 'id'

    def get_queryset(self):
        item_group_id = self.kwargs['item_group_id']
        item_id = self.kwargs['item_id']
        return ItemHistory.all_objects.select_related(
            'approved__approved_to',
            'approved__approved_by',
            'approved__request',
            'approved__approved_item__item_group__organization'
        ).filter(
            approved__approved_item__item_group__organization=self.request.user.organization,
            approved__approved_item__id=item_id
        )


class RequestedItemView(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    View to create, read and delete a request.
    To cancel a request, hit DELETE api to change request status to CANCELLED. (Only if request status is PENDING)
    Permissions: Authenticated user
    Filters: ?type={requested_item_type}&status={request_status}
    requested_item_type:  SHAREABLE=13,
                        RETURNABLE=14,
                        PERMANENT=15

    request_status:     PENDING=7,
                        APPROVED=8,
                        CANCELLED=9,
                        REJECTED=18
    """
    serializer_class = RequestedItemSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('type', 'status',)
    lookup_field = 'id'

    def get_queryset(self):
        """
        RequestedItems requested_by currentUser and belongs to the URL param item_group_id
        :return: Filtered QuerySet
        """
        user = self.request.user
        item_group_id = self.kwargs['item_group_id']
        return RequestedItem.objects.select_related(
            'item_group', 'requested_by'
        ).filter(requested_by=user, item_group__id=item_group_id)

    def get_serializer_context(self):
        """
        Adds ItemGroupID to serializer context
        """
        item_group_id = self.kwargs['item_group_id']
        return {'item_group_id': item_group_id, 'request': self.request}

    def perform_destroy(self, instance):
        """
        Changes request status from PENDING to CANCELLED, else exception.
        :param instance: RequestedItem to be CANCELLED
        :return: HTTP_204_NO_CONTENT if success else exception
        """
        if instance.status is constants.REQUEST_STATUS.PENDING:
            instance.status = constants.REQUEST_STATUS.CANCELLED
            instance.current_status_date = datetime.now()
            instance.save()
            return status.HTTP_204_NO_CONTENT
        raise item_exception.DestroyRequestException


class ManageRequestView(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    Manage requests which are requested from me.
    (If USER, then can only approve shared item group requests whose all items have been assigned.
    ADMIN and MANAGER can approve all requests)
    To reject a request, hit DELETE api and RequestedItem status will be changed to REJECTED (Only if request status is PENDING)
    Filters: ?type={requested_item_type}
    requested_item_type:SHAREABLE=13,
                        RETURNABLE=14,
                        PERMANENT=15
    """
    serializer_class = RequestedItemSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    search_fields = ('item_group__item_name',)
    filterset_fields = ('type',)
    lookup_field = 'id'

    def get_queryset(self):
        """
        Filters QuerySet according to user's role.
        USER - Those requests whose itemGroup's all items are assigned, status PENDING and ItemGroupIds fall in Items currently approved to user.
        ADMIN/MANAGER - All requests of currentUser's oragnization with status PENDING
        :return: Filtered QuerySet
        """
        user = self.request.user
        if user.role == constants.ROLE.USER:
            item_group_ids = ApprovedItem.objects.select_related(
                'approved_to',
                'approved_item'
            ).filter(
                approved_to=user,
                status=constants.ACKNOWLEDGE_STATUS.ACKNOWLEDGED,
                approved_item__type=constants.ITEM_TYPE.SHAREABLE
            ).values_list('approved_item__item_group__id', flat=True)
            return RequestedItem.objects.select_related(
                'requested_by',
                'item_group__organization'
            ).prefetch_related(
                'item_group__items'
            ).filter(
                item_group__id__in=item_group_ids,
                status=constants.REQUEST_STATUS.PENDING,
                type=constants.ITEM_TYPE.SHAREABLE
            ).exclude(item_group__items__is_assigned=False)
        return RequestedItem.objects.select_related('requested_by', 'item_group__organization').filter(
            item_group__organization=user.organization,
            status=constants.REQUEST_STATUS.PENDING
        )

    def perform_destroy(self, instance):
        """
        When approvers cancel reject requests
        Changes request status from PENDING to REJECTED else exception
        :param instance: RequestedItem to be REJECTED
        :return: HTTP_204_NO_CONTENT if success else exception
        """
        if instance.status is constants.REQUEST_STATUS.PENDING:
            instance.status = constants.REQUEST_STATUS.REJECTED
            instance.current_status_date = datetime.now()
            instance.save()
            return status.HTTP_204_NO_CONTENT
        raise item_exception.DestroyRequestException


class MyRequests(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    All RequestedItems requested by currentUser
    Filters: ?type={requested_item_type}&status={request_status}
    requested_item_type:SHAREABLE=13,
                        RETURNABLE=14,
                        PERMANENT=15

    request_status:     PENDING=7,
                        APPROVED=8,
                        CANCELLED=9,
                        REJECTED=18
    """
    serializer_class = RequestedItemSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    search_fields = ('item_group__item_name',)
    filterset_fields = ('type', 'status',)
    lookup_field = 'id'

    def get_queryset(self):
        return RequestedItem.objects.select_related(
            'requested_by',
            'item_group__organization'
        ).filter(requested_by=self.request.user)

    def perform_destroy(self, instance):
        """
        When users cancel their own requests
        Changes request status from PENDING to CANCELLED else exception
        :param instance - RequestedItem to be REJECTED
        :return - HTTP_204_NO_CONTENT if success else exception
        """
        if instance.status is constants.REQUEST_STATUS.PENDING:
            instance.status = constants.REQUEST_STATUS.CANCELLED
            instance.current_status_date = datetime.now()
            instance.save()
            return status.HTTP_204_NO_CONTENT
        raise item_exception.DestroyRequestException

    @action(methods=['GET'], detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        requests_pending = 0
        requests_approved = 0
        requests_cancelled = 0
        requests_rejected = 0

        result = qs.values('status').order_by().annotate(count=Count('status'))
        for elem in result:
            if elem['status'] == constants.REQUEST_STATUS.PENDING:
                requests_pending = elem['count']
            elif elem['status'] == constants.REQUEST_STATUS.APPROVED:
                requests_approved = elem['count']
            elif elem['status'] == constants.REQUEST_STATUS.CANCELLED:
                requests_cancelled = elem['count']
            elif elem['status'] == constants.REQUEST_STATUS.REJECTED:
                requests_rejected = elem['count']

        request_stats_serializer = MyRequestStatsSerializer(data={
            'requests_pending': requests_pending,
            'requests_approved': requests_approved,
            'requests_cancelled': requests_cancelled,
            'requests_rejected': requests_rejected,
            'requests_total': requests_pending + requests_approved + requests_cancelled + requests_rejected
        })
        request_stats_serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK, data=request_stats_serializer.data)


class ApprovedItemView(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    View to Create, Read ApprovedItems
    Permissions: Authenticated user
    Filters: ?request__type={type}&status={acknowledge_status}
    request__type:  SHAREABLE=13,
                    RETURNABLE=14,
                    PERMANENT=15

    acknowledge_status:PENDING=10,
                    ACKNOWLEDGED=11,
                    RETURNED=12
    """
    serializer_class = ApprovedItemSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('request__type', 'status',)
    lookup_field = 'id'

    def get_queryset(self):
        """
        ApprovedItem approved_by currentUser
        :return: Filtered QuerySet
        """
        user = self.request.user
        return ApprovedItem.objects.select_related(
            'approved_item__item_group'
        ).prefetch_related('approved_item__attributes').filter(approved_by=user)

    def get_serializer_context(self):
        """
        Adds request_id, item_id to serializer context
        """
        request_id = self.kwargs['request_id']
        item_id = self.kwargs['item_id']
        return {'request_id': request_id, 'item_id': item_id, 'request': self.request}


class MyApproved(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    View to LIST, RETRIEVE, ACKNOWLEDGE and RETURN Items approved_to currentUser
    Permissions: Authenticated user
    Filters: ?request__type={type}&status={acknowledge_status}
    request__type:  SHAREABLE=13,
                    RETURNABLE=14,
                    PERMANENT=15

    acknowledge_status:PENDING=10,
                    ACKNOWLEDGED=11,
                    RETURNED=12
    """
    serializer_class = ApprovedItemSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    search_fields = ('request__item_group__item_name', 'approved_item__attributes__attribute_name',
                     'approved_item__attributes__attribute_value')
    filterset_fields = ('request__type', 'status',)
    lookup_field = 'id'

    def get_queryset(self):
        """
        ApprovedItem approved_to currentUser
        :return: Filtered QuerySet
        """
        user = self.request.user
        return ApprovedItem.objects.select_related(
            'approved_item__item_group'
        ).prefetch_related('approved_item__attributes').filter(approved_to=user)

    @action(methods=['POST'], detail=True)
    def acknowledge_item(self, request, id):
        """
        Method to acknowledge an approved request
        :param request: default
        :param id: approved_item_id
        :return: response or raise exception
        """
        try:
            approved_request = self.get_queryset().get(id=id)
            if approved_request.status == constants.ACKNOWLEDGE_STATUS.PENDING:
                approved_request.status = constants.ACKNOWLEDGE_STATUS.ACKNOWLEDGED
                approved_request.current_status_date = datetime.now()
                approved_request.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            raise item_exception.AcknowledgeItemException
        except ObjectDoesNotExist:
            raise item_exception.NotFound

    @action(methods=['POST'], detail=True)
    def return_item(self, request, id):
        """
        Method to return an item
        :param request: default
        :param id: approved_item_id
        :return: response or raise exception
        """
        try:
            approved_request = self.get_queryset().select_related('approved_item').get(id=id)
            if approved_request.approved_item.type == constants.ITEM_TYPE.PERMANENT or approved_request.approved_item.item_group.is_accessory:
                raise item_exception.ReturnPermanentItemException

            if approved_request.status == constants.ACKNOWLEDGE_STATUS.ACKNOWLEDGED:
                with transaction.atomic():
                    approved_request.status = constants.ACKNOWLEDGE_STATUS.RETURNED
                    approved_request.current_status_date = datetime.now()
                    approved_request.approved_item.is_assigned = False
                    approved_request.approved_item.quantity += approved_request.request.quantity

                    approved_request.approved_item.save()
                    approved_request.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            raise item_exception.ReturnItemException
        except ObjectDoesNotExist:
            raise item_exception.NotFound

    @action(methods=['GET'], detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        approve_pending = 0
        approve_acknowledged = 0
        approve_returned = 0

        result = qs.values('status').order_by().annotate(count=Count('status'))
        for elem in result:
            if elem['status'] == constants.ACKNOWLEDGE_STATUS.PENDING:
                approve_pending = elem['count']
            elif elem['status'] == constants.ACKNOWLEDGE_STATUS.ACKNOWLEDGED:
                approve_acknowledged = elem['count']
            elif elem['status'] == constants.ACKNOWLEDGE_STATUS.RETURNED:
                approve_returned = elem['count']

        approve_stats_serializer = MyApproveStatsSerializer(data={
            'approve_pending': approve_pending,
            'approve_acknowledged': approve_acknowledged,
            'approve_returned': approve_returned,
            'approve_total': approve_pending + approve_acknowledged + approve_returned
        })
        approve_stats_serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK, data=approve_stats_serializer.data)


class MyOrganizationRequests(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAdminOrManager,)
    serializer_class = RequestedItemSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    search_fields = ('item_group__item_name', 'requested_by__first_name', 'requested_by__last_name',)
    filterset_fields = ('type', 'status',)

    def get_queryset(self):
        user = self.request.user
        return RequestedItem.objects.select_related(
            'requested_by',
            'item_group__organization'
        ).filter(item_group__organization=user.organization)

    @action(methods=['GET'], detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        requests_pending = 0
        requests_approved = 0
        requests_cancelled = 0
        requests_rejected = 0

        result = qs.values('status').order_by().annotate(count=Count('status'))
        for elem in result:
            if elem['status'] == constants.REQUEST_STATUS.PENDING:
                requests_pending = elem['count']
            elif elem['status'] == constants.REQUEST_STATUS.APPROVED:
                requests_approved = elem['count']
            elif elem['status'] == constants.REQUEST_STATUS.CANCELLED:
                requests_cancelled = elem['count']
            elif elem['status'] == constants.REQUEST_STATUS.REJECTED:
                requests_rejected = elem['count']

        request_stats_serializer = MyRequestStatsSerializer(data={
            'requests_pending': requests_pending,
            'requests_approved': requests_approved,
            'requests_cancelled': requests_cancelled,
            'requests_rejected': requests_rejected,
            'requests_total': requests_pending + requests_approved + requests_cancelled + requests_rejected
        })
        request_stats_serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK, data=request_stats_serializer.data)


class MyOrganizationApprovedRequests(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAdminOrManager,)
    serializer_class = ApprovedItemSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    search_fields = ('approved_item__item_group__item_name', 'approved_by__first_name', 'approved_to__first_name',
                     'approved_by__last_name', 'approved_to__last_name',)
    filterset_fields = ('request__type', 'status',)
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        return ApprovedItem.objects.select_related(
            'approved_item__item_group__organization'
        ).prefetch_related('approved_item__attributes').filter(approved_item__item_group__organization=user.organization)

    @action(methods=['GET'], detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        approve_pending = 0
        approve_acknowledged = 0
        approve_returned = 0

        result = qs.values('status').order_by().annotate(count=Count('status'))
        for elem in result:
            if elem['status'] == constants.ACKNOWLEDGE_STATUS.PENDING:
                approve_pending = elem['count']
            elif elem['status'] == constants.ACKNOWLEDGE_STATUS.ACKNOWLEDGED:
                approve_acknowledged = elem['count']
            elif elem['status'] == constants.ACKNOWLEDGE_STATUS.RETURNED:
                approve_returned = elem['count']

        approve_stats_serializer = MyApproveStatsSerializer(data={
            'approve_pending': approve_pending,
            'approve_acknowledged': approve_acknowledged,
            'approve_returned': approve_returned,
            'approve_total': approve_pending + approve_acknowledged + approve_returned
        })
        approve_stats_serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK, data=approve_stats_serializer.data)

    @action(methods=['GET'], detail=True)
    def send_reminder(self, request, id):
        try:
            approved_item = ApprovedItem.objects.select_related(
                'approved_to', 'request'
            ).get(
                id=id,
                request__item_group__organization=request.user.organization
            )

            if approved_item.status == constants.ACKNOWLEDGE_STATUS.PENDING:
                recipient_email = approved_item.approved_to.email
                context = {
                    'num_items': 1
                }
                html_message = loader.get_template('pending_acknowledge.html').render(context)
                send_email.delay(html_message=html_message, recipient_email=recipient_email,
                                 subject=constants.SUBJECT_REMINDER_TO_ACKNOWLEDGE)
            elif approved_item.status == constants.ACKNOWLEDGE_STATUS.ACKNOWLEDGED:
                recipient_email = approved_item.approved_to.email
                context = {
                    'num_items': 1
                }
                html_message = loader.get_template('pending_return.html').render(context)
                send_email.delay(html_message=html_message, recipient_email=recipient_email,
                                 subject=constants.SUBJECT_REMINDER_TO_RETURN)
            return Response(status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
