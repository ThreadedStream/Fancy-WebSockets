import logging
from enum import IntEnum
from typing import (
    TypedDict, Optional,
    Callable, Any,
    Coroutine)
import struct


class Opcodes(IntEnum):
    CONT = 0x0
    TEXT = 0x1
    BINARY = 0x2
    CONN_CLOSE = 0x8
    PING = 0x9
    PONG = 0xA


class Frame(TypedDict):
    FIN: bool
    RSV1: int
    RSV2: int
    RSV3: int
    OPCODE: str
    HAS_MASK: bool
    PAYLOAD_LEN: int
    MASK: Optional[int]
    PAYLOAD_DATA: str


async def decode_frame(read_frame_up_to: Callable[[int], Coroutine[Any, Any, bytes]]):
    frame_piece = await read_frame_up_to(6)
    """
        Say, server has received frame of such form:
        \x81\x8d\
        
        struct.unpack() with "!BB" format option splits this frame 
        piece into two additional pieces, namely, 0x81 and 0x8d
        Afterwards, we need to convert first piece into binary representation
        In our case, 0x81 has the following binary equivalent:
        '10000001'.
        '00001111'
        First bit signifies a fin bit and it equals 1, so to tell the server 
        that the whole message was sent
        Subsequent 3 bits signify rsv bits. In majority of cases, these bits should be equal zero.
        Last four bits signify opcode. In our case, the text opcode was meant.
    """
    frame = Frame()
    frame1, frame2, frame3 = struct.unpack("!BBI", frame_piece)
    # Parsing first 8 bits
    fin = True if frame1 & 0x80 else False
    rsv1 = True if frame1 & 0x40 else False
    rsv2 = True if frame1 & 0x20 else False
    rsv3 = True if frame1 & 0x10 else False
    opcode = frame1 & 0x0F
    # Parsing second 8 bits
    has_mask = True if frame2 & 0x80 else False
    payload_len = frame2 & 0x7F
    frame.update({'FIN': fin, 'RSV1': rsv1,
                  'RSV2': rsv2, 'RSV3': rsv3,
                  'OPCODE': bin(opcode),
                  'HAS_MASK': has_mask,
                  'PAYLOAD_LEN': payload_len})

    if has_mask:
        # Parse mask
        frame.update({'MASK': frame3})

    logging.debug(frame)
