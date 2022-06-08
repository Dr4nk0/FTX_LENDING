# FTX_LENDING
### Still in development so don't open new issues please
Automated selection of best rate StableCoins to lend at the time.

I recommend that you run the script periodically (e.g. every Tuesday at 00:00), you can use cron-tab for that.

You can use the docker container which is doing everything for you : https://hub.docker.com/r/dr4nk0/ftx_lending_automate

## How to use

### Parameters
1) Get your API KEY and SECRET within https://ftx.com/profile
2) Inside main.py replace 'API-KEY' and 'API-SECRET' variable content by your API informations
3) If you are using subaccounts, insert your subacount name inside 'SUBACCOUNT-NAME' variable
4) Drop your coins to the subbacount wallet

### Choose your coins
Currently, the script is using list of StableCoins (USD, USDT, DAI, EUR, AUD, CAD), they have been choosed bescause of their stability in the past months, years.
This selection allow you to minimize the volatility exposition proper to CryptoCurrencies.

If you want to expose your allowed ressources to volatility, you can choose to use differents coin.

To do so, sepcify your currencies inside the variable like this : StableCoins = ['XVG', 'COPE', 'BTC']

You can find the list of coins available for lending here : https://ftx.com/spot-margin/lending


## How the script choose the best rates ?

Based on the work of @RobinZekerNiet at https://ftxpremiums.com/ i managed to find out that StableCoins are often the best stable rates on a large period.

In fact, on the top 10 of best average annualized lending rates we can found :
- USD : 21.44% average rate on all-time period
- DAI : 21,18% average rate on all-time period
- USDT : 20.90% average rate on all-time period

I made a simmulation with 10k$ as base capital, you can see the interest owned after periods of time for each average annualized lending rate : https://drive.google.com/file/d/1psMV9sVOf8vVBZOvgp9az10075df7Kqo/view?usp=sharing

Basicaly, when started, the script will get the last 24H average lending rate of the choosen coins and convert your capital into the winner and lend it all.

Beacuse Mondays are often higky volatile days, i recommand you to start the script on Thuesday night so he can process with stable volatility day.

## Diclaimer
This script in any case can be consider as financial adviser. It only allow you to get the best lending rate available on FTX based on maths calculs.
I'm not responsible in any case of money loss. When dealing with speculatif assets, only invest ressources you can afford to loose even if the risk is higly reduced.
