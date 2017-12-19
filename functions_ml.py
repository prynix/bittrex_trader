#This is designed to hold the bittrex api functions accessed by the trading folder
from bittrex import Bittrex
from config import api_key, api_secret, dbcall
from operator import itemgetter
import pandas as pd
import time
import datetime
import pypyodbc
import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt

#Database access
cnxn = pypyodbc.connect(dbcall)
cursor = cnxn.cursor()

def custom_term_linear_market(coin, interval, ahead):
    cnxn = pypyodbc.connect(dbcall)
    cursor = cnxn.cursor()
    coin = coin.replace('-','')
    string = "SELECT ask, date FROM dbo.%s WHERE date > GETDATE()-%s ORDER BY date DESC"%(coin, interval)
    data = pd.read_sql(string, cnxn)
    df = pd.DataFrame(data)
    df['index1'] = df.index
    x = len(df['index1']) + ahead #amount of intervals (coinprices) ahead
    linear_mod = linear_model.LinearRegression() #defining the linear regression model
    dates = np.reshape(df['index1'],(len(df['index1']),1)) # converting to matrix of n X 1
    prices = np.reshape(df['ask'],(len(df['ask']),1))
    linear_mod.fit(dates,prices) #fitting the data points in the model
    predicted_price = linear_mod.predict(x)
    return ("Predicted price: ",predicted_price[0][0])#,linear_mod.coef_[0][0] ,linear_mod.intercept_[0]
'''
def custom_term_linear_orderbook(coin, interval, ahead):
    cnxn = pypyodbc.connect(dbcall)
    cursor = cnxn.cursor()
    coin = coin.replace('-','')
    string = "SELECT price,key FROM dbo.orderbook WHERE key > %s ORDER BY key DESC"%(interval)
    data = pd.read_sql(string, cnxn)
    df = pd.DataFrame(data)
    df['index1'] = df.index
    x = len(df['index1']) + ahead #amount of intervals (coinprices) ahead
    linear_mod = linear_model.LinearRegression() #defining the linear regression model
    dates = np.reshape(df['index1'],(len(df['index1']),1)) # converting to matrix of n X 1
    prices = np.reshape(df['ask'],(len(df['ask']),1))
    linear_mod.fit(dates,prices) #fitting the data points in the model
    predicted_price = linear_mod.predict(x)
    return ("Predicted price: ",predicted_price[0][0])#,linear_mod.coef_[0][0] ,linear_mod.intercept_[0]'''

#def medium_term():


#def long_term():


#def custom_term():
