from rest_framework import status
from rest_framework.exceptions import APIException


class NoPhoneNumber(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cannot request an item without phone number, please add your phone number and try again."
    default_code = 'invalid'


class InvalidItemGroupDelete(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cannot delete this item group as it's non-permanent items are currently assigned."
    default_code = 'invalid'


class NegativeOrZeroQuantityException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Quantity cannot be less than or equal to zero.'
    default_code = 'invalid'


class InvalidQuantityException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Item group is not an accessory. Quantity should be equal to one.'
    default_code = 'invalid'


class InvalidQuantityRequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Can't more than 1 quantity for non-accessory items."
    default_code = 'invalid'


class InvalidItemRequest(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid item request."
    default_code = 'invalid'


class InvalidItemAdd(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid item. Accessories can't be shared or returned"
    default_code = 'invalid'


class InvalidItemDelete(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cannot delete this item as it is currently assigned to a user."
    default_code = 'invalid'


class OrganizationException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Trying to access content from other organization"
    default_code = 'invalid'


class NotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Not Found"
    default_code = 'invalid'


class DestroyRequestException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Either request is approved, rejected or cancelled."
    default_code = 'invalid'


class AcknowledgeItemException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Either item is already acknowledged or returned."
    default_code = 'invalid'


class ReturnItemException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Either item is already returned or not acknowledged."
    default_code = 'invalid'


class ReturnPermanentItemException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Either item is issued permanently or is an accessory."
    default_code = 'invalid'


class ApproveNonShareableItemException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Cannot share a non-shareable item. If you're having this item, please return it and try again."
    default_code = 'invalid'


class ItemAlreadyAssigned(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Item is already assigned to some user."
    default_code = 'invalid'


class ItemGroupMismatchError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Item group didn't match with request."
    default_code = 'invalid'


class InvalidQuantityApproveException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Can't assign more quantity than available."
    default_code = 'invalid'


class NoDuration(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Duration not provided for RETURNABLE/SHAREABLE item."
    default_code = 'invalid'


class InvalidDuration(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Duration must be greater than 0."
    default_code = 'invalid'


class InvalidItemTypeDuration(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cannot update duration for permanent items."
    default_code = 'invalid'


class ReturnItemUpdateDuration(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cannot update duration for returned items."
    default_code = 'invalid'


class ItemUpdateException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cannot update item, it's currently assigned."
    default_code = 'invalid'


class ItemPendingReminder(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cannot send reminder, approved item should be atleast 24hrs old."
    default_code = 'invalid'
