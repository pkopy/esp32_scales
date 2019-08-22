
import machine
from machine import Timer, RTC
from microWebSrv import MicroWebSrv
import json
from time import sleep
from machine import UART
import udp
import uartData
import urequests
# import gc
# gc.collect()

# Initialize onewire & DS18B20 temperature sensor
# ow = Onewire(23)
# ds = Onewire.ds18x20(ow, 0)
uart = UART(2, 9600, tx=17, rx=16 ) 

# Pull time from Internet
rtc = RTC()
rtc.ntp_sync(server='192.168.4.1', tz='EST-2')

# Instatiate hardware timer
tm = Timer(0)
measures = [{"newMeasure":True, "complete": False}]


# mws = None
def cb_receive_text(webSocket, msg) :
    print("WS RECV TEXT : %s" % msg)
    
    receivedData = uartData.data(msg)
    # objData = x
    # print(objData)
    if 'command' in receivedData and receivedData['command'] == 'SI':
        # print(x['command'])
        tm.deinit()
        del measures[1:]
        measures[0] = {"newMeasure":True, "complete": False}
        print(measures)
        cb = lambda timer: cb_timer(timer, webSocket, receivedData)
        # Init and start timer to poll temperature sensor
        tm.init(period=250, callback=cb)
    if 'command' in receivedData and receivedData['command'] == 'STOP':
        tm.deinit()
    if 'command' in receivedData and receivedData['command'] == 'C' and len(measures) > 1:
        continueObj = {
            'all':measures,
            'continue': True
        }
        print(tm)
        webSocket.SendText(json.dumps(continueObj))
    if 'command' in receivedData and receivedData['command'] == 'ADD':
        
        try:
            f = open('config.conf', 'r')
            data = f.read()
            obj = json.loads(data)
            obj['guid'] = receivedData['guid']
            f.close()
            f = open('config.conf', 'w')
            f.write(json.dumps(obj))
            print('zapisano')
            f.close()
        except:
            print('could not open')

    # uart.write(msg+'\r\n')
    # webSocket.SendText(uart.read())
    webSocket.SendText(json.dumps(receivedData))


def cb_receive_binary(webSocket, data) :
    print("WS RECV DATA : %s" % data)

# def stop():
#     print('Cleaning up and exiting.')
#     mws.Stop()
#     tm.deinit()
#     udp.test()
    # rtc.clear()
    # ds.deinit()
    # ow.deinit()

def cb_closed(webSocket) :
    # tm.deinit()  # Dispose of timer
    # udp.test()
    # stop()
    print("WS CLOSED")

def cb_timer(timer, websocket, objData):
    # Store data in dict
    
    dict = {
        'min':0,
        'max':0,
        'base':0,
        'measure':0,
        'treshold':1
    }
    pin = machine.Pin(2, machine.Pin.OUT)

    if 'command' in objData:
        uart.write(objData['command'] +'\r\n')
        data = uart.read()
        scale_response = data.decode('ascii')
        command = scale_response[:scale_response.find(' ')]
        measure = scale_response[scale_response.find(' '):].lstrip()
        dict['isStab'] = True
        
        if '?' in measure:
            checkStr = measure[1:].lstrip()
            dict['isStab'] = False
            if len((checkStr[:checkStr.find('g')-1])) > 0:
                try:
                    dict['measure'] = float(checkStr[:checkStr.find('g')-1])
                except:
                    print('bad value')
        else:
            if len((measure[:measure.find('g')-1])) > 0:
                try:
                    dict['measure'] = float(measure[:measure.find('g')-1])
                except:
                    print('bad value')
        print('msasas: ', measure[:measure.find('g')-1])
        dict['command'] = command
        dict['time'] = rtc.now()
        dict['max'] = objData['max']
        dict['min'] = objData['min']
        dict['base'] = objData['base']
        dict['treshold'] = objData['treshold']
        dict['measureNumber'] = 0

        
        
        if 'base' in objData:
            inRange = (dict['measure'] < objData['base'] + objData['max'] and  dict['measure'] > objData['base'] - objData['min']) and True or False
            # print(inRange)

        if 'measure' in dict and dict['measure'] > 0 and dict['isStab'] and inRange and measures[0]['newMeasure']:
            measures.append(dict)
            
            dict['stab'] = dict['measure']
            dict['measureNumber'] = len(measures) - 1
            print('add measure')
            measures[0]['newMeasure'] = False
            try:
                response = urequests.post("http://10.10.20.107:5000/addDevice", json=dict)
                response.close()
            except:
                print('Could not send to DB')
            print(measures)
        
        # if len(measures) > 1:
            # if ('measure' in dict and dict['measure'] > 0 and measures[len(measures) - 1]['measure'])  and (dict['measure'] >= measures[len(measures) - 1]['measure'] + 10 or dict['measure'] <= measures[len(measures) - 1]['measure'] - 10 or dict['measure'] <= objData['treshold']):
        if ('measure' in dict and dict['measure'] > 0 and 'measure' in  measures[len(measures) - 1])  and (dict['measure'] <= objData['treshold']):
            measures[0]['newMeasure'] = True
            # and (dict['measure'] >= measures[len(measures) - 1] + 10 or dict['measure'] <= measures[len(measures) - 1] - 10 or dict['measure'] <= 1):
        
        if inRange and  'measure' in dict and dict['measure'] >= objData['treshold'] and dict['isStab']: 
            pin.value(1)
        else:
            pin.value(0)

        # all = []
        # for mesure in measures[:]:
        #     all.append(mesure)
        # dict['allMeasures'] = all


        # if 'stab' in dict:
        objToSend = {
            'all':measures,
            'measure':dict['measure'],
            
        }
        if 'stab' in dict:
            objToSend['stab'] = dict['stab']

        websocket.SendText(json.dumps(objToSend))
        
        
        if 'quantity' in objData and objData['quantity'] == dict['measureNumber']:
            measures[0]['newMeasure'] = True
            measures[0]['complete'] = True
            uart.read()
            tm.deinit()
            objToSend['measure'] = 0
            websocket.SendText(json.dumps(objToSend))

        
        # Convert data to JSON and send
  
def cb_accept_ws(webSocket, httpClient) :
    print("WS ACCEPT")
    webSocket.RecvTextCallback   = cb_receive_text
    webSocket.RecvBinaryCallback = cb_receive_binary
    webSocket.ClosedCallback 	 = cb_closed
    # Use lambda to pass websocket to timer callback
    # cb = lambda timer: cb_timer(timer, webSocket)
    # Init and start timer to poll temperature sensor
    # tm.init(period=250, callback=cb)



mws = MicroWebSrv(port=7000)                 # TCP port 80 and files in /flash/www
print('Websocket is ready')
mws.MaxWebSocketRecvLen     = 256   # Default is set to 1024
mws.WebSocketThreaded       = True  # WebSockets with new threads
mws.WebSocketStackSize      = 4096
mws.AcceptWebSocketCallback = cb_accept_ws # Function to receive WebSockets
mws.Start(threaded=False)  # Blocking call (CTRL-C to exit)

print('Cleaning up and exiting.')
mws.Stop()
# tm.deinit()

