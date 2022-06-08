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
logs = open("logs.txt", "a")
logs.write("---------------Programm started-------------------------\n")
logs.write("\n")
logs.write("Current date is : {0}\n".format(current_time))
logs.write("\n")

main = FtxClient()

StableCoins = ['USD', 'USDT', 'DAI', 'EUR', 'AUD', 'CAD']
StableCoins_price = []
Stablecoins_wallet = []
Stablecoins_wallet_simple = []
Stablecoins_lending_amount = []
Stablecoins_current_rates = []
Stablecoins_past_rates = {}
default_lending_rate = 0
new_stop_cap = 0

def still_locked_updated(locked_size : float, coin : str) :
    while locked_size > 0.0 :
        time.sleep(60)
        actual_offering = main.lending_info()
        for offers in actual_offering :
            if offers['coin'] == best_rate :
                locked_size = offers['locked']
    logs.write("We had to wait for {0} min in order to get your {1} free\n".format(n,coin))
    return (1)

def check_lending_amount (Stablecoins_lending_amount : List) :
    taille = len(Stablecoins_lending_amount)
    c = 0
    for check in Stablecoins_lending_amount :
        for key, values in check.items() :
            if values['locked'] == 0.0 and values['offered'] == 0.0 :
                c = c + 1
            else :
                print (key, "Is not empty")
    return (taille,c)

def get_key(val):
    for where in Stablecoins_wallet_simple :
        for key, value in where.items():
            if val == value:
                return key

def balance_wallet(balance):
    for coin in balance:
        if coin['coin'] in StableCoins :
            current_coin = coin['coin']
            del coin['usdValue']
            del coin['spotBorrow']
            del coin['coin']
            del coin['total']
            del coin['free']
            Stablecoins_wallet.append({current_coin:coin})

#Get last 24h lending rates for each Stablecoins
start_time = ts - 86400 #aujourd'hui - 24h 
end_time = ts #aujourd'hui

for coin in StableCoins:
    past_lending_R = main.lending_history(start_time, end_time, coin)
    moyenne = (sum(d['rate'] for d in past_lending_R) / len(past_lending_R))*365*24*100
    moyenne = round(moyenne,2)
    Stablecoins_past_rates[past_lending_R[0]['coin']] = moyenne
    
logs.write("The last 24H rate average for choosen coins are : " + repr(Stablecoins_past_rates) + "\n")
logs.write("\n")
best_rate = max(Stablecoins_past_rates, key = Stablecoins_past_rates.get)
top_percent = Stablecoins_past_rates.get(best_rate)
logs.write("The best average rate coin is {0} with {1}%\n".format(best_rate,top_percent))
logs.write("\n")

#Get the current lended coin and size
actual_offering = main.lending_info()

for offers in actual_offering :
    if offers['coin'] == best_rate and offers['offered'] > 0 and offers['locked'] > 0 :
        locked_size = offers['locked']
        currently_lended_coin = offers['coin']
        logs.write("The best YRL coin ({0}) is already lended with ({1} units), there is nothing more to do.\n".format(currently_lended_coin,locked_size))
        logs.write("\n")
        logs.write("\n--------------Program ended--------------------\n")
        exit()
    elif offers['coin'] in StableCoins and offers['locked'] > offers['offered'] :
        locked_size = offers['locked']
        currently_lended_coin = offers['coin']
        logs.write("{0} of your {1} are currently being unlended so we have to send request to waiting process...\n".format(locked_size,currently_lended_coin))
        logs.write("\n")
        result = still_locked_updated(locked_size, currently_lended_coin)
    elif offers['coin'] in StableCoins and offers['offered'] == 0.0 and offers['locked'] == 0.0 :
        current_coin = offers['coin']
        del offers['coin']
        del offers['minRate']
        del offers['lendable']
        Stablecoins_lending_amount.append({current_coin:offers})
        check = check_lending_amount(Stablecoins_lending_amount)
    elif offers['coin'] != best_rate and offers['offered'] > 0 or offers['locked'] > 0 :
        currently_lended_coin = offers['coin']
        currently_lended_cap = offers['offered']
        currently_locked_cap = offers['locked']
        logs.write("\nThe Current lended coin is {0}, the offered size is : {1} and locked size is {2}\n".format(currently_lended_coin,currently_lended_cap,currently_locked_cap))
        logs.write("\n")
        main.lending_stop(currently_lended_coin,default_lending_rate,new_stop_cap)
        new_offer = main.lending_info()
        for offers in new_offer :
            if offers['coin'] == currently_lended_coin :
                locked_size = offers['locked']
                coin = currently_lended_coin
                old_locked = locked_size
                result = still_locked_updated(locked_size, coin)
                if result == 1 :
                    logs.write("\n")
                    fromCoin = currently_lended_coin
                    toCoin = best_rate
                    size = currently_lended_cap
                    request_quoteID = main.request_quote(fromCoin, toCoin, size)
                    quoteID = request_quoteID['quoteId']
                    send_quote_accept = main.quote_accept(quoteID)
                    if request_quoteID :
                        fees = send_quote_accept['fill']['fee']
                        convert_size = send_quote_accept['fill']['size']
                        convert_price = send_quote_accept['fill']['price']
                        final_wallet = convert_size * convert_price
                        logs.write("We converted with {0} fees about {1} of {2} to {3} of {4} at a price of {5}\n".format(fees,size,fromCoin,final_wallet,toCoin,convert_price))
                        logs.write("\n")
                        new_lending_offer = main.lending_offer(toCoin,final_wallet,default_lending_rate)
                        logs.write("You just have created a new lending offer of {0} {1}\n".format(final_wallet,toCoin))
                        logs.write("\n--------------Program ended--------------------\n")
                    else :
                        logs.write("Something went wrong with the convert function")
                        exit()
                else :
                    logs.write("Something wend wrong, quitting...\n")
                    exit()

#Get balance for each Stablecoins
balance = main.account_balance()
balance_wallet(balance)

if check[1] == check[0] or result == 1 :
    i = 0
    for getting in Stablecoins_wallet :
        i = i+1
        for key, value in getting.items() :
            coin = key
            amount = value['availableWithoutBorrow']
            Stablecoins_wallet_simple.append({coin:amount})
            StableCoins_price.append(amount)
    coin_number = i
    #if sum(StableCoins_price) != coin_A or coin_B or coin_C :
    #convert
    #maybe
    max_amount = max(StableCoins_price)
    max_coin = get_key(max_amount)
    if max_coin == best_rate :
        new_lending_offer = main.lending_offer(max_coin,max_amount,default_lending_rate)
        logs.write("You just have created a new lending offer of {0} {1}\n".format(max_amount,max_coin))
        logs.write("\n--------------Program ended--------------------\n")
    else :
        fromCoin = max_coin
        toCoin = best_rate
        size = max_amount
        request_quoteID = main.request_quote(fromCoin, toCoin, size)
        quoteID = request_quoteID['quoteId']
        send_quote_accept = main.quote_accept(quoteID)
        if request_quoteID :
            fees = send_quote_accept['fill']['fee']
            convert_size = send_quote_accept['fill']['size']
            convert_price = send_quote_accept['fill']['price']
            final_wallet = convert_size * convert_price
            logs.write("We converted with {0} fees about {1} of {2} to {3} of {4} at a price of {5}\n".format(fees,size,fromCoin,final_wallet,toCoin,convert_price))
            logs.write("\n")
            new_lending_offer = main.lending_offer(toCoin,final_wallet,default_lending_rate)
            logs.write("You just have created a new lending offer of {0} {1}\n".format(final_wallet,toCoin))
            logs.write("\n--------------Program ended--------------------\n")
        else :
            logs.write("Something went wrong with the convert function")
            exit()
elif  check[1] < check[0] :
    print ("Ya une couille")
    exit()
logs.close()
