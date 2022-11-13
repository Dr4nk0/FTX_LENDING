import time
import hmac
import urllib.parse
from requests import Request, Session, Response
from typing import Optional, Dict, Any, List
from decouple import config

#Credentials initiation
api_key = config('NyNzC1P9UYAm8Lbaz8PViEHnHhCcN2_ri9Hh_yZ')
api_secret = config('wgFhr7TofH3UU×MDztnS9h1zgRj5z6bEKiQZBAHK')
subaccount_name = config('SPOT')

# Function creation (GET, POST, DELETE, REQUEST and RESPONSE)

class FtxClient:
    _ENDPOINT = 'https://ftx.com/api/' #FTX API Endpoint

    def __init__(self) -> None:
        self._session = Session()
        self._api_key = api_key
        self._api_secret = api_secret
        self._subaccount_name = subaccount_name

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('GET', path, params=params)

    def _post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('POST', path, json=params)

    def _delete(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('DELETE', path, json=params)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self._ENDPOINT + path, **kwargs)
        self._sign_request(request)
        response = self._session.send(request.prepare())
        return self._process_response(response)

    def _sign_request(self, request: Request) -> None:
        ts = int(time.time() * 1000)
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
        print("\n#####################################################")
        print("La requête APi est :", signature_payload)
        print("#####################################################\n")
        if prepared.body:
            signature_payload += prepared.body
            print("\n#####################################################")
            print("La requête APi est :", signature_payload)
            print("#####################################################\n")
        signature = hmac.new(self._api_secret.encode(), signature_payload, 'sha256').hexdigest()
        request.headers['FTX-KEY'] = self._api_key
        request.headers['FTX-SIGN'] = signature
        request.headers['FTX-TS'] = str(ts)
        if self._subaccount_name:
            request.headers['FTX-SUBACCOUNT'] = urllib.parse.quote(self._subaccount_name)

    def _process_response(self, response: Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if not data['success']:
                raise Exception(data['error'])
            return data['result']

#API GET Global functions

    #Get wallet balances for each coins
    def account_balance(self) -> List[dict]:
        return self._get(f'wallet/balances')

###############################################################

main = FtxClient()

result = main.account_balance()
print (result)


