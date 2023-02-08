import asyncio

import hikari
import hikari.traits

import flare

bot = hikari.GatewayBot("...")
flare.install(bot)


@flare.button(label="Test Button", style=hikari.ButtonStyle.PRIMARY)
async def test_button(
    ctx: flare.MessageContext,
) -> None:
    await ctx.respond(content="Hello World!")


@flare.button(label="Click me!")
async def counter_button(
    ctx: flare.MessageContext,
    # The argument `n` is saved as the state. This argument defaults to 0 if no
    # value is specified in `counter_button()`.
    n: int = 0,
) -> None:
    components = await ctx.get_components()
    # `counter_button` is row 0, coulumn 0.
    components[0][0] = counter_button(n + 1).set_label(f"Clicked {n+1} Times.")

    await ctx.edit_response(components=await asyncio.gather(*components))


@flare.text_select(
    placeholder="Select an Option",
    options=[
        "Option 1",
        "Option 2",
        hikari.SelectMenuOption(label="Option 3", value="Option 3", description=None, emoji=None, is_default=False),
    ],
)
async def select_menu(ctx: flare.MessageContext, hidden_value: int):
    await ctx.respond(
        # fmt: off
        # `ctx.values` is an array of all values the user selected.
        f"The selected value is: {ctx.values[0]}"
        f"\nThe hidden number is: {hidden_value}"
        # fmt: on
    )


# There are a few more select types that can be used.
# Parameters can also be provided like the text slect menu type.
@flare.user_select()
async def user_select(ctx: flare.MessageContext):
    # The users that the user selected.
    ctx.users


@flare.role_select()
async def role_select(ctx: flare.MessageContext):
    # The roles that the user selected.
    ctx.roles


@flare.mentionable_select()
async def mentionable_select(ctx: flare.MessageContext):
    # The users that the user selected.
    ctx.users
    # The roles that the user selected.
    ctx.roles
    # All mentionables that the user selected.
    ctx.mentionables


# Optionally channel types can be provided. In this example only `GUILD_TEXT`
# channels will be selectable.
@flare.channel_select(channel_types=[hikari.ChannelType.GUILD_TEXT])
async def channel_select(ctx: flare.MessageContext):
    # The channels that the user selected.
    ctx.channels


# On message command thats triggered by typing `@<BOT>`
@bot.listen()
async def on_message(event: hikari.MessageCreateEvent):
    if event.message.author.is_bot or not event.message.content:
        return

    me = bot.get_me()

    # If the bot is mentioned
    if me.id in event.message.user_mentions_ids:
        await event.message.respond(
            components=await asyncio.gather(
                flare.Row(counter_button(0)),
                flare.Row(select_menu(15)),
            )
        )


bot.run()
