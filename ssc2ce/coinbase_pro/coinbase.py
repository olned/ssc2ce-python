from ssc2ce.coinbase_pro.auth import make_auth_params
from ssc2ce.common.session import SessionWrapper
from aiohttp import ClientResponseError


class Coinbase(SessionWrapper):
    """
    Handlers:
     - on_connect_ws - Called after the connection is established.
            If auth_type is not equivalent to AuthType.NONE,
            on_connect_ws will be set to self.auth_login;
     - on_close_ws - Called after disconnection, default value is None;
     - on_authenticated - Called after authentication is confirmed, default value is None;
     - on_token - Called after receiving a response to an authentication request, default value is None;
     - on_message - Called when a message is received, default value is self.handle_message;
     - on_handle_response - Called when the message from the exchange does not contain the request id;
     - on_response_error - Called when the response contains an error message.
    """

    def __init__(self,
                 auth_param: dict = None,
                 sandbox: bool = True):

        super().__init__()

        self.ws_api = "wss://ws-feed-public.sandbox.pro.coinbase.com" if sandbox \
            else "wss://ws-feed.pro.coinbase.com"

        self.rest_api = "https://api-public.sandbox.pro.coinbase.com" if sandbox \
            else "https://api.pro.coinbase.com"
        self.sandbox = sandbox
        self.auth_param = auth_param

    async def get_currencies(self):
        try:
            return await self.public_get("/currencies")
        except ClientResponseError as e:
            self.logger.error(e.message)
            return []

    async def get_products(self):
        try:
            return await self.public_get("/products")
        except ClientResponseError as e:
            self.logger.error(e.message)
            return []

    def _auth_headers(self, path, method, body=''):
        auth_params = make_auth_params(key=self.auth_param["api_key"],
                                       secret=self.auth_param["secret_key"],
                                       passphrase=self.auth_param["passphrase"],
                                       request_method=method,
                                       request_path_url=path,
                                       request_body=body)

        return {
            'Content-Type': 'application/json',
            'CB-ACCESS-SIGN': auth_params['signature'].decode('ascii'),
            'CB-ACCESS-TIMESTAMP': auth_params['timestamp'],
            'CB-ACCESS-KEY': auth_params['key'],
            'CB-ACCESS-PASSPHRASE': auth_params['passphrase'],
        }

    async def private_get(self, request_path):
        headers = self._auth_headers(path=request_path, method='GET', body='')

        async with self._session.get(self.rest_api + request_path, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                self.logger.error(self.rest_api + request_path)
                response.raise_for_status()
