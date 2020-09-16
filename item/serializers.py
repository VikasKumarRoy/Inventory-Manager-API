from django.db import models, transaction
from django.template import loader
from base.tasks import send_email
from rest_framework import serializers
from rest_framework import exceptions
from item import exceptions as item_exception
from user.models import User
from item.models import ItemGroup, Item, ItemAttribute, RequestedItem, ApprovedItem, ItemHistory
from datetime import datetime

from utils import constants


class ItemGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemGroup
        fields = ('id', 'created_at', 'item_name', 'is_accessory',)

    def create(self, validated_data):
        admin = self.context['request'].user
        validated_data['added_by'] = admin
        validated_data['organization'] = admin.organization
        return super().create(validated_data)


class ItemAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemAttribute
        fields = ('id', 'created_at', 'attribute_name', 'attribute_value',)


class ItemSerializer(serializers.ModelSerializer):
    attributes = ItemAttributeSerializer(many=True, required=False)

    class Meta:
        model = Item
        fields = ('id', 'created_at', 'quantity', 'type', 'is_assigned', 'attributes')

    def create(self, validated_data):
        admin = self.context['request'].user
        item_group_id = self.context['item_group_id']
        try:
            item_group = ItemGroup.objects.select_related('organization').get(id=item_group_id)
            if item_group.organization.id != admin.organization.id:
                return item_exception.OrganizationException

            validated_data['item_group'] = item_group
            quantity = validated_data.get('quantity')
            if not quantity:
                quantity = 1

            if quantity <= 0:
                raise item_exception.NegativeOrZeroQuantityException

            if not item_group.is_accessory and quantity > 1:
                raise item_exception.InvalidQuantityException

            if item_group.is_accessory and validated_data['type'] != constants.ITEM_TYPE.PERMANENT:
                raise item_exception.InvalidItemAdd

            attributes = validated_data.get('attributes')
            validated_data.pop('attributes')

            item = super().create(validated_data)
            if attributes:
                item_attribute_serializer = ItemAttributeSerializer(data=attributes, many=True)
                item_attribute_serializer.is_valid(raise_exception=True)
                item_attribute_serializer.save(item=item)
            return item
        except models.ObjectDoesNotExist:
            raise exceptions.NotFound

    def update(self, instance, validated_data):

        if instance.is_assigned and not instance.item_group.is_accessory:
            raise item_exception.ItemUpdateException

        item_group = instance.item_group

        quantity = validated_data.get('quantity')
        attributes = validated_data.get('attributes')

        validated_data.clear()

        if quantity and item_group.is_accessory:
            validated_data['quantity'] = quantity

        if attributes:
            ItemAttribute.objects.filter(item=instance).delete()
            item_attribute_serializer = ItemAttributeSerializer(data=attributes, many=True)
            item_attribute_serializer.is_valid(raise_exception=True)
            item_attribute_serializer.save(item=instance)
        return super(ItemSerializer, self).update(instance, validated_data)


class RequestedItemSerializer(serializers.ModelSerializer):
    item_group_name = serializers.CharField(source='item_group.item_name', read_only=True)
    item_group_id = serializers.IntegerField(source='item_group.id', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.full_name', read_only=True)

    class Meta:
        model = RequestedItem
        fields = ('id', 'quantity', 'type', 'created_at', 'updated_at', 'item_group_id',
                  'item_group_name', 'status', 'requested_duration', 'requested_by_name', 'current_status_date')

    def create(self, validated_data):
        requested_user = self.context['request'].user
        validated_data['requested_by'] = requested_user
        item_group_id = self.context['item_group_id']

        if not requested_user.phone:
            raise item_exception.NoPhoneNumber

        try:
            item_group = ItemGroup.objects.select_related('organization').get(id=item_group_id)

            if item_group.organization.id != requested_user.organization.id:
                raise item_exception.OrganizationException

            validated_data['item_group'] = item_group
            quantity_requested = validated_data.get('quantity', 1)

            if quantity_requested <= 0:
                raise item_exception.NegativeOrZeroQuantityException

            if not item_group.is_accessory and quantity_requested > 1:
                raise item_exception.InvalidQuantityException

            if item_group.is_accessory and validated_data['type'] != constants.ITEM_TYPE.PERMANENT:
                raise item_exception.InvalidItemRequest

            requested_duration = validated_data.get('requested_duration')
            if requested_duration and validated_data['type'] == constants.ITEM_TYPE.PERMANENT:
                validated_data.pop('requested_duration')
            if not requested_duration and validated_data['type'] != constants.ITEM_TYPE.PERMANENT:
                raise item_exception.NoDuration
            if validated_data['type'] != constants.ITEM_TYPE.PERMANENT and requested_duration <= 0:
                raise item_exception.InvalidDuration
            return super().create(validated_data)
        except models.ObjectDoesNotExist:
            raise exceptions.NotFound


class ApprovedItemSerializer(serializers.ModelSerializer):
    item_group_name = serializers.CharField(source='approved_item.item_group.item_name', read_only=True)
    item_attributes = serializers.SerializerMethodField()
    type = serializers.IntegerField(source='approved_item.type', read_only=True)
    quantity = serializers.IntegerField(source='request.quantity', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    approved_to_name = serializers.CharField(source='approved_to.full_name', read_only=True)

    def get_item_attributes(self, approvedItem):
        attributes_list = approvedItem.approved_item.attributes
        return ItemAttributeSerializer(attributes_list, many=True).data

    class Meta:
        model = ApprovedItem
        fields = (
            'id', 'status', 'created_at', 'updated_at',
            'item_group_name', 'quantity', 'approved_duration',
            'item_attributes', 'type', 'current_status_date',
            'approved_by_name', 'approved_to_name'
        )

    def create(self, validated_data):
        approver_user = self.context['request'].user
        validated_data['approved_by'] = approver_user
        request_id = self.context['request_id']
        item_id = self.context['item_id']

        try:
            requested_item = RequestedItem.objects.select_related('item_group').get(id=request_id)
        except models.ObjectDoesNotExist:
            raise item_exception.NotFound

        if approver_user.organization.id != requested_item.item_group.organization.id:
            return item_exception.OrganizationException

        try:
            item = Item.objects.select_related('item_group').get(id=item_id)
        except models.ObjectDoesNotExist:
            raise item_exception.NotFound

        if approver_user.organization.id != item.item_group.organization.id:
            return item_exception.OrganizationException

        if requested_item.status != constants.REQUEST_STATUS.PENDING:
            raise item_exception.DestroyRequestException

        if item.item_group != requested_item.item_group:
            raise item_exception.ItemGroupMismatchError

        if item.type != requested_item.type:
            raise item_exception.InvalidItemRequest

        if item.is_assigned and item.type != constants.ITEM_TYPE.SHAREABLE:
            raise item_exception.ItemAlreadyAssigned

        if approver_user.role == constants.ROLE.USER:
            validated_data['approved_duration'] = requested_item.requested_duration

        approved_duration = validated_data.get('approved_duration')
        if approved_duration and item.type == constants.ITEM_TYPE.PERMANENT:
            validated_data.pop('approved_duration')
        if not approved_duration and item.type != constants.ITEM_TYPE.PERMANENT:
            raise item_exception.NoDuration
        if item.type != constants.ITEM_TYPE.PERMANENT and approved_duration <= 0:
            raise item_exception.InvalidDuration

        """
        1. Check if ITEM BEING APPROVED is already APPROVED TO USER with status ACKNOWLEDGED.
        2. Check if item is not SHAREABLE or is an ACCESSORY (raise exception).
        All good till here:
        FOR APPROVER:
            -> Change status of approved item to returned
            -> Mark is_assigned of that item as false
            -> Increment the quantity of that item accordingly
        """
        try:
            approver_user_approved_request = ApprovedItem.objects.select_related('request', 'approved_item__item_group').get(
                approved_to=approver_user,
                approved_item__item_group__is_accessory=False,
                approved_item__id=item.id,
                status=constants.ACKNOWLEDGE_STATUS.ACKNOWLEDGED
            )
            if item.type != constants.ITEM_TYPE.SHAREABLE or item.item_group.is_accessory:
                raise item_exception.ApproveNonShareableItemException

            with transaction.atomic():
                approver_user_approved_request.status = constants.ACKNOWLEDGE_STATUS.RETURNED
                item.is_assigned = False
                item.quantity += approver_user_approved_request.request.quantity
                approver_user_approved_request.save()
        except models.ObjectDoesNotExist:
            if approver_user.role == constants.ROLE.USER:
                raise item_exception.NotFound

        if requested_item.quantity > item.quantity:
            raise item_exception.InvalidQuantityApproveException

        with transaction.atomic():
            item.quantity = item.quantity - requested_item.quantity
            if item.quantity == 0:
                item.is_assigned = True
            requested_item.status = constants.REQUEST_STATUS.APPROVED
            requested_item.current_status_date = datetime.now()
            item.save()
            requested_item.save()

        validated_data['request'] = requested_item
        validated_data['approved_to'] = requested_item.requested_by
        validated_data['approved_item'] = item
        instance = super().create(validated_data)
        recipient_email = requested_item.requested_by.email
        context = {
            'first_name': approver_user.first_name,
            'full_name': "{first_name} {last_name}".format(first_name=approver_user.first_name,
                                                           last_name=approver_user.last_name),
            'email': approver_user.email,
            'role': "Admin" if approver_user.role == constants.ROLE.ADMIN else (
                "Manager" if approver_user.role == constants.ROLE.MANAGER else "User"),
            'organization_name': approver_user.organization.name,
            'item_group_name': item.item_group.item_name,
            'quantity': requested_item.quantity
        }
        html_message = loader.get_template('approved.html').render(context)
        send_email.delay(html_message=html_message, recipient_email=recipient_email, subject=constants.SUBJECT_REQUEST_APPROVED)
        return instance

    def update(self, instance, validated_data):
        item_type = instance.approved_item.type
        if item_type == constants.ITEM_TYPE.PERMANENT:
            raise item_exception.InvalidItemTypeDuration
        if instance.status == constants.ACKNOWLEDGE_STATUS.RETURNED:
            raise item_exception.ReturnItemUpdateDuration
        approved_duration = validated_data.get('approved_duration')
        if not approved_duration or approved_duration <= 0:
            raise item_exception.InvalidDuration
        return super(ApprovedItemSerializer, self).update(instance, validated_data)


class MyRequestStatsSerializer(serializers.Serializer):
    requests_pending = serializers.IntegerField()
    requests_approved = serializers.IntegerField()
    requests_cancelled = serializers.IntegerField()
    requests_rejected = serializers.IntegerField()
    requests_total = serializers.IntegerField()


class MyApproveStatsSerializer(serializers.Serializer):
    approve_pending = serializers.IntegerField()
    approve_acknowledged = serializers.IntegerField()
    approve_returned = serializers.IntegerField()
    approve_total = serializers.IntegerField()


class UserSmallSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'profile_picture', 'role',)


class ItemSmallSerializer(serializers.ModelSerializer):
    item_group_name = serializers.CharField(source='item_group.item_name')

    class Meta:
        model = Item
        fields = ('id', 'quantity', 'item_group_name', 'type')


class ItemHistorySerializer(serializers.ModelSerializer):
    approved_by = serializers.SerializerMethodField()
    approved_to = serializers.SerializerMethodField()
    item = serializers.SerializerMethodField()

    approved_quantity = serializers.IntegerField(source='approved.request.quantity', read_only=True)
    requested_duration = serializers.IntegerField(source='approved.request.requested_duration', read_only=True)
    approved_duration = serializers.IntegerField(source='approved.approved_duration', read_only=True)
    requested_at = serializers.DateTimeField(source='approved.request.created_at', read_only=True)
    approved_at = serializers.DateTimeField(source='approved.created_at', read_only=True)

    def get_approved_by(self, obj):
        return UserSmallSerializer(obj.approved.approved_by).data

    def get_approved_to(self, obj):
        return UserSmallSerializer(obj.approved.approved_to).data

    def get_item(self, obj):
        return ItemSmallSerializer(obj.approved.approved_item).data

    class Meta:
        model = ItemHistory
        fields = (
            'id', 'created_at', 'status',
            'approved_by', 'approved_to', 'item',
            'approved_quantity', 'requested_duration', 'approved_duration', 'requested_at', 'approved_at'
        )
