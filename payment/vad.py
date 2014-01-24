import hashlib
import json

import urllib3
from suds.client import Client
from datetime import datetime


SERVER_URL = 'https://payzen.lyra-labs.fr/'
PAYMENT_URL = SERVER_URL + 'vads-payment/'
ORDER_URL = PAYMENT_URL + 'service/order?cacheId='
WS_URL = SERVER_URL + 'vads-ws/v4?wsdl'
TEST_STR = 'TEST'


class PaymentFormManager:
    def submit_payment_form(self, charge):
        params = {'vads_site_id': charge.site_id(),
                  'vads_amount': self.__amount_in_currency(charge.amount, self.__to_currency_num_code(charge.currency)),
                  'vads_currency': self.__to_currency_num_code(charge.currency),
                  'vads_ctx_mode': 'TEST',
                  'vads_page_action': 'PAYMENT',
                  'vads_action_mode': 'INTERACTIVE',
                  'vads_payment_config': 'SINGLE',
                  'vads_version': 'V2',
                  'vads_trans_date': charge.trans_date,
                  'vads_trans_id': charge.trans_id,
        }

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
            jsonconent = json.loads(str(response.data), 'UTF-8')
            return jsonconent
        except ValueError:
            pass

    def __amount_in_currency(self, amount, currency):
        if currency == '978':
            return str((amount * 100).to_integral())
        else:
            return str(amount.to_integral())

    def __to_currency_num_code(self, currency):
        try:
            int(currency)
            return str(currency)
        except ValueError:
            if currency.lower() == "eur":
                return '978'