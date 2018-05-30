from celery import chain
from mpesa_api.tasks import send_b2c_request_task, process_b2c_call_response_task, \
     handle_online_checkout_response_task, call_online_checkout_and_response

from django.dispatch import receiver
from mpesa_api.models import B2CRequest, OnlineCheckout
from django.db.models.signals import post_save
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from django.conf import settings
from mpesa_api.models import AuthToken

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
    queue = "edx.lms.core.high"
    url = configuration_helpers.get_value('B2C_URL', settings.B2C_URL)
    B2C_INITIATOR_NAME = configuration_helpers.get_value('B2C_INITIATOR_NAME', settings.B2C_INITIATOR_NAME)
    B2C_SECURITY_TOKEN = configuration_helpers.get_value('B2C_SECURITY_TOKEN', settings.B2C_SECURITY_TOKEN)
    B2C_COMMAND_ID = configuration_helpers.get_value('B2C_COMMAND_ID', settings.B2C_COMMAND_ID)
    B2C_SHORTCODE = configuration_helpers.get_value('B2C_SHORTCODE', settings.B2C_SHORTCODE)
    B2C_QUEUE_TIMEOUT_URL = configuration_helpers.get_value('B2C_QUEUE_TIMEOUT_URL', settings.B2C_QUEUE_TIMEOUT_URL)
    B2C_RESULT_URL = configuration_helpers.get_value('B2C_RESULT_URL', settings.B2C_RESULT_URL)
    AuthToken_Var = AuthToken.objects.get_token('b2c')
    chain = send_b2c_request_task.s(int(instance.amount), instance.phone, instance.id,
                                    url, B2C_INITIATOR_NAME, B2C_SECURITY_TOKEN, B2C_COMMAND_ID,
                                    B2C_SHORTCODE, B2C_QUEUE_TIMEOUT_URL, B2C_RESULT_URL, AuthToken_Var).set(queue=queue) | \
            process_b2c_call_response_task.s(instance.id).set(queue=queue)
    chain()


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
    queue = "edx.lms.core.high"
    url = configuration_helpers.get_value('C2B_ONLINE_CHECKOUT_URL', settings.C2B_ONLINE_CHECKOUT_URL)
    C2B_ONLINE_SHORT_CODE = configuration_helpers.get_value('C2B_ONLINE_SHORT_CODE', settings.C2B_ONLINE_SHORT_CODE)
    C2B_ONLINE_PASSKEY = configuration_helpers.get_value('C2B_ONLINE_PASSKEY', settings.C2B_ONLINE_PASSKEY)
    C2B_TRANSACTION_TYPE = configuration_helpers.get_value('C2B_TRANSACTION_TYPE', settings.C2B_TRANSACTION_TYPE)
    C2B_ONLINE_CHECKOUT_CALLBACK_URL = configuration_helpers.get_value('C2B_ONLINE_CHECKOUT_CALLBACK_URL',
                                                                       settings.C2B_ONLINE_CHECKOUT_CALLBACK_URL)
    AuthToken_Var = AuthToken.objects.get_token('c2b')
    chain = call_online_checkout_and_response.s(instance.phone, int(instance.amount), instance.account_reference,
                                                instance.transaction_description, instance.id, instance.order_id,
                                                url, C2B_ONLINE_SHORT_CODE, C2B_ONLINE_PASSKEY,
                                                C2B_TRANSACTION_TYPE, C2B_ONLINE_CHECKOUT_CALLBACK_URL,
                                                AuthToken_Var).set(queue=queue)
    chain()
