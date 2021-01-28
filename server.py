import socket
import asyncio
import threading
from typing import Dict, Set
from utils import *
from frame import *
import logging

HOST = "127.0.0.1"
PORT = 4560

logging.getLogger().setLevel(logging.DEBUG)

RESPONSE = 'HTTP/1.1 101 Switching Protocols\r\n' \
           'Upgrade: websocket\r\n' \
           'Connection: Upgrade\r\n' \
           'Sec-WebSocket-Accept: %s\r\n\r\n'
MSG = "Hello".encode()
users = Dict[str, Set]


class Headers(object):
    def __init__(self):
        self.headers = dict()

    def __add__(self, other):
        assert isinstance(other, dict)
        self.headers.update(other)

    def addheader(self, key, value):
        self.headers[key] = value

    def parse(self, data: bytes):
        self.headers = parse(data=data)

    def keys(self):
        return self.headers.keys()

    def __getitem__(self, key):
        assert isinstance(key, str)
        return self.headers[key]


async def ping(writer: asyncio.StreamWriter):
    logging.debug('In ping...')
    data = b'\x8a\x05'
    data += MSG
    writer.write(data)


async def pong(reader: asyncio.StreamReader):
    logging.debug('In pong...')
    await decode_frame(reader.readexactly, reader)


async def pingponging(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    await ping(writer)
    await pong(reader)
    await asyncio.sleep(5)
    await pingponging(reader, writer)

    asyncio.get_event_loop().call_later(10, pong, (writer,))


async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        response = Headers()
        data = await reader.read(2 ** 10)
        logging.debug(data)
        response.parse(data)
        if response['Has-Query-Params']:
            user_id = extract_params(response['Params'])
            users.update({user_id: (reader, writer)})
        key = 'Sec-WebSocket-Key'
        if key in response.keys():
            ws_key = response[key]
            accept = accept_key(ws_key)
            logging.debug(RESPONSE % accept)
            writer.write((RESPONSE % accept).encode())
            await pingponging(reader, writer)
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
