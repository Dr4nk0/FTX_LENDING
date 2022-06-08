import time
import datetime
import json
import hmac
import requests
import urllib.parse
from operator import itemgetter
from heapq import nlargest
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

#API GET lending calls functions

    #Get global lending history
    def lending_history(self, start_time = str, end_time  = str, coin = str) -> List[dict]:
        return self._get(f'spot_margin/history',
                                    {'start_time' : start_time,
                                    'end_time' : end_time,
                                    'coin' : coin
                                    })

    #Get my lending history
    def my_lending_history(self, start_time = str, end_time  = str) -> List[dict]: 
        return self._get(f'spot_margin/lending_history',
                                    {'start_time' : start_time,
                                    'end_time' : end_time
                                    })
    
    #Get the global previous and next lending rates for every coins available
    def lending_rates(self) -> List[dict]: 
        return self._get(f'spot_margin/lending_rates')
    
    #Get my coins currently lended or locked for 1h and the size which occure and the rate i'm asking for (0 : best)
    def lending_offers(self) -> List[dict]: 
        return self._get(f'spot_margin/offers')
    
    #Give locked size, lendable amount, offered amount and min rate asked for every coin in my wallet compatible with lending 
    def lending_info(self) -> List[dict]: 
        return self._get(f'spot_margin/lending_info')

#API GET Global functions

    #Get wallet balances for each coins
    def account_balance(self) -> List[dict]:
        return self._get(f'wallet/balances')

#API GET & POST convert calls functions

    #Request a convert quote from x coin to y coin with k size
    def request_quote(self, fromCoin: str, toCoin: str, size: float) -> dict:
        return self._post('otc/quotes', 
                                    {'fromCoin': fromCoin,
                                     'toCoin': toCoin,
                                     'size': size
                                     })
    
    #Get quote status
    def quote_status(self, quoteId: int) -> dict:
        return self._get(f'otc/quotes/{quoteId}')

    #Accept quote
    def quote_accept(self, quoteId: int) -> dict:
        return self._post(f'otc/quotes/{quoteId}/accept')

#API POST call functions

    #Submit lending offer full or empty
    def lending_offer(self, coin: str, size: float, rate: float) -> dict:
        return self._post('spot_margin/offers', 
                                    {'coin': coin,
                                     'size': size,
                                     'rate': rate
                                     })
    
    #Submit lending cancellation
    def lending_stop(self, coin: str, rate: float, size: float) -> dict:
        return self._post('spot_margin/offers', 
                                    {'coin': coin,
                                     'rate': rate,
                                     'size': size
                                     })

#program starting
ct = datetime.datetime.now()
ts = ct.timestamp()
current_time = datetime.datetime.now()
logs = open("risky_logs.txt", "a")
logs.write("---------------Programm started-------------------------\n")
logs.write("\n")
logs.write("Current date is : {0}\n".format(current_time))
logs.write("\n")

main = FtxClient()
default_lending_rate = 0
new_stop_cap = 0

#Create list of all lendable coins
Coins_list = []
result = main.lending_rates()
for coin in result :
    Coins_list.append(coin['coin'])

#Get last 24h lending rates for each Stablecoins
start_time = ts - 86400 #aujourd'hui - 24h 
end_time = ts #aujourd'hui
Stablecoins_past_rates = {}
for coin in Coins_list:
    past_lending_R = main.lending_history(start_time, end_time, coin)
    moyenne = (sum(d['rate'] for d in past_lending_R) / len(past_lending_R))*365*24*100
    moyenne = round(moyenne,2)
    Stablecoins_past_rates[past_lending_R[0]['coin']] = moyenne #List contenant chaque coin et sa moyenne de lend sur les dernières 24h
res = nlargest(10, Stablecoins_past_rates, key = Stablecoins_past_rates.get) #list contenant le top 10 des coins sur 24h

Coins_list_predicted = {}
result = main.lending_rates()
for coin in result :
    if coin['coin'] in res :
        estimate = coin['estimate']
        winner = coin['coin']
        Coins_list_predicted[winner]=estimate

res = nlargest(3, Coins_list_predicted, key = Coins_list_predicted.get) #list contenant le top 3 des predicted coins sur 24h
print ("Top 3 is : " + str(res))

def waiting_function(locked_size : float, coin : str) :
    while locked_size > 0.0 :
        time.sleep(60)
        actual_offering = main.lending_info()
        for offers in actual_offering :
            if offers['coin'] == coin :
                locked_size = offers['locked']

#Get the current lended coin and size and stop
actual_offering = main.lending_info()
for offers in actual_offering :
    if offers['offered'] >= offers['locked'] :
        main.lending_stop(offers['coin'],default_lending_rate,new_stop_cap)

for offers in actual_offering:
    if offers['locked'] >= offers['offered'] :
        waiting_function(offers['locked'], offers['coin'])

time.sleep(3)

#Get balance
whole_balance = main.account_balance()
for coin in whole_balance :
    if coin['coin'] != 'USDT' and coin['availableWithoutBorrow'] >= 0 and coin['usdValue'] >= 1 :
        request_quoteID = main.request_quote(coin['coin'], 'USDT', coin['availableWithoutBorrow'])
        send_quote_accept = main.quote_accept(request_quoteID['quoteId'])
        time.sleep(3)
    elif coin['coin'] == 'USDT' and coin['availableWithoutBorrow'] >= 0 :
        available_amount = coin['availableWithoutBorrow']

T1 = 0.39 * available_amount
T2 = 0.29 * available_amount
T3 = 0.29 * available_amount

request_quoteID = main.request_quote('USDT', res[0], T1)
send_quote_accept = main.quote_accept(request_quoteID['quoteId'])
whole_balance = main.account_balance()
for coin in whole_balance :
    if coin['coin'] == res[0] :
        amount = coin['availableWithoutBorrow']
main.lending_offer(res[0],amount,default_lending_rate)

time.sleep(3)

request_quoteID = main.request_quote('USDT', res[1], T2)
send_quote_accept = main.quote_accept(request_quoteID['quoteId'])
whole_balance = main.account_balance()
for coin in whole_balance :
    if coin['coin'] == res[1] :
        amount = coin['availableWithoutBorrow']
main.lending_offer(res[1],amount,default_lending_rate)

time.sleep(3)

request_quoteID = main.request_quote('USDT', res[2], T3)
send_quote_accept = main.quote_accept(request_quoteID['quoteId'])
whole_balance = main.account_balance()
for coin in whole_balance :
    if coin['coin'] == res[2] :
        amount = coin['availableWithoutBorrow']
main.lending_offer(res[2],amount,default_lending_rate)










