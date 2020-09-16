from django.db.models import F
from django.db.models.aggregates import Count
from django.core.mail import send_mail
from django.conf import settings
from django.template import loader
from hardwareManager.celery import app
import html2text
from item.models import ApprovedItem
from utils.helpers import send_mass_html_mail
from utils.constants import ACKNOWLEDGE_STATUS, ITEM_TYPE
from datetime import datetime, timedelta
from utils import constants


@app.task
def send_email(html_message, recipient_email, subject):
    h = html2text.HTML2Text()
    h.ignore_links = False
    send_mail(
        html_message=html_message,
        subject=subject,
        message=h.handle(html_message),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[recipient_email]
    )


@app.task
def check_for_pending_acknowledgement():
    """
    Checks periodically, if there are any pending requests which user haven't approved yet.
    :return: void
    """
    qs = ApprovedItem.objects.select_related(
        'approved_item',
        'approved_to'
    ).filter(
        status=ACKNOWLEDGE_STATUS.PENDING,
        created_at__lt=datetime.now() - timedelta(days=1)
    ).values(
        'approved_to__email'
    ).order_by().annotate(
        num_of_items=Count('approved_to')
    )

    h = html2text.HTML2Text()
    h.ignore_links = False
    data_list = []
    for item in qs:
        recipient_email = item.get('approved_to__email')
        context = {
            'num_items': item.get('num_of_items')
        }
        html_message = loader.get_template('pending_acknowledge.html').render(context)
        data_list.append(
            (constants.SUBJECT_REMINDER_TO_ACKNOWLEDGE, h.handle(html_message), html_message, settings.EMAIL_HOST_USER, [recipient_email])
        )
    send_mass_html_mail(datatuple=tuple(data_list))


@app.task
def check_for_pending_returns():
    """
    Checks periodically whether there are some items whose return date has passed but user haven't returned yet.
    :return: void
    """
    qs = ApprovedItem.objects.select_related(
        'approved_item',
        'approved_to'
    ).filter(
        approved_item__type__in=[ITEM_TYPE.RETURNABLE, ITEM_TYPE.SHAREABLE],
        status=ACKNOWLEDGE_STATUS.ACKNOWLEDGED,
        current_status_date__lt=datetime.now() - timedelta(days=1) * F('approved_duration')
    ).values(
        'approved_to__email'
    ).order_by().annotate(
        num_of_items=Count('approved_to')
    )

    h = html2text.HTML2Text()
    h.ignore_links = False
    data_list = []
    for item in qs:
        recipient_email = item.get('approved_to__email')
        context = {
            'num_items': item.get('num_of_items')
        }
        html_message = loader.get_template('pending_return.html').render(context)
        data_list.append(
            (constants.SUBJECT_REMINDER_TO_RETURN, h.handle(html_message), html_message, settings.EMAIL_HOST_USER, [recipient_email])
        )
    send_mass_html_mail(datatuple=tuple(data_list))


@app.on_after_finalize.connect
def setup_periodic_task(sender, **kwargs):
    sender.add_periodic_task(settings.NOTIFICATIONS_JOB_INTERVAL, check_for_pending_acknowledgement.s(), name='pending approved items reminder')
    sender.add_periodic_task(settings.NOTIFICATIONS_JOB_INTERVAL, check_for_pending_returns.s(), name='pending return items reminder')
