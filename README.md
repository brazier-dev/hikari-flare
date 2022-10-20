# Flare

Stateless component manager for hikari with type-safe API.


# Example
Example with crescent cause im lazy

```python
import hikari
import crescent
import flare


@flare.button(label="Test Button", style=hikari.ButtonStyle.PRIMARY)
async def test_button(
    ctx: flare.Context,
    # Kwargs are used for state.
    number: int | None = None
) -> None:
    print(number)
    await ctx.interaction.create_initial_response(
        content=f"The number is: {number}",
        response_type=hikari.ResponseType.MESSAGE_CREATE
    )

bot = crescent.Bot("...")
flare.install(bot)

@bot.include
@crescent.command
async def cmd(ctx: crescent.Context, n: int) -> None:
    await ctx.respond(components=[
        # Set custom state here.
        test_button.build(number=5)
    ])

bot.run()
```

## Converters

Converters allow you to serialize and deserialize types.
Here in an example of an int converter.

Converters for `int`, `str`, `typing.Literal`, and `enum.Enum` are built in.

```python
class IntConverter(Converter[int]):
    def to_str(self, obj: int) -> str:
        return str(obj)

    def from_str(self, obj: str) -> int:
        return int(obj)

flare.add_converter(
    int,          # The typehint this converter is used for.
    IntConverter  # The converter class.
)
```
