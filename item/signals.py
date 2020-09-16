from django.db.models.signals import post_save
from django.dispatch import receiver
from item.models import ApprovedItem
from item.models import ItemHistory


@receiver(post_save, sender=ApprovedItem, dispatch_uid="log_to_history")
def log_to_history(sender, instance, **kwargs):
    item_history = ItemHistory.objects.create(
        approved=instance,
        status=instance.status
    )
