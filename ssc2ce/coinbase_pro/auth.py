import base64
import hashlib
import hmac
import time


def make_auth_params(key,
                     secret,
                     passphrase,
                     request_method: str,
                     request_path_url: str,
                     request_body: str):

    timestamp = str(int(time.time()))
    message = timestamp + request_method + request_path_url
    if request_body:
        message += request_body

    hmac_key = base64.b64decode(secret)
    message = message.encode('utf-8')
    signature = hmac.new(hmac_key, message, hashlib.sha256)
    signature_b64 = base64.b64encode(signature.digest())

    return dict(key=key,
                passphrase=passphrase,
                timestamp=timestamp,
                signature=signature_b64)


def make_auth_header(key,
                     secret,
                     passphrase,
                     request_method: str,
                     request_path_url: str,
                     request_body: str):

    auth_params = make_auth_params(key=key,
                                   secret=secret,
                                   passphrase=passphrase,
                                   request_method=request_method,
                                   request_path_url=request_path_url,
                                   request_body=request_body)

    return {
        'Content-Type': 'application/json',
        'CB-ACCESS-SIGN': auth_params['signature'].decode('ascii'),
        'CB-ACCESS-TIMESTAMP': auth_params['timestamp'],
        'CB-ACCESS-KEY': auth_params['key'],
        'CB-ACCESS-PASSPHRASE': auth_params['passphrase'],
    }
