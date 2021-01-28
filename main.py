import server
from utils import removesuffix
import time
import frame
import threading


def removesuffix_test():
    string = 'somestringhere'
    suffix = 'here'
    string = removesuffix(string, suffix)
    assert string == "somestring"


def print_current_time():
    print(f"Current time is {time.time()}")


if __name__ == '__main__':
    server.start()
