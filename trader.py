from functions import *
from functions_ml import *
from bittrex.bittrex import *
from config import api_key, api_secret, dbcall
#print(update_price_coin("BTC-ETH"))


bit = Bittrex(api_key, api_secret)

#print(get_coin_data("BTC-LTC"))
#print(custom_term_linear("BTC-LTC",1,1))
while True:
    print(update_prices())
    time.sleep(240)


if __name__ == "__main__":
    app.run()
