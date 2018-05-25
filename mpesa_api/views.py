from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.views import APIView
from mpesa_api.tasks import process_b2c_result_response_task, \
    process_c2b_confirmation_task, process_c2b_validation_task, \
    handle_online_checkout_callback_task
from mpesa_api.mpesa import Mpesa
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from edxmako.shortcuts import render_to_string
from mpesa_api.models import B2CRequest, C2BRequest, OnlineCheckout, \
    B2CResponse, OnlineCheckoutResponse
from django.core.urlresolvers import reverse

class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

class B2cTimeOut(APIView):
    """
    Handle b2c time out
    """
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    @csrf_exempt
    def post(self, request, format=None):
        """
        process the timeout
        :param request:
        :param format:
        :return:
        """
        data = request.data
        return Response(dict(value='ok', key='status', detail='success'))


class B2cResult(APIView):
    """
    Handle b2c result
    """
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    @csrf_exempt
    def post(self, request, format=None):
        """
        process the timeout
        :param request:
        :param format:
        :return:
        """
        data = request.data
        queue = 'edx.lms.core.high'
        chain = process_b2c_result_response_task.s(data).set(queue=queue)
        chain()
        return Response(dict(value='ok', key='status', detail='success'))


class C2bValidation(APIView):
    """
    Handle c2b Validation
    """
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    @csrf_exempt
    def post(self, request, format=None):
        """
        process the c2b Validation
        :param request:
        :param format:
        :return:
        """
        data = request.data
        queue = 'edx.lms.core.high'
        chain = process_c2b_validation_task.s(data).set(queue=queue)
        chain()
        return Response(dict(value='ok', key='status', detail='success'))


class C2bConfirmation(APIView):
    """
    Handle c2b Confirmation
    """
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    @csrf_exempt
    def post(self, request, format=None):
        """
        process the confirmation
        :param request:
        :param format:
        :return:
        """
        data = request.data
        queue = 'edx.lms.core.high'
        chain = process_c2b_confirmation_task.s(data).set(queue=queue)
        chain()
        return Response(dict(value='ok', key='status', detail='success'))


class OnlineCheckoutCallback(APIView):
    """
    Handle online checkout callback
    """
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    @csrf_exempt
    def post(self, request, order_id):
        """
        process the confirmation
        :param request:
        :param format:
        :return:
        """
        data = request.data
        queue = 'edx.lms.core.high'
        chain = handle_online_checkout_callback_task.s(data, order_id).set(queue=queue)
        chain()
        return Response(dict(value='ok', key='status', detail='success'))


class Order(APIView):
    """

    """
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    @csrf_exempt
    def post(self, request, format=None):
        """
        process the confirmation
        :param request:
        :param format:
        :return:
        """
        data = request.data
        return render_to_string('mpesa/mpesa_form.html', {
            'action': '/mpesa/payment_request/',
            'params': {
                'cmd': '_xclick',
                'charset': 'utf-8',
                'currency_code': data['currency_code'],
                'amount': data['amount'],
                'item_name': data['item_name'],
                'custom': data['custom'],
                'business': data['business'],
                'notify_url': data['notify_url'],
                'cancel_return': data['cancel_return'],
                'return': data['return'],
            }
        })




class MpesaPayment(APIView):
    """

    """
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    @csrf_exempt
    def post(self, request, format=None):
        """
        process the confirmation
        :param request:
        :param format:
        :return:
        """
        data = request.data

        data['payment_status'] = 'Completed'
        amount, account_reference = data['amount'], data['item_name']

        if amount and account_reference:
            Mpesa.b2c_request(254700000000, amount)  # starts a b2c payment
            Mpesa.c2b_register_url()  # registers the validate and confirmation url's for b2c
            # starts online checkout on given number
            Mpesa.stk_push(254700000000, amount, account_reference=account_reference, orderId = custom)
            return Response(dict(value='ok', key='status', detail='success', check_url=reverse('check_payment_order')))  # TODO: change to return true dict
        else:
            return Response(dict(value='fail', key='status', detail='fail', check_url=""))  # TODO: change to return false dict


class CheckStatusOfPayment(APIView):
    """

    """
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    @csrf_exempt
    def post(self, request, format=None):
        """
        process the confirmation
        :param request:
        :param format:
        :return:
        """
        data = request.data
        order_id =  data['order_id']
        response = OnlineCheckoutResponse.objects.get(order_id=order_id)
        if response:
            return Response(dict(value='ok' if response.result_code == 0  else 'fail' , key='1', detail=response.result_description))
        else:
            return Response(dict(value='in progress', key='0', detail='in progress'))