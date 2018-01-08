from functions import *
from functions_ml import *
from bittrex.bittrex import *
from config import api_key, api_secret, dbcall

bit = Bittrex(api_key, api_secret)


while True:
    #top = getmovers()
    print(get_orderbook('BTC-ETH'))
    #for item in top:
        #if item[1] > 3:
            #string = 'mover, moving %s percent'%(item[1])
            #send_notification(item[0], string)
            #print(item)








if __name__ == "__main__":
    app.run()
