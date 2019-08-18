import machine
import network
import ubinascii
import json

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

def startConfig():
    wlan_ap = network.WLAN(network.AP_IF)
    wlan_ap.active(True)
    wlan_ap.config(essid='ESP32-PK2')
    wlan_ap.ifconfig(('192.168.0.1','255.255.255.0','192.168.0.1','8.8.8.8'))
    print('AP config:', wlan_ap.ifconfig())

    import socket
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

    s = socket.socket()
    s.bind(addr)
    s.listen(10)
    print('listening on', addr)

    nets = []
    net = wlan.scan()

    for i in net:
        # print(i[0].decode())
        obj = {}
        obj['name'] = i[0].decode()
        obj['mac'] = ubinascii.hexlify(i[1]).decode()
        obj['rssi'] = str(i[3])
        obj['channel'] = str(i[2])
        obj['auth'] = i[4]
        nets.append(obj)
    
    while True:
        import httpRequestParser as parser
        cl, addr = s.accept()
        req = cl.recv(1024)
        reqObj = parser.requestParse(req)
        url = ''
        method = reqObj['method'].split(' ')
        if len(method) > 1:
            url = method[1][1:]
            print('URL: ' + url)    
        mimetype = 'text.plain'
        data = ''
        try:
            f = open(url)
            data = f.read()
            f.close()
        except:
            print('could not open')
    
        if '.' in url: 

            ext = url[-5: len(url)]
            ext = ext[ext.find('.'):]
    
            # print(ext)
    
            mimetype = {
                '.html' : 'text/html',
                '.ico' : 'image/x-icon',
                '.jpg' : 'image/jpeg',
                '.png' : 'image/png',
                '.gif' : 'image/gif',
                '.css' : 'text/css',
                '.map' : 'text',
                '.js' : 'text/javascript'
            }[ext]
        print('mime:' + mimetype )
        cl.send('HTTP/1.1 200 OK\n')
        cl.send('Content-Type: ' + mimetype +'\n')
        cl.send('Connection: close\n\n')

        if url=='login':
            # count = 0
            if not wlan.isconnected():
                wlan.connect(reqObj['body']['wifi'], reqObj['body']['pass'])
                while not wlan.isconnected():
                    print('connecting to network...')
                    pass
    
            cl.sendall('<h1>Connect with ' + reqObj['body']['wifi'] + ' ' + str(wlan.ifconfig()[0]) + '</h1>')

            try:
                f = open('config.conf', 'w+')
                msg = {
                    'wifi':reqObj['body']['wifi'],
                    'pass':reqObj['body']['pass']
                }
                x = json.dumps(msg)
                print(x)
                f.write(x)
                print('zapisano')
                f.close()
                cl.close()
                import ws1
            except:
                print('could not write')

            
        elif url == 'config.html' and len(data) > 0 and not wlan.isconnected():
            config(cl, data, nets)
        elif not wlan.isconnected():
            try:
                f = open('config.html')
                configData = f.read()
                f.close()
            except:
                print('could not open')

            config(cl, configData, nets)
        
        elif len(data) > 0:
            cl.sendall(data)
        else:
            cl.sendall('NOT FOUND')
        cl.close()
                
def config(clientSocket, data, nets):
    rows = []
    for net in nets:
        row = '<tr><td class="name">%s</td><td class="bssid">%s</td><td class="signal">%s</td><td class="channel">%s</td><td class="auth">%s</td></tr>'  % (net['name'], net['mac'], net['rssi'], net['channel'], net['auth'])
        rows.append(row)
    response = data % '\n'.join(rows)
    clientSocket.sendall(response)                
            