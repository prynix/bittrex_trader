#This is designed to hold the bittrex api functions accessed by the trading folder
from bittrex import Bittrex
from config import api_key, api_secret, dbcall, access_token
from operator import itemgetter
import pandas as pd
import time
import datetime
import pypyodbc
import requests as rq
import json


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
		print('sent')

def get_orderbook(market):
	if '-' not in market:
		if 'BTC' in market[:4]:
			market = market.replace('BTC','BTC-')
		if 'ETH' in market[:4]:
			market = market.replace('ETH','ETH-')
		if 'USDT' in market[:4]:
			market = market.replace('USDT','USDT-')
	cnxn = pypyodbc.connect(dbcall)
	cursor = cnxn.cursor()
	order_book = p.get_orderbook(market,'both')
	order_book = order_book['result']
	buy_orderbook = []
	sell_orderbook = []
	df_sell_desc = []
	df_buy_desc = []
	column_headers = ['rate','quantity','total']
	if order_book['sell']:
		for item in order_book['sell']:
			total = float(item['Rate'])*float(item['Quantity'])
			total = '{:.8f}'.format(total)
			sell_orderbook.append(tuple(((item['Rate']),(item['Quantity']),(total))))
			df_sell_orderbook = pd.DataFrame(list(sell_orderbook),columns=column_headers)
			df_sell_orderbook = df_sell_orderbook[['rate','quantity','total']].apply(pd.to_numeric)
			df_sell_desc = df_sell_orderbook.describe()
	if order_book['buy']:
		for item in order_book['buy']:
			total = float(item['Rate'])*float(item['Quantity'])
			total = '{:.8f}'.format(total)
			buy_orderbook.append(tuple(((item['Rate']),(item['Quantity']),(total))))
			df_buy_orderbook = pd.DataFrame(list(buy_orderbook),columns=column_headers)
			df_buy_orderbook = df_buy_orderbook[['rate','quantity','total']].apply(pd.to_numeric)
			df_buy_desc = df_buy_orderbook.describe()
	return {'df_buy_orderbook':df_buy_orderbook, 'df_sell_orderbook':df_sell_orderbook, 'df_buy_desc':df_buy_desc, 'df_sell_desc':df_sell_desc}

def makeratios(totalbuys,totalsells):
	ratiobuy = 1
	ratiosell = 1
	if totalbuys > totalsells:
		r = totalbuys/totalsells
		r = '{:.2f}'.format(r)
		ratio = '%s:%s'%(r,1)
		ratiobuy = r
	if totalbuys < totalsells:
		r = totalsells/totalbuys
		r = '{:.2f}'.format(r)
		ratio = '%s:%s'%(1,r)
		ratiosell = r
	if totalbuys == totalsells:
		ratio = '%s:%s'%(1,1)
	return {'ratio':ratio, 'ratiobuy':ratiobuy,'ratiosell':ratiosell}

def getratios(): #slow
	column_headers = ['coin','buy ratio','sell ratio']
	ratio_list = pd.DataFrame(columns=column_headers)
	cnxn = pypyodbc.connect(dbcall)
	cursor = cnxn.cursor()
	collection = "SELECT * FROM sys.Tables"
	latest_row = pd.DataFrame(list(cursor.execute(collection)))
	latest_row = latest_row[0]
	movers = []
	for w in latest_row:
		if w != "":
			if "USDT" not in w:
				print(w)
				orders = get_orderbook(w)
				totalbuys = orders['df_buy_orderbook']['total']
				totalbuys = sum(totalbuys)
				totalsells = orders['df_sell_orderbook']['total']
				totalsells = sum(totalsells)
				ratio = makeratios(totalbuys,totalsells)
				ratio_list = ratio_list.append({'coin':w,'buy ratio':ratio['ratiobuy'],'sell ratio':ratio['ratiosell']}, ignore_index=True)
	ratio_list = ratio_list,sort(columns,descending=[0,1,0])
	return ratio_list

def update_prices(): #done
	cnxn = pypyodbc.connect(dbcall)
	cursor = cnxn.cursor()
	tick = p.get_market_summaries()
	tick = tick['result']
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
		if bid != old:
			change = ((float(bid)/float(old))-1)*100
			change = '{:.8f}'.format(change)
		else:
			change = 0
			change = int(change)
		date = time.strftime('%Y-%m-%d %H:%M:%S')
		#Inital table creation script
		#change = 0
		#string = "CREATE TABLE %s(currency varchar(10), last decimal(16,8), bid decimal(16,8), ask decimal(16,8), volume decimal(20,8), openbuyorders decimal(16,8), opensellorders  decimal(16,8), change decimal(16,8), date datetime);"%(y)
		string = "INSERT INTO dbo.%s VALUES ('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"%(y, y, last, bid, ask, volume, openbuyorders, opensellorders, change, date)
		#print(string)
		cursor.execute(string,)
		cnxn.commit()
	cnxn.close()
	return ("Archived at: ", time.asctime(time.localtime(time.time())))

def create_tables():
	cnxn = pypyodbc.connect(dbcall)
	cursor = cnxn.cursor()
	tick = p.get_market_summaries()
	tick = tick['result']
	for x in tick:
		y = x['MarketName']
		y = y.replace('-','')
		string = "CREATE TABLE %s(currency varchar(10), last decimal(16,8), bid decimal(16,8), ask decimal(16,8), volume decimal(20,8), openbuyorders decimal(16,8), opensellorders  decimal(16,8), change decimal(16,8), date datetime);"%(y)
		cursor.execute(string,)
		cnxn.commit()
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
		old = 0
		old = int(old)
		change = 0
		change = int(change)
		date = time.strftime('%Y-%m-%d %H:%M:%S')
		string = "INSERT INTO dbo.%s VALUES ('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"%(y, y, last, bid, ask, volume, openbuyorders, opensellorders, change, date)
		cursor.execute(string,)
		cnxn.commit()
	cnxn.close()
	return ("Created at: ", time.asctime(time.localtime(time.time())))


def getdayaverage(coin,interval):
	if interval % 1 != 0:
		return ("Please enter in whole days or enter '0' to get all")
	if interval % 1 == 0 and interval != 0:
		column_headers = ['average bid','average ask','average volume','date']
		collection = "SELECT [bid],[ask],[volume],[date] FROM dbo.%s WHERE [date] <= DATEADD(day,%s, GETDATE()) ORDER BY date DESC"%(coin,interval)
		latest_row = pd.DataFrame(list(cursor.execute(collection)),columns=column_headers)
		latest_row = latest_row.drop('date', axis=1).apply(lambda x: x.mean())
		latest_row = latest_row.rename_axis('%s day average'%(interval))
		cnxn.commit()
		return latest_row
	if interval == 0:
		column_headers = ['average bid','average ask','average volume','date']
		collection = "SELECT [bid],[ask],[volume],[date] FROM dbo.%s ORDER BY date DESC"%(coin)
		latest_row = pd.DataFrame(list(cursor.execute(collection)),columns=column_headers)
		latest_row = latest_row.drop('date', axis=1).apply(lambda x: x.mean())
		latest_row = latest_row.rename_axis('9 day average')
		cnxn.commit()
		return latest_row

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

def getmovers(amount):
	cnxn = pypyodbc.connect(dbcall)
	cursor = cnxn.cursor()
	collection = "SELECT * FROM sys.Tables"
	latest_row = pd.DataFrame(list(cursor.execute(collection)))
	latest_row = latest_row[0]
	movers = []
	for w in latest_row:
		if w != "":
			if "USDT" not in w:
				collection = "SELECT TOP(1) change FROM dbo.%s ORDER BY date DESC"%(w)
				change = pd.DataFrame(list(cursor.execute(collection)))
				change = float(change[0])
				movers.append(tuple((w,change)))
	movers.sort(key=itemgetter(1), reverse=True)
	movers = movers[:amount]
	cnxn.commit()
	cnxn.close()
	return movers

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
