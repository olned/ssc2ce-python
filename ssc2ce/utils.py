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


def hide_secret(request):
    data = request.copy()
    hidden_keys = ["password", "username", "client_id", "client_secret", "refresh_token", "access_token"]

    for key, value in data.items():
        if isinstance(value, dict):
            data[key] = hide_secret(value)
        elif key in hidden_keys:
            data[key] = "***"

    return data


class IntId:
    id = 0

    def get_id(self):
        self.id += 1
        return self.id
