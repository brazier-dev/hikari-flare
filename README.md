# Flare

Stateless component manager for hikari with type-safe API.

## Example

```python
import flare
import hikari


@flare.button(label="Test Button", style=hikari.ButtonStyle.PRIMARY)
async def test_button(
    ctx: flare.Context,
) -> None:
    await ctx.respond(content="Hello World!")

@flare.button(label="State Button", style=hikari.ButtonStyle.PRIMARY)
async def state_button(
    ctx: flare.Context,
    # Args and kwargs are used for state.
    number: int,
) -> None:
    await ctx.respond(content=f"The number is: {number}")

bot = hikari.GatewayBot("...")
flare.install(bot)

@bot.listen()
async def buttons(event: hikari.GuildMessageCreateEvent) -> None:

    # Ignore other bots or webhooks pinging us
    if not event.is_human:
        return

    me = bot.get_me()

    # If the bot is mentioned
    if me.id in event.message.user_mentions_ids:
        # Set custom state for components that need it
        row = await flare.Row(test_button(), state_button(5))
        message = await event.message.respond("Hello Flare!", component=row)

bot.run()
```

The API can also be accessed at a lower level if components need typed attributes.

```python
class Button(flare.Button):
    a: int
    b: str

    async def callback(self, ctx: flare.Context) -> None:
        typing_extensions.reveal_type(self.a)  # int
        typing_extensions.reveal_type(self.b)  # str
        await ctx.respond("Hello flare!")
```

## Converters

Converters allow you to serialize and deserialize types.
Here in an example of an int converter.

Converters for `int`, `str`, `typing.Literal`, and `enum.Enum` are built in.

```python
class IntConverter(Converter[int]):
    async def to_str(self, obj: int) -> str:
        return str(obj)

    async def from_str(self, obj: str) -> int:
        return int(obj)

flare.add_converter(
    int,          # The typehint this converter is used for.
    IntConverter  # The converter class.
)
```
