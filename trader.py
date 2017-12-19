from functions import *
from functions_ml import *
from bittrex.bittrex import *
from config import api_key, api_secret, dbcall
#print(update_price_coin("BTC-ETH"))


bit = Bittrex(api_key, api_secret)

#print(get_coin_data("BTC-LTC"))
#print(custom_term_linear("BTC-LTC",1,1))

coin = 'ETH'
market = 'BTC-ETH'

#Get base coin balance
balance = bit.get_balance(coin)
balance_cur = balance['result']['Available']
print('Account balance: ', balance_cur)

#Get tradable amount per trade (10% of balance)
trade_amount = balance_cur*0.10
print('Trade amount: ', trade_amount)


#Get current price
#update = update_price_coin(market)
current_price = get_coin_data(market)
current_ask = current_price['ask']
print('Current ask: ', current_ask[0])

#get prediction
pred = custom_term_linear_market(market,1,1)
#print(pred)

order_book = bit.get_orderbook('BTC-ETH',BUY_ORDERBOOK)



result = get_orderbook()
avg = sum(result['price'])#/len(result.df_buy_orderbook['price'])
print(avg)


'''
orders = bit.get_open_orders(market)
print(orders)

print(update_price_coin(market))
current_price = get_coin_data(market)
print(custom_term_linear(market,1,1))
print(current_price)
'''
