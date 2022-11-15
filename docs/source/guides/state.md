# State and parameters

When creating a component, state is stored as arguments and keyword arguments
in the function.

```python
@flare.button(label="Button")
async def button(
    ctx: flare.Context,
    arg: int,
    kwarg: int = 0,
):
    ...
```

You will be forced to supply `arg` in the `button()` method, but `kwarg`
will be optional. The signature of `button()` will be:
```python
def __init__(arg: int, kwarg: int = 0):
    ...
```

When calling `button()`, if you do not provide arguments correctly, type
errors will be raised.

```python
button(1)               # Ok!
button(1, 2)            # Ok!
button(arg=1, kwarg=2)  # Ok!
button()                # Type Error: Missing argument `arg`.
button(1, invalid=5)    # Type Error: `invalid` is not a keyword argument.
```

Required keyword arguments are also supported.

```python
@flare.button(label="Button")
async def button(
    ctx: flare.Context,
    *,
    required_kwarg: int,
):
    ...

button(required_kwarg=10)  # Ok!
button()                   # Type Error
```


# Editing Components

Components can be edited to update state. THe simplist way to edit components
is to create all of them again.

```python
@flare.button(label="Click Me!")
async def button(
    ctx: flare.Context,
    number: int,
) -> None: 
    await ctx.edit_response(
        component=flare.Row(button(number=number+1))
    )
```

There is also a shortcut to return all the rows in the message `flare.Context`
is proxying.

```python
@flare.button(label="Click Me!")
async def button(
    ctx: flare.Context,
    number: int,
) -> None: 
    # Returns all the components that this `ctx` proxies as `typing.Sequence[flare.Row]`.
    rows = ctx.get_components()

    # Print all of the components
    for row in rows:
        for component in components:
            print(component)
```

This list can be modified to change modified to edit components.

```python
@flare.button(label="Click me!")
async def counter_button(
    ctx: flare.Context,
    number: int,
) -> None:
    number += 1

    # Get all the components as a list of rows.
    rows = await ctx.get_components()

    # Edit the values for `counter_button` in the list of
    # rows.
    me = rows[0][0]
    me.number += 1

    await ctx.edit_response(
        content=number,
        # Build all the rows.
        components=await asyncio.gather(*rows),
    )
```
