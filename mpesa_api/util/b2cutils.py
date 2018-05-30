import json

from django.conf import settings

from mpesa_api.models import AuthToken
from mpesa_api.util.http import post
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers


def send_b2c_request(amount, phone_number, transaction_id,
                     url, B2C_INITIATOR_NAME, B2C_SECURITY_TOKEN, B2C_COMMAND_ID,
                     B2C_SHORTCODE, B2C_QUEUE_TIMEOUT_URL, B2C_RESULT_URL, AuthToken, occassion=''):
    """
    seds a b2c request
    :param amount:
    :param phone_numer:
    :return:
    """
    headers = {"Content-Type": 'application/json',
               'Authorization': 'Bearer {}'.format(AuthToken)}
    request = dict(
        InitiatorName=B2C_INITIATOR_NAME,
        SecurityCredential=B2C_SECURITY_TOKEN,
        CommandID=B2C_COMMAND_ID,
        Amount=str(amount),
        PartyA=B2C_SHORTCODE,
        PartyB=str(phone_number),
        Remarks="record-{}".format(str(transaction_id)),
        QueueTimeOutURL=B2C_QUEUE_TIMEOUT_URL,
        ResultURL=B2C_RESULT_URL,
        Occassion=occassion
    )

    response = post(url=url, headers=headers, data=json.dumps(request))
    return response.json()
