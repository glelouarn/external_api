from time import gmtime, strftime
from random import randint

from django.db import models

import payment


ORDER_STATUS = {'COMPLETE': 'complete', 'PENDING': 'pending', 'INCOMPLETE': 'incomplete', 'CANCELLED': 'cancelled'}
TEST_ORDINAL = '0'


class Instrument:
    def __init__(self, method, card_number, cvv, exp_year, exp_month):
        self.method = method
        self.card_number = card_number
        self.cvv = cvv
        self.exp_year = exp_year
        self.exp_month = exp_month


class Charge(models.Model):
    status = models.CharField(max_length=20, default=ORDER_STATUS['INCOMPLETE'])
    amount = models.DecimalField(decimal_places=5, max_digits=14)
    currency = models.CharField(max_length=3)

    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey('auth.User', related_name='charges', serialize=False)

    trans_id = models.CharField(max_length=6, serialize=False, null=True)
    trans_date = models.CharField(max_length=14, serialize=False, null=True)

    def get_instruments(self):
        return self._instruments
    def set_instruments(self, value):
        self._instruments = value
    used_instruments = property(get_instruments, set_instruments)

    messages = []
    methods = []
    _instruments = []

    def __init__(self, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)

        if self.trans_id is None:
            self.trans_id = str(randint(0, 99999)).rjust(6, '0')
        if self.trans_date is None:
            self.trans_date = strftime('%Y%m%d%H%M%S', gmtime())

    def construct_urls(self):
        urls = []
        pay_url = payment.vad.PAYMENT_URL + 'exec.refresh.a?cacheId=' + self.cache_id()
        urls.append({'href': pay_url, 'rel': 'redirect', 'method': 'get'})
        return urls

    def update_from_form_submit(self, http_response):
        if http_response == 200:
            self.status = ORDER_STATUS['PENDING']
        else:
            self.status = ORDER_STATUS['CANCELLED']

    def update_from_silent_form_submit(self, http_response):
        if http_response == 200:
            self.status = ORDER_STATUS['COMPLETE']
        else:
            self.status = ORDER_STATUS['CANCELLED']

    def update_from_context(self, context_json):
        del self.methods[:]
        del self.messages[:]


        if self.status == ORDER_STATUS['PENDING']:
            if context_json is None:
                self.status = ORDER_STATUS['CANCELLED']
            else:
                for pay_method in context_json['methods']:
                    self.methods.append({'method': pay_method['card_type']})
                if len(self.methods) > 1:
                    self.messages = [{'title': 'PAYMENT_INSTRUMENT_REQUIRED'},
                                     {'description': 'Transaction is incomplete. No payment instrument was chosen.'}]

    def update_from_payment(self, get_info_response, save=True):
        if get_info_response.errorCode == 0:
            self._instruments = [Instrument(get_info_response.cardInfo.cardBrand, get_info_response.cardInfo.cardNumber, 123, get_info_response.cardInfo.expiryYear, get_info_response.cardInfo.expiryMonth)]

            if get_info_response.transactionStatus in (1, 4, 5, 6):
                self.status = ORDER_STATUS['COMPLETE']
            else:
                self.status = ORDER_STATUS['CANCELLED']

            del self.messages[:]
            del self.methods[:]

            if save:
                self.save()

    def site_id(self):
        return self.owner.username[0:8]

    def site_key(self):
        return self.owner.username[9:]

    def cache_id(self):
        return self.site_id() + self.trans_date[2:8] + self.trans_id + TEST_ORDINAL

    def __str__(self):
        return str(self.pk) + ' - ' + str(self.status) + ' - ' + repr(self.created)

    class Meta:
        ordering = ('created',)