from enum import IntEnum
from typing import TypedDict, Optional


# For more details, see https://tools.ietf.org/html/rfc6455#page-45
class StatusCodes(IntEnum):
    OK = 1000
    GOING_AWAY = 1001
    PROTOCOL_ERR = 1002
    INVALID_DATA = 1003
    RESERVED_0 = 1004
    RESERVED_1 = 1005
    RESERVED_2 = 1006
    TYPE_INCONSISTENCY = 1007
    POLICY_VIOLATION = 1008
    MSG_TOO_BIG = 1009
    NEGOTIATION_ERR = 1010
    UNEXPECTED_COND = 1011
    RESERVED_3 = 1015


class Opcodes(IntEnum):
    CONT = 0x0
    TEXT = 0x1
    BINARY = 0x2
    CONN_CLOSE = 0x8
    PING = 0x9
    PONG = 0xA


class FrameOpts(TypedDict):
    FIN: bool
    RSV1: int
    RSV2: int
    RSV3: int
    OPCODE: Opcodes
    HAS_MASK: bool
    PAYLOAD_LEN: int
    MASK: Optional[int]
    PAYLOAD_DATA: str
