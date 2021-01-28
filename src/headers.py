import logging
from utils import removesuffix
from typing import Dict, Any


class Headers(object):
    def __init__(self):
        self.headers = dict()

    def addheader(self, key, value) -> None:
        self.headers[key] = value

    @staticmethod
    def _parse_method_and_protocol(header_str: str) -> tuple:
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

    def parse(self, data: bytes) -> None:
        dt = data.decode('utf-8')
        try:
            dt = removesuffix(dt, '\r\n\r\n')
            keys = dt.split('\r\n')
            has_query_params, method, params, protocol = self._parse_method_and_protocol(keys[0])
            self.headers.update({
                'Has-Query-Params': has_query_params,
                'Method': method,
                'Params': params,
                'Protocol': protocol
            })
            del keys[0]
            for key in keys:
                k = key.split(':')[0].strip()
                v = key.split(':')[1].strip()
                self.headers[k] = v
        except Exception as ex:
            logging.error(ex)

    @property
    def keys(self) -> None:
        return self.headers.keys()

    def __getitem__(self, key) -> None:
        assert isinstance(key, str)
        return self.headers[key]

    def __add__(self, other) -> None:
        assert isinstance(other, dict)
        self.headers.update(other)
