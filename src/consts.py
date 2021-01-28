HOST = "127.0.0.1"
PORT = 4560

RESPONSE = 'HTTP/1.1 101 Switching Protocols\r\n' \
           'Upgrade: websocket\r\n' \
           'Connection: Upgrade\r\n' \
           'Sec-WebSocket-Accept: %s\r\n\r\n'
