from helper import *
from datetime import date
import json
from requests import Request, Session
import pprint

class DataFileManager():
    """Class to manage write and read operations in the file."""

    def __init__(self, path):
        self.path = path

    def load(self):
        self.file = open(self.path, "r")
        line = self.file.readline()
        while line:
            print(line)
            line = self.file.readline()
        self.file.close()

    def writeTransaction(self, transaction):
        with open(self.path, "a") as outfile:
             outfile.write(json.dumps(transaction) + "\n")

    def getCryptoTransactionsFromUser(self, user, cryptoSymbol):
        transactions = []
        with open(self.path, "r") as f:
            for line in f:
                #print(line)
                transaction = json.loads(line)
                if(transaction['user'] == user and transaction['currency'] ==  cryptoSymbol):
                    print(line)
                    transactions.append(transaction)
        return tuple(transactions)


class EWalltet():
    """Electronic Wallet Class"""
    def __init__(self):
        self.user = None
        self.fileManager = DataFileManager("transactions.json")
        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

        self.COINMARKET_API_KEY = "2448e9c9-b938-4f0e-85f1-9878a7b41c87"
        self.headers = {
          'Accepts': 'application/json',
          'X-CMC_PRO_API_KEY': self.COINMARKET_API_KEY
        }

        self.session = Session()
        self.session.headers.update(self.headers)

    def setUser(self, user):
        self.user = user
    def getUser(self):
        return self.user

    def getCryptoData(self, currency):
        parameters = {
        'symbol':  currency,
        'convert': 'USD'
        }
        response = self.session.get(self.url, params=parameters).json()
        status = response['status']
        pprint.pprint(response)
        if (status['error_code'] > 0):
            print("AQUI ESTOY")
            print("****ERROR****")
            raise Exception(status['error_message'])

        key = currency.upper()
        self.crypto = {
            'symbol' : key,
            'name'  : response['data'][key]['name'],
            'price' : response['data'][key]['quote']['USD']['price']
        }
        print("salio de get crypto")
        print(self.crypto)
        return self.crypto

    def isUserDefined(self):
        return not self.user is None

    def buildTransaction(self, type,user, crypto, amount, code):
        today = date.today()
        transaction = {
        "user" : user,
        "type" : type,
        "currency" : crypto['symbol'],
        "amount" : amount,
        "codeToAffect": code,
        "date" : today.strftime("%d/%m/%Y")
        }
        return transaction

    def printTransaction(self, transaction):
        print("------------------------------------")
        str = "\tSe registró la transacción: \n"
        if(transaction["type"] == SEND):
            str += "->Tipo: recepción de dinero.\n"
            str += "->Cuenta receptora: "+transaction["user"]+"\n"
        else:
            str += "->Tipo: envio de dinero.\n"
            str += "->Cuenta remitente: "+transaction["user"]+"\n"
        str += "->Moneda: "+transaction["currency"]+"\n"
        str += "->Cantidad: "+transaction["amount"]+"\n"
        if(transaction["type"] == SEND):
            str += "->Cuenta remitente: "+transaction["codeToAffect"]+"\n"
        else:
            str += "->Cuenta receptora: "+transaction["codeToAffect"]+"\n"
        str += "->Fecha: "+transaction["date"]+"\n"
        print(str)
        print("------------------------------------")

    def receive(self, currency, amount, code):
        crypto = self.getCryptoData(currency)
        if(code == self.user):
            raise Exception("El codigo del remitente +\""+code+"\" no puede ser igual a tu codigo: "+self.user+".")
        receiveTransaction = self.buildTransaction(RECEIVE,self.user,crypto, amount, code)
        sendTransaction =    self.buildTransaction(SEND, code, crypto, amount, self.user)
        print("despues de construir")
        self.fileManager.writeTransaction(receiveTransaction)
        self.fileManager.writeTransaction(sendTransaction)
        print("****TRANSACCIÓN REGISTRADA EXITOSAMENTE.****")
        self.printTransaction(transaction)

    def send(self,currency, amount, code):
        crypto = self.getCryptoData(currency)
        if(code == self.user):
            raise Exception("El codigo del receptor +\""+code+"\" no puede ser igual a tu codigo: "+self.user+".")
        sendTransaction = self.buildTransaction(SEND,self.user,crypto, amount, code)
        receiveTransaction =    self.buildTransaction(RECEIVE, code, crypto, amount, self.user)
        self.fileManager.writeTransaction(receiveTransaction)
        self.fileManager.writeTransaction(sendTransaction)
        print("****TRANSACCIÓN REGISTRADA EXITOSAMENTE.****")
        self.printTransaction(transaction)

    def printBalance(self, currency):
        crypto = self.getCryptoData(currency)
        transactions = self.fileManager.getCryptoTransactionsFromUser(self.user, crypto['symbol'])
        if(len(transactions) == 0):
            print("\tNo tienes ninguna transacción con la divisa: "+crypto['name'])
        else:
            self.printBalanceOfTransactions(transactions, crypto)

    def printBalanceOfTransactions(self,transactions, crypto):
        headerLen = (printableLen.DATE + printableLen.TYPE + (printableLen.AMOUNT * 3) + 5)
        print(headerLen)
        print(self.stringBuilder(headerLen,"BALANCE DE TRANSACCIÓNES", "*"))
        today = date.today()
        caracter = '-'
        header = ""
        header += "Usuario: "+ self.stringBuilder(printableLen.CODE, self.user) +"|"
        header += "Fecha: " + self.stringBuilder(printableLen.DATE, today.strftime("%d/%m/%Y"))+"|"
        header += "Divisa: " + self.stringBuilder(printableLen.CODE, crypto['name']) + "|"
        header += "Precio: " + self.stringBuilder(printableLen.AMOUNT, '$' + str(crypto['price'])," ", False)
        print(header)
        print(caracter*headerLen)
        header = ""
        header += self.stringBuilder(printableLen.DATE, "Fecha") + "|"
        header += self.stringBuilder(printableLen.TYPE, "Tipo") + "|"
        header += self.stringBuilder(printableLen.AMOUNT, "Debitos") + "|"
        header += self.stringBuilder(printableLen.AMOUNT, "Creditos") + "|"
        header += self.stringBuilder(printableLen.AMOUNT, "Saldo") + "|"
        print(header)
        print(caracter*headerLen)

        cryptoValuesDict = {
            crypto['symbol'] : 0.0
        }

        for transaction in transactions:
            cryptoValuesDict = self.printTransactionInBalanceFormat(transaction, cryptoValuesDict)

        totalValue = cryptoValuesDict[crypto['symbol']]
        print("Tu saldo en dólares americanos es de : $" + str(totalValue*crypto['price']))

    def printTransactionInBalanceFormat(self, transaction, cryptoValuesDict):
        strPrinteable = self.stringBuilder(printableLen.DATE, transaction['date']) + "|"
        value = float(transaction['amount'])
        balance = 0.0
        if(transaction['type'] == SEND):
            strPrinteable += self.stringBuilder(printableLen.TYPE, "TRANSFERENIA") + "|"
            strPrinteable += self.stringBuilder(printableLen.AMOUNT, str(value)) + "|"
            strPrinteable += self.stringBuilder(printableLen.AMOUNT, " ") + "|"
            balance -= value
        else:
            strPrinteable += self.stringBuilder(printableLen.TYPE, "RECEPCIÓN") + "|"
            strPrinteable += self.stringBuilder(printableLen.AMOUNT, " ") + "|"
            strPrinteable += self.stringBuilder(printableLen.AMOUNT, str(value)) + "|"
            balance += value

        cryptoValuesDict[transaction['currency']] += balance
        strPrinteable += self.stringBuilder(printableLen.AMOUNT, str(cryptoValuesDict[transaction['currency']])) + "|"
        print(strPrinteable)
        return cryptoValuesDict


    def stringBuilder(self, amount, str, caracter = " ", centerContext = True):
        strPrinteable = ""
        strLen = len(str)
        if (centerContext == True) :
            centerIndex = int(amount / 2) - int(strLen / 2)
        else:
            centerIndex = 0
        for x in range(amount):
            if(x < centerIndex):
                strPrinteable += caracter
            elif(x >= centerIndex and x < centerIndex + strLen):
                index = x - centerIndex
                strPrinteable += str[index]
            else:
                strPrinteable += caracter
        return strPrinteable
