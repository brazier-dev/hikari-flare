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

You will be forced to supply `arg` in the `button.set()` method, but `kwarg`
will be optional. The signature of `button.set()` will be:
```python
def set(arg: int, kwarg: int = 0):
    ...
```

When calling `button.set()`, if you do not provide arguments correctly, type
errors will be raised.

```python
button.set(1)               # Ok!
button.set(1, 2)            # Ok!
button.set(arg=1, kwarg=2)  # Ok!
button.set()                # Type Error: Missing argument `arg`.
button.set(1, invalid=5)    # Type Error: `invalid` is not a keyword argument.
```

```{warning}
Mypy [does not support](https://github.com/python/mypy/issues/13403) this typing.
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

button.set(required_kwarg=10)  # Ok!
button.set()                   # Type Error
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
    print(number)
    await ctx.edit_response(
        component=flare.Row(button.set(number=number+1))
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

```{note}
`component.set()` clones components. It does not modify them in place.
```

A helper method is also provided to help edit components.

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
    counter_button.set_in(rows, number=number)

    await ctx.edit_response(
        content=number,
        # Build all the rows.
        components=await asyncio.gather(*rows),
    )
```
