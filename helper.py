def isNumber(option):
    try:
        option = int(option)
        return True
    except ValueError:
        return False

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


class printableLen:
    CODE= 13
    TYPE= 13
    SYMBOL= 10
    AMOUNT= 25
    DATE= 10
    HEADERLEN = (DATE + TYPE + (AMOUNT * 3) + 5)
