# Flare

Stateless component manager for hikari with type-safe API.

## Example

```python
import flare
import hikari


class TestButton(flare.Button, label="Test Button"):
    async def callback(self, ctx: flare.Context) -> None:
        await ctx.respond(content="Hello World!")


class StateButton(flare.Button, label="State Button", cookie="Custom Cookie"):
    # state is declared as dataclass fields
    number: int

    async def callback(self, ctx: flare.Context):
        await ctx.respond(content=f"The number is: {self.number}")


bot = hikari.GatewayBot("...")
flare.install(bot)


print("\\" in StateButton._cookie)


@bot.listen()
async def buttons(event: hikari.GuildMessageCreateEvent) -> None:

    # Ignore other bots or webhooks pinging us
    if not event.is_human:
        return

    me = bot.get_me()

    # If the bot is mentioned
    if me.id in event.message.user_mentions_ids:
        # Set custom state for components that need it
        row = await flare.Row(TestButton(), StateButton(5))
        await event.message.respond("Hello Flare!", component=row)


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
