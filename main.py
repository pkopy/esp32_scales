
import network
from machine import idle
import udp
import wifiConfig
import json
import upysh as fm
import urequests
# import gc
# gc.collect()
                       
# mdns = mDNS()
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
# mdns = network.mDNS()

# wlan_ap = network.WLAN(network.AP_IF)
# wlan_ap.active(True)
# wlan_ap.config(essid='ESP32 - PK1')
# print('AP config:', wlan_ap.ifconfig())


        

#     print('Connected:', wlan.ifconfig())
#     # mdns.start('myESP', 'MicroPython ESP32')
#     # ftp.start(user='admin', password='admin')
#     # telnet.start(user='admin', password='admin')
config = ''
try:
    f = open('config.conf')
    config = f.read()
    f.close()
except:
    # f = open('config.cfg', 'w')
    # config = f.read()
    print('could not open')

# if not wlan.isconnected() :
#     print('connecting to network...')
#     wlan.connect('RADWAG', 'rdg37gh213vbk')
#     while not wlan.isconnected():
#         idle()
#         break
def connect(obj):
    print('connecting to network...')
    wlan.connect(obj['wifi'], obj['pass'])
    while not wlan.isconnected():
        idle()
        print('Connecting...')
    print('Connected:', wlan.ifconfig())
    

    
if len(config) > 0:
    test = json.loads(config)
    if not wlan.isconnected() and 'wifi' in test and not 'guid' in test:
        connect(test)
        # response = urequests.post("http://10.10.20.107:5000/addDevice", json={"oko":155})
        # response.close()
        udp.test()
        # import ws1
    # if 'guid' in test and 'wifi' in test:
    #     connect(test)
    #     import ws1
    # print(test)
else:
    wifiConfig.startConfig()

# udp.test()
