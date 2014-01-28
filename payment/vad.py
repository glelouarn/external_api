import hashlib
import json
from datetime import datetime

import urllib3
from suds.client import Client


SERVER_URL = 'https://payzen.leon.lyra-network.com/'
PAYMENT_URL = SERVER_URL + 'vads-payment/'
ORDER_URL = PAYMENT_URL + 'service/order?cacheId='
WS_URL = SERVER_URL + 'vads-ws/v4?wsdl'
TEST_STR = 'TEST'


class PaymentFormManager:
    def submit_payment_form(self, charge):
        params = self._get_payment_params(charge)

        signature = ""
        for f in sorted(params.keys()):
            signature += params[f] + '+'
        params['signature'] = hashlib.sha1((signature + charge.site_key()).encode('utf-8')).hexdigest()

        return urllib3.PoolManager().request('POST', PAYMENT_URL, fields=params).status


    def request_payment_from_ws(self, charge):
        signature = charge.site_id() + '+' + charge.trans_id + '+' + str(1) + '+' + TEST_STR + '+' + charge.site_key()
        ws_format_trans_date = datetime.strptime(charge.trans_date, "%Y%m%d%H%M%S").strftime("%Y-%m-%dT%H:%M:%S+00:00")

        client = Client(WS_URL)
        print(client)
        return client.service.getInfo(charge.site_id(), ws_format_trans_date,
                                      charge.trans_id, 1, TEST_STR,
                                      hashlib.sha1((signature).encode('utf-8')).hexdigest())


    def request_payment_context(self, charge):
        response = urllib3.PoolManager().request('GET', ORDER_URL + charge.cache_id())
        try:
            json_content = json.loads(str(response.data), 'UTF-8')
            return json_content
        except ValueError:
            pass

    def make_silent_payment(self, charge):
        params = self._get_silent_payment_params(charge)

        signature = ""
        for f in sorted(params.keys()):
            signature += params[f] + '+'
        params['signature'] = hashlib.sha1((signature + charge.site_key()).encode('utf-8')).hexdigest()

        status = urllib3.PoolManager().request('POST', PAYMENT_URL, fields=params).status


    def _amount_in_currency(self, amount, currency):
        if currency == '978':
            return str((amount * 100).to_integral())
        else:
            return str(amount.to_integral())


    def _to_currency_num_code(self, currency):
        try:
            int(currency)
            return str(currency)
        except ValueError:
            if currency.lower() == "eur":
                return '978'

    def _get_payment_params(self, charge):
        params = {'vads_site_id': charge.site_id(),
                  'vads_amount': self._amount_in_currency(charge.amount, self._to_currency_num_code(charge.currency)),
                  'vads_currency': self._to_currency_num_code(charge.currency),
                  'vads_ctx_mode': 'TEST',
                  'vads_page_action': 'PAYMENT',
                  'vads_action_mode': 'INTERACTIVE',
                  'vads_payment_config': 'SINGLE',
                  'vads_version': 'V2',
                  'vads_trans_date': charge.trans_date,
                  'vads_trans_id': charge.trans_id,
        }

        return params

    def _get_silent_payment_params(self, charge):
        params = self._get_payment_params(charge)

        #Added silent payment params
        silent_params = {'vads_action_mode': 'SILENT',
                         'vads_payment_cards': charge.used_instruments[0].method,
                         'vads_card_number': charge.used_instruments[0].card_number,
                         'vads_expiry_month': str(charge.used_instruments[0].exp_month),
                         'vads_expiry_year': str(charge.used_instruments[0].exp_year),
                         'vads_cvv': str(charge.used_instruments[0].cvv)
        }

        params.update(silent_params)
        return params
