import base64
import json
from datetime import datetime

from django.conf import settings

from mpesa_api.models import AuthToken
from mpesa_api.util.http import post
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers


def register_c2b_url():
    """
    Register the c2b_url
    :return:
    """
    url = configuration_helpers.get_value('C2B_REGISTER_URL', settings.C2B_REGISTER_URL)
    headers = {"Content-Type": 'application/json',
               'Authorization': 'Bearer {}'.format(AuthToken.objects.get_token('c2b'))}
    body = dict(
        ShortCode=configuration_helpers.get_value('C2B_SHORT_CODE', settings.C2B_SHORT_CODE),
        ResponseType= configuration_helpers.get_value('C2B_RESPONSE_TYPE', settings.C2B_RESPONSE_TYPE),
        ConfirmationURL= configuration_helpers.get_value('C2B_CONFIRMATION_URL', settings.C2B_CONFIRMATION_URL),
        ValidationURL= configuration_helpers.get_value('C2B_VALIDATE_URL', settings.C2B_VALIDATE_URL)
    )
    response = post(url=url, headers=headers, data=json.dumps(body))
    return response.json()


# def process_online_checkout(msisdn, amount, account_reference, transaction_desc):
#     """
#     Handle the online checkout
#     :param msisdn:
#     :param amount:
#     :param account_reference:
#     :param transaction_desc:
#     :return:
#     """
#     url = settings.C2B_ONLINE_CHECKOUT_URL
#     headers = {"Content-Type": 'application/json',
#                'Authorization': 'Bearer {}'.format(AuthToken.objects.get_token('c2b'))}
#     timestamp = str(datetime.now())[:-7].replace('-', '').replace(' ', '').replace(':', '')
#     password = base64.b64encode(bytes('{}{}{}'.format(settings.C2B_ONLINE_SHORT_CODE, settings.C2B_ONLINE_PASSKEY,
#                                                       timestamp), 'utf-8')).decode('utf-8')
#     body = dict(
#         BusinessShortCode=settings.C2B_ONLINE_SHORT_CODE,
#         Password=password,
#         Timestamp=timestamp,
#         TransactionType=settings.C2B_TRANSACTION_TYPE,
#         Amount=str(amount),
#         PartyA=str(msisdn),
#         PartyB=settings.C2B_ONLINE_SHORT_CODE,
#         PhoneNumber=str(msisdn),
#         CallBackURL=settings.C2B_ONLINE_CHECKOUT_CALLBACK_URL,
#         AccountReference=account_reference,
#         TransactionDesc=transaction_desc
#     )
#     response = post(url=url, headers=headers, data=json.dumps(body))
#     return response.json()
