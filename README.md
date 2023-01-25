# Flare

A stateless component manager for hikari with a type-safe API.

### Features:
- buttons, select menus, and modals
- easy and powerful API for simple interactions
- saves data between bot restarts by utilizing the component's custom id 

*If you want to create complex component interactions [hikari-miru](https://github.com/HyperGH/hikari-miru) may be a better choice.*


### Installation

```sh
pip install hikari-flare
```

### Links
> 🗃️ | [Docs](https://brazier-dev.github.io/hikari-flare)<br>
> 📦 | [Pypi](https://pypi.org/project/hikari-flare/)

## Example

```python
import flare
import hikari


@flare.button(label="Test Button", style=hikari.ButtonStyle.PRIMARY)
async def test_button(
    ctx: flare.MessageContext,
) -> None:
    await ctx.respond(content="Hello World!")

@flare.button(label="State Button", style=hikari.ButtonStyle.PRIMARY)
async def state_button(
    ctx: flare.MessageContext,
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
