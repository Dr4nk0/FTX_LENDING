import time
import datetime
import json
import hmac
import requests
import urllib.parse
from operator import itemgetter
from requests import Request, Session, Response
from typing import Optional, Dict, Any, List

# Function creation (GET, POST, DELETE, REQUEST and RESPONSE)
class FtxClient:
    _ENDPOINT = 'https://ftx.com/api/' #FTX API Endpoint

    def __init__(self) -> None:
        self._session = Session()
        self._api_key = '' #API-KEY
        self._api_secret = '' #API-SECRET
        self._subaccount_name = '' #Subaccount-name

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
        if prepared.body:
            signature_payload += prepared.body
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

    def get_current_lending_offers(self) -> List[dict]: 
        return self._get(f'spot_margin/offers')
    
    def get_account_balance(self) -> List[dict]:
        return self._get(f'wallet/balances')

    def post_lending_offer(self, coin: str, size: float, rate: float) -> dict:
        return self._post('spot_margin/offers',{'coin': coin,'size': size,'rate': rate})

#Convert calls functions
    def request_quote(self, fromCoin: str, toCoin: str, size: float) -> dict:
        return self._post('otc/quotes',{'fromCoin': fromCoin,'toCoin': toCoin,'size': size})
    
    #Get quote status
    def quote_status(self, quoteId: int) -> dict:
        return self._get(f'otc/quotes/{quoteId}')

    #Accept quote
    def quote_accept(self, quoteId: int) -> dict:
        return self._post(f'otc/quotes/{quoteId}/accept')

#PROGRAM STARTING HERE
print ("\nProgram starting...\n")
main = FtxClient()

StableCoins = ['USD', 'USDT', 'DAI', 'EUR', 'AUD', 'CAD']
Stablecoins_wallet = []
default_lending_rate = 0

def clean_balance_wallet(balance):
    for coin in balance:
        if coin['coin'] in StableCoins :
            current_coin = coin['coin']
            del coin['usdValue']
            del coin['spotBorrow']
            del coin['total']
            del coin['free']
            Stablecoins_wallet.append({current_coin:coin})

def convert_coin(fromCoin,toCoin,size):
    request_quoteID = main.request_quote(fromCoin, toCoin, size)
    quoteID = request_quoteID['quoteId']
    send_quote_accept = main.quote_accept(quoteID)

wallet_balance = main.get_account_balance()
clean_balance_wallet(wallet_balance)

def extract_wallet_balances(wallet) :
    for coins in wallet :
        for key, value in coins.items() :
            if value['availableWithoutBorrow'] > 1 :
                new_coin_liquidity_size = value['availableWithoutBorrow']
                new_coin_liquidity_name = key
    return (new_coin_liquidity_size, new_coin_liquidity_name)

balances = extract_wallet_balances(Stablecoins_wallet)
print ("You want to add about {0} of {1}\n".format(balances[0], balances[1]))

current_offer = main.get_current_lending_offers()

for offers in current_offer :
    if offers['size'] > 1 :
        best_coin = offers['coin']
        current_liquidity = offers['size']
        break

print ("You are currently lending {0} of {1}\n".format(current_liquidity, best_coin))

def clean_offer(current_size, new_size, coin, rate) :
    added_liquidity = current_size + new_size
    main.post_lending_offer(coin=coin, size=added_liquidity, rate=rate)
    print("The final lending offer is now about {0} of {1}\n".format(added_liquidity,coin))

if balances[1] != best_coin :
    print ("We have to convert your {0} into {1}\n".format(balances[1], best_coin))
    convert_coin(fromCoin=balances[1], toCoin=best_coin, size=balances[0])
    wallet_balance = main.get_account_balance()
    clean_balance_wallet(wallet_balance)
    balances = extract_wallet_balances(Stablecoins_wallet)
    clean_offer(current_size=current_liquidity, new_size=balances[0], coin=best_coin, rate=default_lending_rate)
else :
    clean_offer(current_size=current_liquidity, new_size=balances[0], coin=best_coin, rate=default_lending_rate)

print ("Program ending...\n")
