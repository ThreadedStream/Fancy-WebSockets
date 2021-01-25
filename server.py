import os
import socket
import logging
import base64
import time
import hashlib
import io
import asyncio
from utils import removesuffix

logging.getLogger().setLevel(logging.DEBUG)

HOST = "127.0.0.1"
PORT = 4560

GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

RESPONSE = 'HTTP/1.1 101 Switching Protocols\r\n' \
           'Upgrade: websocket\r\n' \
           'Connection: Upgrade\r\n' \
           'Sec-WebSocket-Accept: %s\r\n\r\n'

PING = 0x81
LEN = 0x05
MSG = "Hello".encode()


def erase_range(data: str, lo: int, up: int) -> str:
    return data[lo:up]


def accept_key(key: str) -> str:
    sha1 = hashlib.sha1((key + GUID).encode()).digest()
    return base64.b64encode(sha1).decode()


def _parse(data: bytes) -> dict:
    dt = data.decode('utf-8')
    parsed = dict()
    try:
        dt = removesuffix(dt, '\r\n\r\n')
        keys = dt.split('\r\n')
        protocol = keys[0]
        del keys[0]
        parsed['Protocol'] = protocol
        for key in keys:
            k = key.split(':')[0]
            v = key.split(':')[1].strip()
            parsed[k] = v
        return parsed
    except Exception as ex:
        logging.error(ex)


class Headers(object):
    def __init__(self):
        self.headers = dict()

    def __add__(self, other):
        assert isinstance(other, dict)
        self.headers.update(other)

    def addheader(self, key, value):
        self.headers[key] = value

    def parse(self, data: bytes):
        self.headers = _parse(data=data)

    def keys(self):
        return self.headers.keys()

    def __getitem__(self, key):
        assert isinstance(key, str)
        return self.headers[key]


async def ping(writer: asyncio.StreamWriter):
    logging.debug('In ping...')
    data = b'\x81\x05'
    data += MSG
    writer.write(data)

async def pong(reader: asyncio.StreamReader):
    logging.debug('In pong...')
    data = await reader.read(2 ** 8)
    logging.debug(data)

async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        client_connected = True
        response = Headers()
        data = await reader.read(2 ** 10)
        logging.debug(data)
        response.parse(data)
        key = 'Sec-WebSocket-Key'
        if key in response.keys():
            ws_key = response[key]
            accept = accept_key(ws_key)
            logging.debug(RESPONSE % accept)
            writer.write((RESPONSE % accept).encode())
            while True:
                await ping(writer)
                time.sleep(2)
                await pong(reader)
                time.sleep(4)
        else:
            raise Exception('Malformed header encountered')
    except KeyboardInterrupt as ex:
        logging.debug("Gracefully exiting")


async def server_start():
    logging.debug("Starting server on " + HOST + ":" + str(PORT))
    server = await asyncio.start_server(handle, HOST, PORT, family=socket.AF_INET)
    while True:
        await server.start_serving()


def start():
    asyncio.run(server_start())
