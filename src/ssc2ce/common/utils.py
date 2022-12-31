import re
from typing import Pattern


def resolve_route(value, routes):
    key, handler = None, None
    for key, handler in routes:
        if key:
            if isinstance(key, str):
                if key == value:
                    return handler
            elif isinstance(key, Pattern) and re.match(key, value):
                return handler

    if key is not None and key == "" and handler:
        return handler


class IntId:
    def __init__(self):
        self.id = 0

    def get_id(self):
        self.id += 1
        return self.id
