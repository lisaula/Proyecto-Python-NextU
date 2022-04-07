"""
    Funcion de validacion que valor pasado por argumento sea un numero entero.
"""
def isNumber(option):
    try:
        option = int(option)
        return True
    except ValueError:
        return False

"""
    Funcion de validacion que valor pasado por argumento sea un numero real.
"""
def isFloat(option):
    try :
        option = float(option)
        return True
    except :
        return False

"""Variables de control para escritura de transacciones"""
SEND = 'S'
RECEIVE = 'R'
INCOME = 'I'
DEBT = 'D'


"""
    Clase para control de margene de impresion. 
"""
class printableLen:
    CODE= 13
    TYPE= 13
    SYMBOL= 10
    AMOUNT= 25
    DATE= 10
    HEADERLEN = (DATE + TYPE + (AMOUNT * 3) + 5)
