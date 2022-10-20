import typing


SEP = "\x01"
ESC = "\\"
ESC_SEP = "\\\x01"
NULL = "\x00"
ESC_NULL = "\\\x00"

def serialize(cookie: str, types: dict[str, typing.Any], kwargs: dict[str, typing.Any]) -> str:
    out = f"{cookie}{SEP}"

    for k in types.keys():
        out += f"{str(kwargs.get(k, NULL)).replace(SEP, ESC_SEP)}{SEP}"

    return out[:-1]

def split_on_sep(s: str) -> list[str]:
    out: list[list[str]] = [[s[0]]]

    for last, char in zip(s[:-1], s[1:]):
        if last != ESC and char == SEP:
            out.append([])
        else:
            out[-1] += [char]

    return [''.join(row).replace(ESC_SEP, SEP) for row in out]

def deserialize(id: str, map: dict[str, typing.Any]) -> tuple[str, dict[str, typing.Any]]:
    cookie, *args = split_on_sep(id)

    types = map[cookie].args

    transformed_args: dict[str, typing.Any] = {}

    for k, arg in zip(types.keys(), args):
        if arg != NULL:
            arg = arg.replace(ESC_NULL, NULL)
            transformed_args[k] = arg

    return (cookie, transformed_args)
