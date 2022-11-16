import asyncio

import hikari
import hikari.traits

import flare

bot = hikari.GatewayBot("...")
flare.install(bot)


@flare.button(label="Test Button", style=hikari.ButtonStyle.PRIMARY)
async def test_button(
    ctx: flare.Context,
) -> None:
    await ctx.respond(content="Hello World!")


@flare.button(label="Click me!")
async def counter_button(
    ctx: flare.Context,
    # The argument `n` is saved as the state. This argument defaults to 0 if no
    # value is specified in `counter_button()`.
    n: int = 0,
) -> None:
    components = await ctx.get_components()
    components[0][0] = counter_button(n + 1).set_label(f"Clicked {n+1} Times.")

    await ctx.edit_response(components=await asyncio.gather(*components))


@flare.select(
    placeholder="Select an Option",
    options=[
        "Option 1",
        "Option 2",
        "Option 3",
    ],
)
async def select_menu(ctx: flare.Context, hidden_value: int):
    await ctx.respond(
        # fmt: off
        f"The selected value is: {ctx.values[0]}"
        f"\nThe hidden number is: {hidden_value}"
        # fmt: on
    )

@bot.listen()
async def on_message(event: hikari.MessageCreateEvent):
    if event.message.author.is_bot or not event.message.content:
        return

    me = bot.get_me()

    # If the bot is mentioned
    if me.id in event.message.user_mentions_ids:
        await event.message.respond(
            # When responding to the interaction, use the default values.
            components=await asyncio.gather(
                flare.Row(counter_button(0)),
                flare.Row(select_menu(15)),
            )
        )


bot.run()
