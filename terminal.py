from helper import *
from eWallet import *
class Terminal:
    """Text interface Class."""

    def __init__(self):
        self.exit = False
        self.wallet = EWalltet()

    def Login(self):
        print(".....Bienvenido a tu billetera electrónica....")
        while not self.wallet.isUserDefined():
            print("Ingresa un Codigo de Usuario (Solo letras y números).")
            user = input("O escribe \"exit\" para salir: ")
            while not user.isalnum():
                print("Ingresa un Codigo de Usuario (Solo letras y números).")
                user = input("O escribe \"exit\" para salir: ")
            self.wallet.setUser(user)
            # print("wallet user " + self.wallet.user+ " user "+user)
            if(user == "exit"):
                print("Adios.")
                self.exit = True

    def start(self):
        while not self.exit:
            self.Login()
            if(self.wallet.isUserDefined() and not self.exit):
                print("Hola "+ self.wallet.getUser())
                print ("Escoje una de las opciones:")
                print ("\t1. Recibir cantidad.")
                print ("\t2. Transferir monto.")
                print ("\t3. Mostrar balance de una moneda.")
                print ("\t4. Mostrar Balance General.")
                print ("\t5. Mostrar historico de transacciones.")
                print ("\t6. Salir del menú.")
                option = input("Indique un número: ")
                self.validOptions(option)


    def validOptions(self, option):
        if(isNumber(option)):
            if(option == "1"):
                print("Escogiste recibir cantidad.")
                currency = input("Ingresa la moneda que recibiras: ")
                amount = input("Ingrese la cantidad que recibiras: ")
                code = input("Ingrese el codigo del remitente: ")
                #try:
                self.wallet.receive(currency, amount, code)
                #except Exception as e:
                #    print("****Error****")
                #    print(str(e))
            elif (option == "2"):
                print("Escogiste transferir monto.")
                currency = input("Ingresa la moneda en que transferiras: ")
                amount = input("Ingrese la cantidad: ")
                code = input("Ingrese el codigo del receptor: ")
                try:
                    self.wallet.send(currency, amount, code)
                except Exception as e:
                    print(e)
            elif (option == "3"):
                print("Escogiste mostrar balance de una moneda.")
                currency = input("Ingresa la moneda :")
                #try:
                self.wallet.printBalance(currency)
                #except Exception as e:
                #    print(e)
            elif (option == "4"):
                print("Escogiste mostrar balance general.")
                #try:
                self.wallet.printGeneralBalance()
                #except Exception as e:
                #    print(e)
            elif (option == "5"):
                print("Escogiste mostrar historico de transacciónes.")
            elif (option == "6"):
                print("Adios.")
                self.wallet.setUser(None)
            else:
                print("Opcion no valida, escoja una opcion del menu.")
        else:
            print("Opcion no valida. Ingrese un numero de las opciones del menu.\nReintente de nuevo.")
