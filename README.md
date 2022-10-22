# Flare

Stateless component manager for hikari with type-safe API.

## Example

```python
import hikari
import flare


@flare.button(label="Test Button", style=hikari.ButtonStyle.PRIMARY)
async def test_button(
    ctx: flare.Context,
) -> None:
    await ctx.interaction.create_initial_response(
        content="Hello World!",
        response_type=hikari.ResponseType.MESSAGE_CREATE
    )

@flare.button(label="State Button", style=hikari.ButtonStyle.PRIMARY)
async def state_button(
    ctx: flare.Context,
    # Kwargs are used for state.
    number: int | None = None
) -> None:
    print(number)
    await ctx.interaction.create_initial_response(
        content=f"The number is: {number}",
        response_type=hikari.ResponseType.MESSAGE_CREATE
    )

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
        row = flare.Row(test_button, state_button.set(number=5))
        message = await event.message.respond("Hello Flare!", component=row)

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
