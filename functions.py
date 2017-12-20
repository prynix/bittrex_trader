#This is designed to hold the bittrex api functions accessed by the trading folder
from bittrex import Bittrex
from config import api_key, api_secret, dbcall, access_token
from operator import itemgetter
import pandas as pd
import time
import datetime
import pypyodbc


#definitions
d = {}
top_10 = []
p = Bittrex(api_key, api_secret)
#tick = p.get_market_summaries()

#Database access
cnxn = pypyodbc.connect(dbcall)
cursor = cnxn.cursor()

def send_notification(title, body):
    data_send = {"type": "note", "title": title, "body": body}
    resp = rq.post('https://api.pushbullet.com/v2/pushes', data=json.dumps(data_send),
                         headers={'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'})
    if resp.status_code != 200:
        raise Exception('Something wrong')
    else:
        print('complete sending')


def get_orderbook():
	cnxn = pypyodbc.connect(dbcall)
	cursor = cnxn.cursor()
	order_book = p.get_market_history('BTC-ETH','BTC')
	order_book = order_book['result']
	rates = []
	quan = []
	buy_orderbook = []
	sell_orderbook = []
	for x in order_book:
		book_total = x['Total']
		book_time = x['TimeStamp']
		book_price = x['Price']
		book_quan = x['Quantity']
		book_type = x['OrderType']
		if x['OrderType'] == 'BUY':
			#buy_orderbook.append(tuple((('total',book_total),('time',book_time),('price',book_price),('quantity',book_quan))))
			buy_orderbook.append(tuple((book_total,book_time,book_price,book_quan)))
		if x['OrderType'] == 'SELL':
			#sell_orderbook.append(tuple((('total',book_total),('time',book_time),('price',book_price),('quantity',book_quan))))
			sell_orderbook.append(tuple((book_total,book_time,book_price,book_quan)))
		string = "INSERT INTO dbo.orderbook VALUES ('%s','%s', '%s', '%s', '%s')"%(book_total, book_time, book_price, book_quan, book_type)
		cursor.execute(string,)
		cnxn.commit()
	cnxn.close()
	column_headers = ['total','time','price','quantity']
	df_buy_orderbook = pd.DataFrame(list(buy_orderbook),columns=column_headers)
	df_sell_orderbook = pd.DataFrame(list(sell_orderbook),columns=column_headers)
	return df_buy_orderbook#, df_sell_orderbook



def update_prices():
	cnxn = pypyodbc.connect(dbcall)
	cursor = cnxn.cursor()
	tick = p.get_market_summaries()
	tick = tick['result']
	#print(tick)
	print("hello from the other side")
	for x in tick:
		y = x['MarketName']
		y = y.replace('-','')
		volume = str(x['Volume'])
		last = float(x['Last'])
		bid = float(x['Bid'])
		ask = float(x['Ask'])
		openbuyorders = str(x['OpenBuyOrders'])
		opensellorders = str(x['OpenSellOrders'])
		last = '{:.8f}'.format(last)
		bid = '{:.8f}'.format(bid)
		ask = '{:.8f}'.format(ask)
		collection = "SELECT TOP(1) bid FROM dbo.%s ORDER BY date DESC"%(y)
		latest_row = pd.DataFrame(list(cursor.execute(collection)))
		old = float(latest_row[0])
		old = '{:.8f}'.format(old)
		change = ((float(bid)/float(old))-1)*100
		date = time.strftime('%Y-%m-%d %H:%M:%S')
		#Inital table creation script
		#string = "CREATE TABLE %s(currency varchar(10), last decimal(16,8), bid decimal(16,8), ask decimal(16,8), volume decimal(20,8), openbuyorders decimal(16,8), opensellorders  decimal(16,8), change decimal(16,8), date datetime);"%(y)
		string = "INSERT INTO dbo.%s VALUES ('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"%(y, y, last, bid, ask, volume, openbuyorders, opensellorders, change, date)
		#print(string)
		cursor.execute(string,)
		cnxn.commit()
	cnxn.close()
	return ("Archived at: ", time.asctime(time.localtime(time.time())))

def update_price_coin(coin):
	cnxn = pypyodbc.connect(dbcall)
	cursor = cnxn.cursor()
	tick = p.get_market_summaries()
	tick = tick['result']
	for x in tick:
		if x['MarketName'] == coin:
			y = x['MarketName']
			y = y.replace('-','')
			y = str(y)
			volume = float(x['Volume'])
			last = float(x['Last'])
			bid = float(x['Bid'])
			ask = float(x['Ask'])
			openbuyorders = float(x['OpenBuyOrders'])
			opensellorders = float(x['OpenSellOrders'])
			volume = '{:.8f}'.format(volume)
			last = '{:.8f}'.format(last)
			bid = '{:.8f}'.format(bid)
			ask = '{:.8f}'.format(ask)
			openbuyorders = '{:.8f}'.format(openbuyorders)
			opensellorders = '{:.8f}'.format(opensellorders)
			collection = "SELECT TOP(1) bid FROM dbo.%s ORDER BY date DESC"%(y)
			latest_row = pd.DataFrame(list(cursor.execute(collection)))
			old = float(latest_row[0])
			old = '{:.8f}'.format(old)
			change = ((float(bid)/float(old))-1)*100
			date = time.strftime('%Y-%m-%d %H:%M:%S')
			string = "INSERT INTO dbo.%s VALUES ('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"%(y, y, last, bid, ask, volume, openbuyorders, opensellorders, change, date)
			cursor.execute(string,)
			cnxn.commit()
	cnxn.close()
	return ("Added %s"%(coin))

def get_coin_data(coin):
	cnxn = pypyodbc.connect(dbcall)
	cursor = cnxn.cursor()
	coin = coin.replace('-','')
	column_headers = ['currency','last','bid','ask','volume','openbuyorders','opensellorders','change','date']
	collection = "SELECT TOP(1) * FROM dbo.%s ORDER BY date DESC"%(coin)
	latest_row = pd.DataFrame(list(cursor.execute(collection)),columns=column_headers)
	latest_row['change'] = '{:.10f}'.format(float(latest_row['change']))
	cnxn.commit()
	return latest_row



def get_top10(interval):
	cnxn = pypyodbc.connect(dbcall)
	cursor = cnxn.cursor()
	collection = "SELECT * FROM sys.Tables"
	latest_row = pd.DataFrame(list(cursor.execute(collection)))
	latest_row = latest_row[0]
	top_10 = []
	if interval % 1 <> 0:
		return ("Please enter in whole days or enter '0' to get all")
	if interval % 1 == 0 & interval <> 0:
		for w in latest_row:
			if w != "":
				collection = "SELECT TOP(1) bid FROM dbo.%s WHERE date > GETDATE()-%s ORDER BY date DESC"%(w, interval)
				change = pd.DataFrame(list(cursor.execute(collection)))
				change = float(change[0])
				top_10.append(tuple((w,change)))
		top_10.sort(key=itemgetter(1), reverse=True)
		top_10 = top_10[:10]
		cnxn.commit()
	if interval == 0:
		for w in latest_row:
			if w != "":
				collection = "SELECT TOP(1) bid FROM dbo.%s ORDER BY date DESC"%(w)
				change = pd.DataFrame(list(cursor.execute(collection)))
				change = float(change[0])
				top_10.append(tuple((w,change)))
		top_10.sort(key=itemgetter(1), reverse=True)
		top_10 = top_10[:10]
		cnxn.commit()
	cnxn.close()
	return top_10


def get_bottom10(interval):
	cnxn = pypyodbc.connect(dbcall)
	cursor = cnxn.cursor()
	collection = "SELECT * FROM sys.Tables"
	latest_row = pd.DataFrame(list(cursor.execute(collection)))
	latest_row = latest_row[0]
	bottom_10 = []
	if interval % 1 <> 0:
		return ("Please enter in whole days or enter '0' to get all")
	if interval % 1 == 0 & interval <> 0:
		for w in latest_row:
			if w != "":
				collection = "SELECT TOP(1) bid FROM dbo.%s WHERE date > GETDATE()-%s ORDER BY date DESC"%(w, interval)
				change = pd.DataFrame(list(cursor.execute(collection)))
				change = float(change[0])
				bottom_10.append(tuple((w,change)))
		bottom_10.sort(key=itemgetter(1), reverse=True)
		bottom_10 = top_10[:10]
		cnxn.commit()
	if interval == 0:
		for w in latest_row:
			if w != "":
				collection = "SELECT TOP(1) bid FROM dbo.%s ORDER BY date DESC"%(w)
				change = pd.DataFrame(list(cursor.execute(collection)))
				change = float(change[0])
				bottom_10.append(tuple((w,change)))
		bottom_10.sort(key=itemgetter(1), reverse=False)
		bottom_10 = top_10[:10]
		cnxn.commit()
	cnxn.close()
	return bottom_10

def get_coin_perc(coin):
	cnxn = pypyodbc.connect(dbcall)
	cursor = cnxn.cursor()
	coin = []
	collection = "SELECT TOP(1) bid FROM dbo.%s ORDER BY date DESC"%(coin)
	change = pd.DataFrame(list(cursor.execute(collection)))
	change = float(change[0])
	coin.append(change)
	cnxn.commit()
	cnxn.close()
	return coin

def get_previous_price(coin,interval):
	cnxn = pypyodbc.connect(dbcall)
	cursor = cnxn.cursor()
	coin = []
	collection = "SELECT TOP(%s) bid,ask FROM dbo.%s ORDER BY date DESC"%(interval,coin)
	change = pd.DataFrame(list(cursor.execute(collection)))
	coin.append(change)
	cnxn.commit()
	cnxn.close()
	return coin
