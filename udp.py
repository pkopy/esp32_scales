import logging
import socket

log = logging.getLogger('udp_server')


def udp_server(host='0.0.0.0', port=1234):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    log.info("Listening on udp %s:%s" % (host, port))
    s.bind((host, port))
    daa = b''
    while True:
        (data, addr) = s.recvfrom(1024)
        print(data, addr)
        if data == b'':
            s.sendto(b'zamykam', addr)
            break
        if data == b'start\n':
            s.sendto(b'Socked connected - send data\n', addr)
            daa = data
            
            break
            # ws1.start()
        # else:
        #     s.sendto(b'test-XXXX', addr)
        yield data
    if daa == b'':
        test()
    else:
        # test()
        # print('udp is closed')
        import ws1
        # ws1.start()
    

def test():
    FORMAT_CONS = '%(asctime)s %(name)-12s %(levelname)8s\t%(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT_CONS)

    for data in udp_server():
        log.debug(data)