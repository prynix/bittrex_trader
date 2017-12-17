#This is designed to hold the bittrex api functions accessed by the trading folder
from bittrex import Bittrex
from config import api_key, api_secret, dbcall
import pandas as pd
import time
import datetime
import pypyodbc

#definitions
d = {}
p = Bittrex(None, None)
#tick = p.get_market_summaries()

#Database access
cnxn = pypyodbc.connect(dbcall)
cursor = cnxn.cursor()

def update_prices():
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
	return ("Archived at: ", time.asctime(time.localtime(time.time())))

def get_top5():
	collection = "SELECT * FROM sys.Tables"
	latest_row = pd.DataFrame(list(cursor.execute(collection)))
	latest_row = latest_row[0]
	#for x in latest_row:
		#collection = "SELECT TOP(1) bid FROM dbo.%s ORDER BY date DESC"%(x)
		#change = pd.DataFrame(list(cursor.execute(collection)))
		#change = latest_row[0]
		#x = latest_row.append(change)

	for w in latest_row.split(" "):
		if w != "":
			collection = "SELECT TOP(1) bid FROM dbo.%s ORDER BY date DESC"%(x)
			change = pd.DataFrame(list(cursor.execute(collection)))
			change = change[0]
			latest_row.append(change)
	print(latest_row)
	cnxn.commit()

get_top5()

#def get_bottom5():
