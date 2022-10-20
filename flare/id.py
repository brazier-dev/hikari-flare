import typing


def serialize(cookie: str, types: dict[str, typing.Any], kwargs: dict[str, typing.Any]) -> str:
    out = f"{cookie}:"

    for k in types.keys():
        out += f"{str(kwargs.get(k, 'NULL'))}:"

    return out[:-1]

def deserialize(id: str, map: dict[str, typing.Any]) -> tuple[str, dict[str, typing.Any]]:
    cookie, *args = id.split(":")

    types = map[cookie].args

    transformed_args = {}

    for k, arg in zip(types.keys(), args):
        if arg != "NULL":
            transformed_args[k] = arg

    return (cookie, transformed_args)
