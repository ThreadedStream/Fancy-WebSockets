import server
from utils import removesuffix


def removesuffix_test():
    string = 'somestringhere'
    suffix = 'here'
    string = removesuffix(string, suffix)
    assert string == "somestring"


if __name__ == '__main__':
    server.start()
