def removesuffix(string: str, suffix: str) -> str:
    pos = string.find(suffix)
    if pos != -1:
        string = string[0:pos]
    else:
        raise ValueError('suffix is not present in passed string')
    return string

