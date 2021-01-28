import logging
from typing import (
    Callable, Any,
    Coroutine)
from structs import *
import struct
import asyncio
from utils import (decipher_message, ascii_to_str)


def match_opcode(opcode_num: int) -> Opcodes:
    # Pseudo-switch yet again
    num_to_opcode = {0x0: Opcodes.CONT, 0x1: Opcodes.TEXT, 0x2: Opcodes.BINARY,
                     0x8: Opcodes.CONN_CLOSE, 0x9: Opcodes.PING, 0xA: Opcodes.PONG}
    assert opcode_num in num_to_opcode
    return num_to_opcode[opcode_num]


def build_frame(fin: bool, opcode: int, payload_len, payload_data) -> bytes:
    payload_data_fmt = "B" * payload_len
    nibble_0 = (int(fin) << 3)
    nibble_1 = opcode
    byte_0 = (nibble_0 << 4) | nibble_1
    byte_1 = payload_len
    rest = payload_data
    raw_data = struct.pack(f"!BB{payload_data_fmt}", byte_0, byte_1, rest)
    return raw_data


async def decode_frame(read_frame_up_to: Callable[[int], Coroutine[Any, Any, bytes]]):
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
    frame = FrameOpts()
    frame1, frame2, mask = struct.unpack("!BBI", await read_frame_up_to(6))
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
                  'OPCODE': match_opcode(opcode),
                  'HAS_MASK': has_mask,
                  'PAYLOAD_LEN': payload_len})

    if has_mask:
        # Parse mask
        frame.update({'MASK': mask})

    piece = await read_frame_up_to(frame['PAYLOAD_LEN'])
    fmt = "!" + "B" * frame['PAYLOAD_LEN']
    raw_payload_data = struct.unpack(fmt, piece)
    payload_data = ascii_to_str(list(decipher_message(raw_payload_data, frame['MASK'], frame['PAYLOAD_LEN'])))
    frame.update({'PAYLOAD_DATA': payload_data})
    logging.debug(frame)


"""
    Here is an example of decoding the masked message put within a frame
"""


def decode_sample_frame():
    frame = b"\x81\x85\x37\xfa\x21\x3d\x7f\x9f\x4d\x51\x58"
    frame1, mask, frame3, frame4 = struct.unpack("!HIIB", frame)
    """
        struct unpack does not support unpacking of non-powers of two.
        Here is a small walk-around to make 5 byte integer.
        frame3 = 0x7f9f4d51
        frame4 = 0x58
        We need to pad frame3 with two zeros at the end, so that it has the following form: 0x7f9f4d5100. 
        This operation is equivalent to shifting frame3 to the left by factor of 8 bits.
        The only operation left is applying bitwise OR to concatenate transformed frame3 with frame4.
    """
    frame3 = (frame3 << 8) | frame4
    octets = 5
    transformed = decipher_message(frame3, mask, 5)
    print(transformed)
