from __future__ import absolute_import, unicode_literals

from decimal import Decimal

from celery import shared_task

from mpesa_api.models import B2CRequest, C2BRequest, OnlineCheckout, \
    B2CResponse, OnlineCheckoutResponse
from mpesa_api.util.b2cutils import send_b2c_request
from celery.contrib import rdb
import logging
from django.conf import settings
from mpesa_api.models import AuthToken
from mpesa_api.util.http import post
import base64
import json
from datetime import datetime
logger = logging.getLogger(__name__)


@shared_task(name='b2c_call')
def send_b2c_request_task(amount, phone, id):
    """
    task for send a b2c request
    :param amount:
    :param phone:
    :param id:
    :return:
    """
    return send_b2c_request(amount, phone, id)


@shared_task(name='handle_b2c_call_response')
def process_b2c_call_response_task(response, id):
    """
    process the request sent back from b2c request
    :param response:
    :param id:
    :return:
    """
    data = response
    B2CRequest.objects.filter(pk=id).update(
        request_id=data.get('requestId', ''),
        error_code=data.get('errorCode', ''),
        error_message=data.get('errorMessage', ''),
        conversation_id=data.get('ConversationID', ''),
        originator_conversation_id=data.get('OriginatorConversationID', ''),
        response_code=data.get('ResponseCode', ''),
        response_description=data.get('ResponseDescription', '')
    )
    rdb.set_trace()


@shared_task(name='handle_b2c_result_response')
def process_b2c_result_response_task(response):
    """
    Process b2c result
    :param response:
    :return:
    """
    try:
        data = response.get('Result', '')
        update_data = dict()
        update_data['result_type'] = str(data.get('ResultType', ''))
        update_data['result_code'] = str(data.get('ResultCode', ''))
        update_data['result_description'] = data.get('ResultDesc', '')
        update_data['transaction_id'] = data.get('TransactionID', '')
        update_data['originator_conversation_id'] = data.get('OriginatorConversationID', '')
        update_data['conversation_id'] = data.get('ConversationID', '')

        params = data.get('ResultParameters', {}).get('ResultParameter', {})

        if len(params) > 0:
            # means that we have data doe we handle that
            for p in params:
                key, value = p.values()

                if key == 'TransactionReceipt':
                    update_data['transaction_receipt'] = value
                elif key == 'TransactionAmount':
                    update_data['transaction_amount'] = value
                    update_data['amount'] = value
                elif key == 'B2CWorkingAccountAvailableFunds':
                    update_data['working_funds'] = value
                elif key == 'B2CUtilityAccountAvailableFunds':
                    rupdate_data['utility_funds'] = value
                elif key == 'B2CChargesPaidAccountAvailableFunds':
                    update_data['paid_account_funds'] = value
                elif key == 'TransactionCompletedDateTime':
                    date, time = value.split(' ')
                    day, month, year = date.split('.')
                    trx_date = '{}-{}-{} {}'.format(year, month, day, time)
                    update_data['transaction_date'] = trx_date
                elif key == 'ReceiverPartyPublicName':
                    phone, name = value.split(' - ')
                    update_data['mpesa_user_name'] = name
                    update_data['phone'] = int(phone)
                elif key == 'B2CRecipientIsRegisteredCustomer':
                    update_data['is_registered_customer'] = value

        # save
        B2CResponse.objects.create(**update_data)
    except Exception as ex:
        pass


@shared_task(name='handle_c2b_validation')
def process_c2b_validation_task(response):
    """
    Handle c2b request
    {
        "TransactionType": "Pay Bill",
        "TransID": "LK631GQCSP",
        "TransTime": "20171106225323",
        "TransAmount": "100.00",
        "BusinessShortCode": "600000",
        "BillRefNumber": "Test",
        "InvoiceNumber": "",
        "OrgAccountBalance": "",
        "ThirdPartyTransID": "",
        "MSISDN": "254708374149",
        "FirstName": "John",
        "MiddleName": "J.",
        "LastName": "Doe"
    }
    :param response:
    :return:
    """
    date = response.get('TransTime', '')
    year, month, day, hour, min, sec = date[:4], date[4:-8], date[6:-6], date[8:-4], date[10:-2], date[12:]
    org_balance = 0.0
    if response.get('OrgAccountBalance', ''):
        org_balance = Decimal(response.get('OrgAccountBalance'))
    data = dict(
        transaction_type=response.get('TransactionType', ''),
        transaction_id=response.get('TransID', ''),
        transaction_date='{}-{}-{} {}:{}:{}'.format(year, month, day, hour, min, sec),
        amount=Decimal(response.get('TransAmount', '0')),
        business_short_code=response.get('BusinessShortCode', ''),
        bill_ref_number=response.get('BillRefNumber', ''),
        invoice_number=response.get('InvoiceNumber', ''),
        org_account_balance=org_balance,
        third_party_trans_id=response.get('ThirdPartyTransID', ''),
        phone=int(response.get('MSISDN', '0')),
        first_name=response.get('FirstName', ''),
        middle_name=response.get('MiddleName', ''),
        last_name=response.get('LastName', ''),
        is_validated=True
    )

    C2BRequest.objects.create(**data)


@shared_task(name='handle_c2b_confirmation')
def process_c2b_confirmation_task(response):
    """
    Handle c2b request
    {
        "TransactionType": "Pay Bill",
        "TransID": "LK631GQCSP",
        "TransTime": "20171106225323",
        "TransAmount": "100.00",
        "BusinessShortCode": "600000",
        "BillRefNumber": "Test",
        "InvoiceNumber": "",
        "OrgAccountBalance": "",
        "ThirdPartyTransID": "",
        "MSISDN": "254708374149",
        "FirstName": "John",
        "MiddleName": "J.",
        "LastName": "Doe"
    }
    :param response:
    :return:
    """
    date = response.get('TransTime', '')
    year, month, day, hour, min, sec = date[:4], date[4:-8], date[6:-6], date[8:-4], date[10:-2], date[12:]
    org_balance = 0.0
    if response.get('OrgAccountBalance', ''):
        org_balance = Decimal(response.get('OrgAccountBalance'))

    data = dict(
        transaction_type=response.get('TransactionType', ''),
        transaction_id=response.get('TransID', ''),
        transaction_date='{}-{}-{} {}:{}:{}'.format(year, month, day, hour, min, sec),
        amount=Decimal(response.get('TransAmount', '0')),
        business_short_code=response.get('BusinessShortCode', ''),
        bill_ref_number=response.get('BillRefNumber', ''),
        invoice_number=response.get('InvoiceNumber', ''),
        org_account_balance=org_balance,
        third_party_trans_id=response.get('ThirdPartyTransID', ''),
        phone=int(response.get('MSISDN', '0')),
        first_name=response.get('FirstName', ''),
        middle_name=response.get('MiddleName', ''),
        last_name=response.get('LastName', ''),
        is_completed=True
    )

    try:
        req = C2BRequest.objects.filter(transaction_id=response.get('TransID', ''))

        if req:
            C2BRequest.objects.filter(transaction_id=response.get('TransID', '')).update(is_completed=True)
        else:
            C2BRequest.objects.create(**data)
    except Exception as ex:
        pass


# @shared_task(name='make_online_checkout_call')
# def call_online_checkout_task(phone, amount, account_reference, transaction_desc):
#     """
#     Handle online checkout request
#     :param phone:
#     :param amount:
#     :param transaction_ref:
#     :param transaction_desc:
#     :return:
#     """
#     return process_online_checkout(phone, amount, account_reference, transaction_desc)


@shared_task(name='handle_online_checkout_response')
def handle_online_checkout_response_task(response, transaction_id):
    """
    Handle checkout response
    :param response:
    :param id:
    :return:
    """
    OnlineCheckout.objects.filter(pk=transaction_id).update(
        checkout_request_id=response.get('CheckoutRequestID', ''),
        customer_message=response.get('CustomerMessage', ''),
        merchant_request_id=response.get('MerchantRequestID', ''),
        response_code=response.get('ResponseCode', ''),
        response_description=response.get('ResponseDescription', '')
    )


def call_online_checkout_and_response(msisdn, amount, account_reference, transaction_desc, transaction_id, order_id):
    """
    Handle the online checkout
    :param msisdn:
    :param amount:
    :param account_reference:
    :param transaction_desc:
    :return:
    """
    url = settings.C2B_ONLINE_CHECKOUT_URL
    headers = {"Content-Type": 'application/json',
               'Authorization': 'Bearer {}'.format(AuthToken.objects.get_token('c2b'))}
    timestamp = str(datetime.now())[:-7].replace('-', '').replace(' ', '').replace(':', '')
    password = base64.b64encode('{}{}{}'.format(settings.C2B_ONLINE_SHORT_CODE, settings.C2B_ONLINE_PASSKEY,
                                                      timestamp)).decode('utf-8')
    body = dict(
        BusinessShortCode=settings.C2B_ONLINE_SHORT_CODE,
        Password=password,
        Timestamp=timestamp,
        TransactionType=settings.C2B_TRANSACTION_TYPE,
        Amount=str(amount),
        PartyA=str(msisdn),
        PartyB=settings.C2B_ONLINE_SHORT_CODE,
        PhoneNumber=str(msisdn),
        CallBackURL=settings.C2B_ONLINE_CHECKOUT_CALLBACK_URL.format("order_id"),
        AccountReference=account_reference,
        TransactionDesc=transaction_desc
    )
    response = post(url=url, headers=headers, data=json.dumps(body))
    response = response.json()
    OnlineCheckout.objects.filter(pk=transaction_id).update(
        checkout_request_id=response.get('CheckoutRequestID', ''),
        customer_message=response.get('CustomerMessage', ''),
        merchant_request_id=response.get('MerchantRequestID', ''),
        response_code=response.get('ResponseCode', ''),
        response_description=response.get('ResponseDescription', '')
    )

@shared_task(name='handle_online_checkout_callback')
def handle_online_checkout_callback_task(response, order_id):
    """
    Process the callback response
    :param response:
    :return:

     Accepted
    ========
    {
      "Body":{
        "stkCallback":{
          "MerchantRequestID":"19465-780693-1",
          "CheckoutRequestID":"ws_CO_27072017154747416",
          "ResultCode":0,
          "ResultDesc":"The service request is processed successfully.",
          "CallbackMetadata":{
            "Item":[
              {
                "Name":"Amount",
                "Value":1
              },
              {
                "Name":"MpesaReceiptNumber",
                "Value":"LGR7OWQX0R"
              },
              {
                "Name":"Balance"
              },
              {
                "Name":"TransactionDate",
                "Value":20170727154800
              },
              {
                "Name":"PhoneNumber",
                "Value":254721566839
              }
            ]
          }
        }
      }
    }

    Canceled
    =========
    {
      "Body":{
        "stkCallback":{
          "MerchantRequestID":"8555-67195-1",
          "CheckoutRequestID":"ws_CO_27072017151044001",
          "ResultCode":1032,
          "ResultDesc":"[STK_CB - ]Request cancelled by user"
        }
      }
    """
    try:
        data = response.get('Body', {}).get('stkCallback', {})
        update_data = dict()
        update_data['result_code'] = data.get('ResultCode', '')
        update_data['result_description'] = data.get('ResultDesc', '')
        update_data['checkout_request_id'] = data.get('CheckoutRequestID', '')
        update_data['merchant_request_id'] = data.get('MerchantRequestID', '')
        update_data['order_id'] = order_id

        meta_data = data.get('CallbackMetadata', {}).get('Item', {})
        if len(meta_data) > 0:
            # handle the meta data
            for item in meta_data:
                if len(item.values()) > 1:
                    key, value = item.values()
                    if key == 'MpesaReceiptNumber':
                        update_data['mpesa_receipt_number'] = value
                    if key == 'Amount':
                        update_data['amount'] = Decimal(value)
                    if key == 'PhoneNumber':
                        update_data['phone'] = int(value)
                    if key == 'TransactionDate':
                        date = str(value)
                        year, month, day, hour, min, sec = date[:4], date[4:-8], date[6:-6], date[8:-4], date[10:-2], date[12:]
                        update_data['transaction_date'] = '{}-{}-{} {}:{}:{}'.format(year, month, day, hour, min, sec)

        # save
        OnlineCheckoutResponse.objects.create(**update_data)
        logger.info(dict(updated_data=update_data))
    except Exception as ex:
        logger.error(ex)
        raise ValueError(str(ex))
