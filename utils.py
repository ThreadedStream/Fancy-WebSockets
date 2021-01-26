"""
    Set of utilities used by websocket server module
"""
import hashlib
import base64
import logging

GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'


def removesuffix(string: str, suffix: str) -> str:
    pos = string.find(suffix)
    if pos != -1:
        string = string[0:pos]
    else:
        raise ValueError('suffix is not present in passed string')
    return string


def erase_range(data: str, lo: int, up: int) -> str:
    return data[lo:up]


def extract_params(params: str) -> str:
    qmark_pos = params.find('?')
    if qmark_pos != -1:
        user_id = params[qmark_pos:len(params)].strip().split('=')[1]
        return user_id
    else:
        raise Exception('Make sure that request parameters are not empty')


def accept_key(key: str) -> str:
    sha1 = hashlib.sha1((key + GUID).encode()).digest()
    return base64.b64encode(sha1).decode()


def parse_method_and_protocol(header_str: str) -> tuple:
    has_query_params = False
    tokens = header_str.split(' ')
    if len(tokens) > 2:
        has_query_params = True
        method = tokens[0].strip()
        params = tokens[1].strip()
        protocol = tokens[2].strip()
    elif len(tokens) == 2:
        method = tokens[0].strip()
        params = None
        protocol = tokens[1].strip()
    else:
        raise Exception("Header string is empty")

    return has_query_params, method, params, protocol


def parse(data: bytes) -> dict:
    dt = data.decode('utf-8')
    parsed = dict()
    try:
        dt = removesuffix(dt, '\r\n\r\n')
        keys = dt.split('\r\n')
        has_query_params, method, params, protocol = parse_method_and_protocol(keys[0])
        parsed['Has-Query-Params'] = has_query_params
        parsed['Method'] = method
        parsed['Params'] = params
        parsed['Protocol'] = protocol
        del keys[0]
        for key in keys:
            k = key.split(':')[0]
            v = key.split(':')[1].strip()
            parsed[k] = v
        return parsed
    except Exception as ex:
        logging.error(ex)
