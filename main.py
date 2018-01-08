from functions import *
from functions_ml import *
from bittrex.bittrex import *
from config import api_key, api_secret, dbcall

bit = Bittrex(api_key, api_secret)
while True:
    print(getratios())


while False:
    top = getmovers(15)
    print(top)
    #result = get_orderbook('BTCETH')

    #print(result['df_buy_desc'])
    column_headers = ['coin','buy ratio','sell ratio']
    ratio_list = pd.DataFrame(columns=column_headers)
    for item in top:
        if item[1] >= 1:
            orders = get_orderbook(item[0])
            totalbuys = orders['df_buy_orderbook']['total']
            totalbuys = sum(totalbuys)
            totalsells = orders['df_sell_orderbook']['total']
            totalsells = sum(totalsells)
            ratio = makeratios(totalbuys,totalsells)
            ratio_list = ratio_list.append({'coin':item[0],'buy ratio':ratio['ratiobuy'],'sell ratio':ratio['ratiosell']}, ignore_index=True)
    print(ratio_list)
if __name__ == "__main__":
    app.run()
