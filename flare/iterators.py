import builtins
import typing as t

__all__: t.Sequence[str] = (
    "enumerate",
    "flatten",
)

T = t.TypeVar("T")


def enumerate(array: t.Iterable[t.Iterable[T]]) -> t.Iterable[tuple[int, int, T]]:
    """
    Enumerates and flattens 2d array. This function can be used to iterate through a messages
    components and the row and column number of each component.

    .. code-block:: python

        components = await ctx.get_components()

        # `row` is the x coordinate.
        # `column` is the y coordinate.

        async for row, column, component in flare.enumerate(components):
            ...
    """
    for row_number, row in builtins.enumerate(array):
        for column_number, component in builtins.enumerate(row):
            yield (row_number, column_number, component)


def flatten(array: t.Iterable[t.Iterable[T]]) -> t.Iterable[T]:
    """
    Flattens a 2d array. This can be used to iterate through all components in a message
    in a single for loop.

    .. code-block:: python

        components = await ctx.get_components()

        async for component in falre.flatten(components):
            ...
    """
    for row in array:
        for component in row:
            yield component
