import server
from utils import removesuffix
import time
from consts import *


def removesuffix_test():
    string = 'somestringhere'
    suffix = 'here'
    string = removesuffix(string, suffix)
    assert string == "somestring"


def print_current_time():
    print(f"Current time is {time.time()}")


if __name__ == '__main__':
    chat_server = server.ChatServer(HOST, PORT)

