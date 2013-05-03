from google.appengine.ext import webapp
import json
import base64
import hashlib
import hmac
import logging

payment_sharedsecret = 'abcdef'


class MainPage(webapp.RequestHandler):

    # Stores all the order ids as keys if indicated that the response for the
    # payment status update should be a failure.
    status_update_error_response_orders = {}

    def get(self):
        #decode and verify the signed_request.
        signed_request = self.request.get('signed_request')
        data = parse_signed_request(signed_request, payment_sharedsecret)

        logging.warning(data)
        self.response.headers['Content-Type'] = 'application/json'

        #TODO: implement actual storing of the orders. For the sake of example not really required.
        response_data = {'method': 'unknown'}
        if data['method'] == 'payments_get_items':
            price = 0
            if data['order_info'] == 'package-5-cents':
                price = 5
            if data['order_info'] == 'package-100-cents':
                price = 100
            if data['order_info'] == 'package-130-cents':
                price = 130
            if data['order_info'] == 'package-150-cents':
                price = 150
            if data['order_info'] == 'package-250-cents':
                price = 250
            if data['order_info'] == 'package-300-cents':
                price = 300
            if data['order_info'] == 'package-450-cents':
                price = 450
            if data['order_info'] == 'package-500-cents':
                price = 500
            if data['order_info'] == 'package-600-cents':
                price = 600
            if data['order_info'] == 'package-900-cents':
                price = 900
            if data['order_info'] == 'package-1000-cents':
                price = 1000
            if data['order_info'] == 'package-1500-cents':
                price = 1500
            if data['order_info'] == 'package-1990-cents':
                price = 1990
            if data['order_info'] == 'package-1999-cents':
                price = 1999
            if data['order_info'] == 'package-2500-cents':
                price = 2500
            if data['order_info'] == 'package-5-cents-fail-getitems':
                raise Exception("This call is meant to mess the getitems call.")
            if data['order_info'] == 'package-5-cents-fail-statusupdate':
                price = 5
                self.status_update_error_response_orders[data['order_id']] = True


            #response for 'payments_get_items'
            response_data = {'method': 'payments_get_items',
                             'content': [
                              {'title': 'Cheap purple cow',
                               'description': 'Not a normal cow! No this one is purple (and cheap).',
                               'price': str(price),
                               'image_url': 'http://www.slopemedia.org/wp-content/uploads/2012/10/1purple_cow.gif'
                               }
                             ]}
        elif data['method'] == 'payments_status_update':
            error_response = self.status_update_error_response_orders.get(data['order_id'], False)
            if error_response:
                del self.status_update_error_response_orders[data['order_id']]
                raise Exception("This call is meant to mess the payment status update call.")
            status = 'settled' if data['status'] == 'placed' else 'failed'
            #response for 'payments_status_update'
            response_data = {'method': 'payments_status_update',
                             'content': {'order_id': data['order_id'],
                                         'status': status}
                             }
        logging.warning(json.dumps(response_data))
        self.response.out.write(json.dumps(response_data))

    def post(self):
        self.get()

#util to base64 url decode
def base64_url_decode(inp):
    padding_factor = (4 - len(inp) % 4) % 4
    inp += "="*padding_factor
    return base64.b64decode(unicode(inp).translate(dict(zip(map(ord, u'-_'), u'+/'))))

#util to parse the signed_request and verify it.
def parse_signed_request(signed_request, secret):

    l = signed_request.split('.', 2)
    encoded_sig = l[0]
    payload = l[1]

    sig = base64_url_decode(encoded_sig)
    data = json.loads(base64_url_decode(payload))

    if data.get('algorithm').upper() != 'HMAC-SHA256':
        logging.error('Unknown algorithm')
        return None
    else:
        expected_sig = hmac.new(secret, msg=payload, digestmod=hashlib.sha256).digest()

    if sig != expected_sig:
        return None
    else:
        logging.debug('valid signed request received..')
        return data

#Payment-endpoint for this project: http://example-gameover-game.appspot.com/api/
app = webapp.WSGIApplication([('/api/', MainPage)], debug=True)
