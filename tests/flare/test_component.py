from flare.components.base import CallbackComponent


class MockComponent:
    def __init__(self, callback) -> None:
        self.callback = callback

    as_keyword = CallbackComponent.as_keyword


def test_as_keyword_pos_args_only():
    def callback(ctx, a, b, c):
        ...

    assert MockComponent(callback).as_keyword([1, 2, 3], {}) == {
        "a": 1,
        "b": 2,
        "c": 3,
    }


def test_as_keyword_kw_args_only():
    def callback(ctx, a=None, b=None, c=None):
        ...

    assert MockComponent(callback).as_keyword([], {"a": 1, "b": 2, "c": 3,}) == {
        "a": 1,
        "b": 2,
        "c": 3,
    }


def test_as_keyword_single_pos_arg():
    def callback(ctx, a, b, c):
        ...

    assert MockComponent(callback).as_keyword([1], {}) == {
        "a": 1,
    }


def test_as_keyword_kw_and_pos_arg():
    def callback(ctx, a, b=None, c=None):
        ...

    assert MockComponent(callback).as_keyword([1], {"c": 3}) == {
        "a": 1,
        "c": 3,
    }

    assert MockComponent(callback).as_keyword([1], {"b": 2}) == {
        "a": 1,
        "b": 2,
    }
