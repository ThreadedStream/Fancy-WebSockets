import socket
from typing import Dict, Tuple
from headers import Headers
from utils import *
from frame import *
import logging
from consts import *

logging.getLogger().setLevel(logging.DEBUG)


class Server(object):
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    # Synopsis: Non-async wrapper for _server_start
    def start(self):
        asyncio.run(self._server_start())

    # Synopsis: Async function to start a server
    async def _server_start(self):
        logging.debug("Starting server on " + self.host + ":" + str(self.port))
        server = await asyncio.start_server(self.callback, self.host, self.port, family=socket.AF_INET)
        await server.serve_forever()

    # Must be overridden
    async def callback(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        raise NotImplementedError

    # Must be overridden for proper functioning
    async def ping(self, writer: asyncio.StreamWriter) -> None:
        raise NotImplementedError

    # Must be overridden for proper functioning
    async def pong(self, reader: asyncio.StreamReader) -> None:
        raise NotImplementedError

    # Can be overridden
    async def pingpongs(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        await self.pong(reader)
        await self.ping(writer)


class DummyServer(Server):
    def __init__(self, host: str, port: int, init_and_activate: bool = True):
        super(DummyServer, self).__init__(host, port)
        if init_and_activate:
            super().start()

    async def callback(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        await super().pingpongs(reader, writer)

    async def ping(self, writer: asyncio.StreamWriter) -> None:
        logging.debug("In ping...")
        data = b'\x8a\x05'
        message = "Hello".encode()
        data += message

    async def pong(self, reader: asyncio.StreamReader) -> None:
        logging.debug("In pong...")
        logging.debug(await reader.read())


