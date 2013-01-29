from google.appengine.ext import webapp
import json
import base64
import hashlib
import hmac
import logging


class MainPage(webapp.RequestHandler):
    
    
    def get(self):
        signed_request = self.request.get('signed_request')
        data = parse_signed_request(signed_request, 'abcdef')
        logging.warning(data)
        self.response.headers['Content-Type'] = 'application/json'
        
        response_data = {'method': 'unknown'}
        if data['method'] == 'payments_get_items':
            response_data = {'method': 'payments_get_items',
                             'content': [
                              {'title': 'Title of order',
                               'description': 'Description of order',
                               'price': '200',
                               'image_url': 'http://aux.iconpedia.net/uploads/1505202069.png'
                               }
                              ]}
        elif data['method'] == 'payments_status_update':
            response_data = {'method': 'payments_status_update',
                             'content': {'order_id': data['order_id'],
                                         'status': 'settled'}
                             }
        self.response.out.write(json.dumps(response_data))

    def post(self):
        self.get()
 
def base64_url_decode(inp):
    padding_factor = (4 - len(inp) % 4) % 4
    inp += "="*padding_factor 
    return base64.b64decode(unicode(inp).translate(dict(zip(map(ord, u'-_'), u'+/'))))
 
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


app = webapp.WSGIApplication([('/api/', MainPage)], debug=True)

