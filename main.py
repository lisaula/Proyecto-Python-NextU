from requests import Request, Session
import json
# from eWallet import *
from terminal import Terminal
import pprint
from helper import *


TIU = Terminal()
while not TIU.exit :
     TIU.start()

"""https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"""
# url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
#
# COINMARKET_API_KEY = "2448e9c9-b938-4f0e-85f1-9878a7b41c87"
# headers = {
#   'Accepts': 'application/json',
#   'X-CMC_PRO_API_KEY': COINMARKET_API_KEY
# }
#
# session = Session()
# session.headers.update(headers)
# while True:
#     currency = input("enter currency: ")
#     parameters = {
#     'symbol':  currency,
#     'convert': 'USD'
#     }
#     response = session.get(url, params=parameters).json()
#     status = response['status']
#     if (status['error_code'] > 0):
#         print(status['error_message'])
#     else:
#         print(response['data'][currency]['quote']['USD']['price'])


#data=requests.get("https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest",headers=headers).json()
#pprint.pprint(response)
#print ("data %s", data)
# for cripto in data["data"]:
#     monedas_dict[cripto["symbol"]]=cripto["name"]
#     str = cripto["symbol"] + "USDT"
#     try:
#         price = getPrice(str).json()
#         print(str + "price "+ price["price"])
#     except Exception as e:
#         print("Error")
#         print(price)
#
# monedas = monedas_dict.keys()

# dictionary ={
# "Code" : "01",
# "Crypto" : "BTC",
# "Type" : "send",
# "Mount" : 100,
# "CodeAfected" : "02",
# }
#
# with open("transactions.json", "w") as outfile:
#     json.dump(dictionary, outfile)
#
# file_m = DataFileManager("transactions.json")
# file_m.load()
