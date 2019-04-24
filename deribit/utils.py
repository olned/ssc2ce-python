import re


def resolve_route(value, routes):
    key, handler = None, None
    for key, handler in routes:
        if key and re.match(key, value):
            return handler

    if key is not None and key == "" and handler:
        return handler
