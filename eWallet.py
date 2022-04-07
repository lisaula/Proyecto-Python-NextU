from helper import *
from datetime import date
import json
from requests import Request, Session
import pprint
from pathlib import Path

class DataFileManager():
    """Class to manage write and read operations in the file."""

    def __init__(self, path):
        self.path = path
        """Crea el archivo si no existe"""
        fle = Path(path)
        fle.touch(exist_ok=True)

    def load(self):
        self.file = open(self.path, "r+")
        line = self.file.readline()
        while line:
            print(line)
            line = self.file.readline()
        self.file.close()

    def writeTransaction(self, transaction):
        with open(self.path, "a+") as outfile:
             outfile.write(json.dumps(transaction) + "\n")

    """
        Devuelve una tupla de todas las transacciones de un usuario especifico.
        En caso de pasar argumento de moneda, devuelve solo las transacciones
        con la moneda recibida en argumento.
    """
    def getCryptoTransactionsFromUser(self, user, cryptoSymbol = None):
        transactions = []
        with open(self.path, "r+") as f:
            for line in f:
                #print(line)
                transaction = json.loads(line)
                if(transaction['user'] == user):
                    #print(line)
                    if(cryptoSymbol is None):
                        transactions.append(transaction)
                    elif (transaction['currency'] ==  cryptoSymbol):
                        transactions.append(transaction)
        return tuple(transactions)

    """
        Devuelve una lista de las monedas usadas por un usuario
        registradas en el archivo, "transactions.json"
    """
    def getCurrenciesUsedByUser(self, user):
        currenciesList = []
        with open(self.path, "r+") as f:
            for line in f:
                #print(line)
                transaction = json.loads(line)
                if(transaction['user'] == user):
                    if(transaction['currency'] not in currenciesList):
                        currenciesList.append(transaction['currency'])
        return currenciesList

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

    """Funcion que obtine el precio, nombre y datos generales de una Cryptomoneda, si tal existe
        en el catalogo de Coin Market
    """
    def getCryptoData(self, currency):
        parameters = {
        'symbol':  currency,
        'convert': 'USD'
        }
        response = self.session.get(self.url, params=parameters).json()
        status = response['status']
        #pprint.pprint(response)
        if (status['error_code'] == 400):
            raise Exception("LA MONEDA \""+currency+"\" NO EXISTE DENTRO DEL CATALOGO DE COIN MARKET")
        elif (status['error_code'] > 0):
            print("****ERROR****")
            raise Exception(status['error_message'])

        key = currency.upper()
        self.crypto = {
            'symbol' : key,
            'name'  : response['data'][key]['name'],
            'price' : response['data'][key]['quote']['USD']['price']
        }
        #print("salio de get crypto")
        #print(self.crypto)
        return self.crypto

    def isUserDefined(self):
        return not self.user is None

    """
        Construye la transaccion en formato Json que se guardara en el archivo
        args:
            1. type: el tipo de transaccion
            2. user: codigo del usuario principal de la transaccion
            3. crypto: simbolo de la crypto moneda utilizada.
            4. amount: cantidad de la transaccion
            5. code: codigo(usuario) afectado de la transaccion.
    """
    def buildTransaction(self, type,user, crypto, amount, code):
        today = date.today()
        if(not isFloat(amount)):
            raise Exception("La cantidad ingresada \""+amount+"\" no es un valor numérico.")

        transaction = {
        "user" : user,
        "type" : type,
        "currency" : crypto['symbol'],
        "amount" : amount,
        "codeToAffect": code,
        "date" : today.strftime("%d/%m/%Y")
        }
        return transaction


    """
        Imprime la transaccion en formato vertical
        Se utiliza despues escribir en el archivo
        Para confirmar registro correcto despues de las llamadas
        a las funciones "receive" y "send"
    """
    def printTransaction(self, transaction):
        print("------------------------------------")
        str = "\tSe registró la transacción: \n"
        if(transaction["type"] == SEND):
            str += "->Tipo: envio de dinero.\n"
            str += "->Cuenta remitente: "+transaction["user"]+"\n"
        else:
            str += "->Tipo: recepción de dinero.\n"
            str += "->Cuenta receptora: "+transaction["user"]+"\n"
        str += "->Moneda: "+transaction["currency"]+"\n"
        str += "->Cantidad: "+transaction["amount"]+"\n"
        if(transaction["type"] == SEND):
            str += "->Cuenta receptora: "+transaction["codeToAffect"]+"\n"
        else:
            str += "->Cuenta remitente: "+transaction["codeToAffect"]+"\n"
        str += "->Fecha: "+transaction["date"]+"\n"
        print(str)
        print("------------------------------------")

    """
        Funcion de recepcion de dinero.
        Escribe dos transacciones en el archivo
            1. transaccion de tipo RECEIVE, utiliza al usuario loggeado como 'user' principal en la transaccion.
            2. transaccion de tipo DEBT, utiliza el usario que envio el dinero como el 'user' principal en la transaccion
        argumentos:
            currency: cryptomoneda usada.
            amount: cantidad de la criptomoneda.
            code: usuario que envia el dinero. (usuario afectado a restarle la cantidad de su billetera)(este usuario no ejecuta la transaccion)
    """
    def receive(self, currency, amount, code):
        crypto = self.getCryptoData(currency)
        if(code == self.user):
            raise Exception("El codigo del remitente \""+code+"\" no puede ser igual a tu codigo: "+self.user+".")
        receiveTransaction = self.buildTransaction(RECEIVE,self.user,crypto, amount, code)
        sendTransaction =    self.buildTransaction(DEBT, code, crypto, amount, self.user)
        print("despues de construir")
        self.fileManager.writeTransaction(receiveTransaction)
        self.fileManager.writeTransaction(sendTransaction)
        print("****TRANSACCIÓN REGISTRADA EXITOSAMENTE.****")
        self.printTransaction(receiveTransaction)

    """
        Funcion de envio de dinero.
        Escribe dos transacciones en el archivo
            1. transaccion de tipo SEND, utiliza al usuario loggeado como 'user' principal en la transaccion.
            2. transaccion de tipo INCOME, utiliza el usario que recibe el dinero como el 'user' principal en la transaccion
        argumentos:
            currency: cryptomoneda usada.
            amount: cantidad de la criptomoneda.
            code: usuario que recibe el dinero. (usuario afectado a sumarle la cantidad a su billetera)(este usuario no ejecuta la transaccion)
    """
    def send(self,currency, amount, code):
        crypto = self.getCryptoData(currency)
        if(code == self.user):
            raise Exception("El codigo del receptor \""+code+"\" no puede ser igual a tu codigo: "+self.user+".")
        sendTransaction = self.buildTransaction(SEND,self.user,crypto, amount, code)
        receiveTransaction =    self.buildTransaction(INCOME, code, crypto, amount, self.user)
        self.fileManager.writeTransaction(receiveTransaction)
        self.fileManager.writeTransaction(sendTransaction)
        print("****TRANSACCIÓN REGISTRADA EXITOSAMENTE.****")
        self.printTransaction(sendTransaction)

    """Funcion de impresion de reporte
        imprime en pantalla el estado de cuenta de una cryptomoneda pasada por argumento.
    """
    def printBalance(self, currency):
        crypto = self.getCryptoData(currency)
        transactions = self.fileManager.getCryptoTransactionsFromUser(self.user, crypto['symbol'])
        if(len(transactions) == 0):
            print("\n\tNo tienes ninguna transacción con la divisa: "+crypto['name']+"\n")
        else:
            self.printBalanceOfTransactions(transactions, crypto)

    """Funcion de impresion de reporte Balance General
        imprime en pantalla el estado de cuenta de todas las cryptomonedas de un usuario especifico.
        La impresion de las crypto monedas es ordenada, independientemente del orden que se registraron las transacciones en el archivo.
    """
    def printGeneralBalance(self):
        curreciesRegisteredInUserList = self.fileManager.getCurrenciesUsedByUser(self.user)
        if(len(curreciesRegisteredInUserList) == 0):
            print("\n\t*****NO TIENES TRANSACCIONES REGISTRADAS*****\n")
        else:
            self.printElementsInCurreciesList(curreciesRegisteredInUserList)

    """
        Funcion de impresion ordenada de las cryptomonedas encontradas en el archivo 'transactions.json'
    """
    def printElementsInCurreciesList(self, currenciesList):
        cryptoValuesDict = {}
        self.printHeaderOfGBReport("BALANCE GENERAL DE TRANSACCIÓNES")
        for elem in currenciesList:
            transactions = self.fileManager.getCryptoTransactionsFromUser(self.user, elem)
            self.printGeneralBalanceOfTransactions(transactions, elem, cryptoValuesDict)
        self.printBalanceOfCurrenciesDetailed(cryptoValuesDict)

    """
        Funcion de impresion del encabezado del reporte Balance General
    """
    def printHeaderOfGBReport(self, reportName):
        #print(printableLen.HEADERLEN)
        print(self.stringBuilder(printableLen.HEADERLEN,reportName, "*"))

        today = date.today()
        caracter = '-'
        header = ""
        header += "Usuario: "+ self.stringBuilder(printableLen.CODE, self.user) +"|"
        header += "Fecha: " + self.stringBuilder(printableLen.DATE, today.strftime("%d/%m/%Y"))+"|"
        print(header)
        print(caracter*printableLen.HEADERLEN)
        header = ""
        header += self.stringBuilder(printableLen.DATE, "Fecha") + "|"
        header += self.stringBuilder(printableLen.TYPE, "Tipo") + "|"
        header += self.stringBuilder(printableLen.AMOUNT, "Debitos") + "|"
        header += self.stringBuilder(printableLen.AMOUNT, "Creditos") + "|"
        header += self.stringBuilder(printableLen.AMOUNT, "Saldo") + "|"
        print(header)
        print(caracter*printableLen.HEADERLEN)

    def printGeneralBalanceOfTransactions(self, transactions, currency, cryptoValuesDict):
        print(self.stringBuilder(printableLen.HEADERLEN, currency,"-"))

        for transaction in transactions:
            self.printTransactionInBalanceFormat(transaction, cryptoValuesDict)


    """
        Funcion de impresion detallada en formato vertical para reporte de Balance General.
        Args:
            cryptoValuesDict: Diccionario que guarda como Key el symbolo de la moneda y
                              como value el numero real(float) del saldo de dicha moneda.
    """
    def printBalanceOfCurrenciesDetailed(self, cryptoValuesDict):
        print(self.stringBuilder(printableLen.HEADERLEN,"DETALLE DE SALDOS POR DIVISA", "*"))
        header = ""
        header += self.stringBuilder(printableLen.CODE, "Divisa") + "|"
        header += self.stringBuilder(printableLen.AMOUNT, "Precio") + "|"
        header += self.stringBuilder(printableLen.AMOUNT, "Saldo") + "|"
        header += self.stringBuilder(printableLen.AMOUNT, "Saldo en USD") + "|"
        print(header)
        caracter = '-'
        print(caracter*printableLen.HEADERLEN)
        totalValue =0.0
        for key, value in cryptoValuesDict.items():
            header = ""
            crypto = self.getCryptoData(key)
            header += self.stringBuilder(printableLen.CODE,crypto["name"] ) + "|"
            header += self.stringBuilder(printableLen.AMOUNT,str(crypto['price'])) + "|"
            header += self.stringBuilder(printableLen.AMOUNT, str(value)) + "|"
            balanceInUSA = self.getBalanceInUSA(value, crypto['price'])
            header += self.stringBuilder(printableLen.AMOUNT, str(balanceInUSA)) + "|"
            totalValue += balanceInUSA
            print(header)

        print("\n\nTu saldo en dólares americanos es: $"+str(totalValue))
        print(caracter*printableLen.HEADERLEN)


    def getBalanceInUSA(self, value, price):
        return value * price

    """
        Funcion de impresion de encabezado y detalle de transacciones en formato vertical
        para reporte de Balance de una moneda especifica.
        args:
            1.transactions: tupla de las transacciones a imprimir
            2. crypto: de tipo json que contiene todo los valores generales(precio, nombre, symbolo) de la cryptomoneda que se esta imprimiendo
    """
    def printBalanceOfTransactions(self,transactions, crypto):
        #print(printableLen.HEADERLEN)
        print(self.stringBuilder(printableLen.HEADERLEN,"BALANCE DE TRANSACCIÓNES", "*"))
        today = date.today()
        caracter = '-'
        header = ""
        header += "Usuario: "+ self.stringBuilder(printableLen.CODE, self.user) +"|"
        header += "Fecha: " + self.stringBuilder(printableLen.DATE, today.strftime("%d/%m/%Y"))+"|"
        header += "Divisa: " + self.stringBuilder(printableLen.CODE, crypto['name']) + "|"
        header += "Precio: " + self.stringBuilder(printableLen.AMOUNT, '$' + str(crypto['price'])," ", False)
        print(header)
        print(caracter*printableLen.HEADERLEN)
        header = ""
        header += self.stringBuilder(printableLen.DATE, "Fecha") + "|"
        header += self.stringBuilder(printableLen.TYPE, "Tipo") + "|"
        header += self.stringBuilder(printableLen.AMOUNT, "Debitos") + "|"
        header += self.stringBuilder(printableLen.AMOUNT, "Creditos") + "|"
        header += self.stringBuilder(printableLen.AMOUNT, "Saldo") + "|"
        print(header)
        print(caracter*printableLen.HEADERLEN)

        cryptoValuesDict = {}

        for transaction in transactions:
             self.printTransactionInBalanceFormat(transaction, cryptoValuesDict)

        totalValue = cryptoValuesDict[crypto['symbol']]
        print("Tu saldo en dólares americanos es de : $" + str(self.getBalanceInUSA(totalValue,crypto['price'])))
        print(caracter*printableLen.HEADERLEN)

    """
        Funcion de impresion de detalle de transacciones en formato vertical
        para reporte de Balance de una moneda especifica.
        args:
            1.transaction: Json de la transaccion a imprimir
            2. cryptoValuesDict: Diccionario para el control de suma o resta del saldo de dicha cryptomoneda de la transaccion.
                                Key -> (string)Symbolo de la cryptomoneda
                                Value -> (float) saldo de la moneda
    """
    def printTransactionInBalanceFormat(self, transaction, cryptoValuesDict):
        strPrinteable = self.stringBuilder(printableLen.DATE, transaction['date']) + "|"
        value = float(transaction['amount'])
        balance = 0.0
        if(transaction['type'] == SEND or transaction['type'] == DEBT):
            strPrinteable += self.stringBuilder(printableLen.TYPE, "EGRESO") + "|"
            strPrinteable += self.stringBuilder(printableLen.AMOUNT, str(value)) + "|"
            strPrinteable += self.stringBuilder(printableLen.AMOUNT, " ") + "|"
            balance -= value
        else:
            strPrinteable += self.stringBuilder(printableLen.TYPE, "INGRESO") + "|"
            strPrinteable += self.stringBuilder(printableLen.AMOUNT, " ") + "|"
            strPrinteable += self.stringBuilder(printableLen.AMOUNT, str(value)) + "|"
            balance += value

        if transaction['currency'] not in cryptoValuesDict:
            cryptoValuesDict[transaction['currency']] = balance
        else:
            cryptoValuesDict[transaction['currency']] += balance

        strPrinteable += self.stringBuilder(printableLen.AMOUNT, str(cryptoValuesDict[transaction['currency']])) + "|"
        print(strPrinteable)


    """
        Funcion de impresion para el reporte Historico de Transacciones
    """
    def printAllTransactions(self):
        transactions = self.fileManager.getCryptoTransactionsFromUser(self.user)
        if(len(transactions) == 0):
            print("\n\t******NO TIENES TRANSACCIÓNES REGISTRADAS.******\n")
        else:
            self.printHeaderAllTransactions()
            for transaction in transactions:
                self.printTransactionsinUserFormat(transaction)
            caracter = "-"
            print(caracter*printableLen.HEADERLEN)


    """
        Funcion que imprime el encabezado del reporte Historico de Transacciones
    """
    def printHeaderAllTransactions(self):
        print(self.stringBuilder(printableLen.HEADERLEN,"HISTORIAL DE TRANSACCIÓNES", "*"))
        today =  date.today()
        caracter = '-'
        str = "Usuario: " + self.stringBuilder(printableLen.CODE, self.user) + "|"
        str += "Fecha: " + self.stringBuilder(printableLen.DATE, today.strftime("%d/%m/%Y"))+"|"
        print(str)
        print(caracter*printableLen.HEADERLEN)

        str = self.stringBuilder(printableLen.DATE, "FECHA") + "|"
        str += self.stringBuilder(printableLen.SYMBOL, "DIVISA") + "|"
        str += self.stringBuilder(printableLen.TYPE, "TIPO") + "|"
        str += self.stringBuilder(printableLen.CODE, "CÓDIGO") + "|"
        str += self.stringBuilder(printableLen.AMOUNT, "MONTO") + "|"
        print(str)
        print(caracter*printableLen.HEADERLEN)

    """
        Funcion de impresion de las transacciones en formato horizontal para exposicion del usuario
        en el reporte Historico de Transacciones
        Comentario:
            Las transacciones 'TRANSFERENCIA' y 'RECEPCION' son de primer orden, estas transacciones fueron ejecutadas por el usuario.
            Las transacciones 'INGRESO' y 'EGRESO' son de segundo orden, estas transacciones afectan el saldo del usuario loggeado, por consecuancia de la ejecucion de otro usuario.
    """
    def printTransactionsinUserFormat(self, transaction):
        str = self.stringBuilder(printableLen.DATE, transaction["date"]) + "|"
        str += self.stringBuilder(printableLen.SYMBOL, transaction["currency"]) + "|"
        if(transaction["type"] == SEND):
            str += self.stringBuilder(printableLen.TYPE, "TRANSFERENCIA") + "|"
        elif(transaction["type"] == RECEIVE):
            str += self.stringBuilder(printableLen.TYPE, "RECEPCIÓN") + "|"
        elif(transaction["type"] == INCOME):
            str += self.stringBuilder(printableLen.TYPE, "INGRESO") + "|"
        else:
            str += self.stringBuilder(printableLen.TYPE, "EGRESO") + "|"
        str += self.stringBuilder(printableLen.CODE, transaction["codeToAffect"]) + "|"
        str += self.stringBuilder(printableLen.AMOUNT, transaction["amount"]) + "|"
        print(str)



    """
        Funcion para la construccion de un string.
        args:
            1. amount: cantidad de desface que debe tener el texto.
            2. str: texto a imprimir.
            3. caracter: si el texto es menor a la cantidad que se pretende imprimir, este char se utilizara como relleno. Por default es espacio vacio.
            4. centerContext: boolean que indica si la impresion del el texto a imprimir debe ir centrado, o debe empezar en el indice 0. 
    """
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
