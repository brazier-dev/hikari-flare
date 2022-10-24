# Getting Started

## Installation

flare can be installed using pip via the following command:

``$ python3 -m pip install -U hikari-flare``

## First steps

How about the typical example from webdev with a counter button?

```python
import hikari

bot = hikari.GatewayBot("TOKEN")

@flare.button(label="Click me!")
async def counter_button(
    ctx: flare.Context,
    # The argument `n` is saved as the state. This argument defaults to 0 if no
    # value is specified in `counter_button.set()` or `counter_button.set()` is
    # not used.
    n: int = 0,
) -> None:
    n += 1
    await ctx.edit_response(
        f"The button was pressed {n} times.",
        # The components are edited to update the state.
        component=flare.Row(counter_button.set(n=n))
    )


@bot.listen()
async def on_message(event: hikari.MessageCreateEvent):
    if event.message.author.is_bot or not event.message.content:
        return

    me = bot.get_me()

    # If the bot is mentioned
    if me.id in event.message.user_mentions_ids:
        await event.message.respond(
            "The button was pressed 0 times.",
            # When responding to the interaction, use the default values.
            component=flare.Row(counter_button)
        )
```
