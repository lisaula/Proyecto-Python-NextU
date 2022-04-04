def isNumber(option):
    try:
        option = int(option)
        return True
    except ValueError:
        return False

"""Variables de control para escritura de transacciones"""
SEND = 'S'
RECEIVE = 'R'


class printableLen:
    CODE= 13
    TYPE= 13
    SYMBOL= 10
    AMOUNT= 25
    DATE= 10
