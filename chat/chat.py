from src.server import Server
from typing import Dict, Tuple, List
import asyncio
from src.headers import Headers
from queue import Queue
import logging
from src.utils import *
from src.consts import *
from src.frame import decode_frame, build_frame


class ChatServer(Server):
    def __init__(self, host: str, port: int, init_and_activate: bool = True):
        super(ChatServer, self).__init__(host, port)
        self.users = Dict[str, Tuple[asyncio.StreamReader, asyncio.StreamWriter]]
        self.message_buffer = Queue(2 ** 10)
        if init_and_activate:
            super().start()

    async def callback(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            response = Headers()
            data = await reader.read(2 ** 10)
            logging.debug(data)
            response.parse(data)
            if response['Has-Query-Params']:
                user_id = extract_params(response['Params'])
                self.users.update({user_id: (reader, writer)})
            key = 'Sec-WebSocket-Key'
            if key in response.keys:
                ws_key = response[key]
                accept = accept_key(ws_key)
                logging.debug(RESPONSE % accept)
                writer.write((RESPONSE % accept).encode())
                await self.pingpongs(reader, writer)
            else:
                raise Exception('Malformed header encountered')
        except KeyboardInterrupt as ex:
            logging.debug("Gracefully exiting")

    async def ping(self, writer: asyncio.StreamWriter):
        if not self.message_buffer.empty():
            item = self.message_buffer.get()
            # Message delivery goes here
            #writer.write(data)

    async def pong(self, reader: asyncio.StreamReader):
        frame = await decode_frame(reader.readexactly)
        self.message_buffer.put(item=frame)

    async def pingpongs(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        await self.ping(writer)
        await self.pong(reader)
        await asyncio.sleep(5)
        await self.pingpongs(reader, writer)
