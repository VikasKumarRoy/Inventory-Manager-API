from django.db import models
from base.models import BaseModel
from user.models import User
from organization.models import Organization
from utils import constants


class ItemGroup(BaseModel):
    item_name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='item_groups')
    added_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='item_groups')
    is_accessory = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return "{id} {name}".format(id=self.id, name=self.item_name)


class Item(BaseModel):
    quantity = models.IntegerField(default=1)
    item_group = models.ForeignKey(ItemGroup, on_delete=models.CASCADE, related_name='items')
    type = models.PositiveSmallIntegerField(choices=constants.ITEM_TYPE_CHOICES, default=constants.ITEM_TYPE.RETURNABLE)
    is_assigned = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return "{id} {name} {type}".format(id=str(self.id),
                                           name=self.item_group.item_name,
                                           type=constants.ITEM_TYPE_CHOICES[0][1] if self.type == constants.ITEM_TYPE.SHAREABLE else (
                                               constants.ITEM_TYPE_CHOICES[1][1] if self.type == constants.ITEM_TYPE.RETURNABLE else
                                               constants.ITEM_TYPE_CHOICES[2][1]))


class ItemAttribute(BaseModel):
    attribute_name = models.CharField(max_length=100)
    attribute_value = models.CharField(max_length=100)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='attributes')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.attribute_name


class RequestedItem(BaseModel):
    item_group = models.ForeignKey(ItemGroup, on_delete=models.DO_NOTHING, related_name='requests')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    requested_duration = models.IntegerField(blank=True, null=True)
    type = models.PositiveSmallIntegerField(choices=constants.ITEM_TYPE_CHOICES)
    status = models.PositiveSmallIntegerField(choices=constants.REQUEST_STATUS_CHOICES, default=constants.REQUEST_STATUS.PENDING)
    quantity = models.IntegerField(default=1)

    current_status_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return "{id} {name} {type} {status}".format(id=str(self.id),
                                                    name=self.item_group.item_name,
                                                    type=constants.ITEM_TYPE_CHOICES[0][
                                                        1] if self.type == constants.ITEM_TYPE.SHAREABLE else (
                                                        constants.ITEM_TYPE_CHOICES[1][
                                                            1] if self.type == constants.ITEM_TYPE.RETURNABLE else
                                                        constants.ITEM_TYPE_CHOICES[2][1]),
                                                    status=constants.REQUEST_STATUS_CHOICES[0][
                                                        1] if self.status == constants.REQUEST_STATUS.PENDING
                                                    else (constants.REQUEST_STATUS_CHOICES[1][
                                                              1] if self.status == constants.REQUEST_STATUS.APPROVED
                                                          else (constants.REQUEST_STATUS_CHOICES[2][
                                                                    1] if self.status == constants.REQUEST_STATUS.CANCELLED
                                                                else constants.REQUEST_STATUS_CHOICES[2][1])))


class ApprovedItem(BaseModel):
    request = models.OneToOneField(RequestedItem, on_delete=models.CASCADE, related_name='approved_request')
    approved_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='items_approved_by')
    approved_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items_approved_to')
    approved_duration = models.IntegerField(blank=True, null=True)
    approved_item = models.ForeignKey(Item, on_delete=models.DO_NOTHING, related_name='approved_items')
    status = models.PositiveSmallIntegerField(choices=constants.ACKNOWLEDGE_STATUS_CHOICES, default=constants.ACKNOWLEDGE_STATUS.PENDING)

    current_status_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return "{id} {name} {request_status} {status}".format(id=str(self.id),
                                                              name=self.approved_item.item_group.item_name,
                                                              request_status=constants.REQUEST_STATUS_CHOICES[0][
                                                                  1] if self.request.status == constants.REQUEST_STATUS.PENDING
                                                              else (constants.REQUEST_STATUS_CHOICES[1][
                                                                        1] if self.request.status == constants.REQUEST_STATUS.APPROVED
                                                                    else (constants.REQUEST_STATUS_CHOICES[2][
                                                                              1] if self.request.status == constants.REQUEST_STATUS.CANCELLED
                                                                          else constants.REQUEST_STATUS_CHOICES[2][1])),
                                                              status=constants.ACKNOWLEDGE_STATUS_CHOICES[0][
                                                                  1] if self.status == constants.ACKNOWLEDGE_STATUS.PENDING
                                                              else (constants.ACKNOWLEDGE_STATUS_CHOICES[1][
                                                                        1] if self.status == constants.ACKNOWLEDGE_STATUS.ACKNOWLEDGED
                                                                    else (constants.ACKNOWLEDGE_STATUS_CHOICES[2][1])))


class ItemHistory(BaseModel):
    approved = models.ForeignKey(ApprovedItem, on_delete=models.DO_NOTHING, null=True)
    status = models.PositiveSmallIntegerField(choices=constants.ACKNOWLEDGE_STATUS_CHOICES, default=constants.ACKNOWLEDGE_STATUS.PENDING)

    class Meta:
        ordering = ['-created_at']
