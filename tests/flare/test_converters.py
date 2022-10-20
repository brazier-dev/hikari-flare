import typing
from flare.converters import _get_left, _is_union

def test_get_left():
    assert _get_left(int | str) is int
    assert _get_left(typing.Union[int, str]) is int

def test_is_union():
    assert _is_union(int | str)
    assert _is_union(typing.Union[int, str])
    assert not _is_union(int)
