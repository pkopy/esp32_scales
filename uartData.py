# from machine import UART
import json
# uart = UART(2, 9600, tx=17, rx=16 ) 

def data(msg):
    
    # print
    # uart.write('SI\r\n')
    # return uart.read()
    return json.loads(msg)