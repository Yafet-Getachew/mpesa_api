from celery import chain
from mpesa_api.core.tasks import send_b2c_request_task, process_b2c_call_response_task, \
    call_online_checkout_task, handle_online_checkout_response_task
from django.db.models.signals import post_save
from django.dispatch import receiver

from mpesa_api.core.models import B2CRequest, OnlineCheckout


@receiver(post_save, sender=B2CRequest)
def handle_b2c_request_post_save(sender, instance, **kwargs):
    """
    Handles B2CRequest post_save
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """

    # call the mpesa
    chain(send_b2c_request_task.s(int(instance.amount), instance.phone, instance.id),
          process_b2c_call_response_task.s(instance.id)).apply_async(queue='b2c_request')


@receiver(post_save, sender=OnlineCheckout)
def handle_online_checkout_post_save(sender, instance, **Kwargs):
    """
    Handle online checkout post save
    :param sender:
    :param instance:
    :param Kwargs:
    :return:
    """
    # online checkout
    chain(call_online_checkout_task.s(instance.phone, int(instance.amount), instance.account_reference,
                                      instance.transaction_description),
          handle_online_checkout_response_task.s(instance.id)).apply_async(queue='online_checkout_request')