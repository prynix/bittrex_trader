from functions import *
from functions_ml import *
from bittrex.bittrex import *
from config import api_key, api_secret, dbcall
from flask import *
import sys
import time
bit = Bittrex(api_key, api_secret)
app = Flask(__name__)

print(placeorder('BTC-XVG',50,0,'sell','S000000001'))
time.sleep(50)
#@app.route('/')
#def index():
while False:
    #return render_template('index.html')
    top = getmovers(15)
    #result = get_orderbook('BTCETH')

    #print(result['df_buy_desc'])
    column_headers = ['coin','buy ratio','sell ratio','move%']
    ratio_list = pd.DataFrame(columns=column_headers)
    for item in top:
        if item[1] >= 1:
            orders = get_orderbook(item[0])
            totalbuys = orders['df_buy_orderbook']['total']
            totalbuys = sum(totalbuys)
            totalsells = orders['df_sell_orderbook']['total']
            totalsells = sum(totalsells)
            ratio = makeratios(totalbuys,totalsells)
            ratio_list = ratio_list.append({'coin':item[0],'buy ratio':ratio['ratiobuy'],'sell ratio':ratio['ratiosell'],'move%':item[1]}, ignore_index=True)
    print(ratio_list)

    #Use this to pause loop for 100s
    print "waiting...\\",
    syms = ['\\', '|', '/', '-']
    bs = '\b'

    for _ in range(100):
        for sym in syms:
            sys.stdout.write("\b%s" % sym)
            sys.stdout.flush()
            time.sleep(.5)
if __name__ == "__main__":
    app.run(debug=True)
