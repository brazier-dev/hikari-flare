import asyncio
import enum
import typing as t

import hikari
import hikari.traits

import flare

bot = hikari.GatewayBot("...")
flare.install(bot)


class CheckSolvedResult(enum.IntEnum):
    NOTHING = enum.auto()
    PLAYER1 = enum.auto()
    PLAYER2 = enum.auto()
    TIE = enum.auto()


# An algorythm to check if the game is solved.
def check_solved(rows: t.MutableSequence[flare.Row]) -> CheckSolvedResult:
    x = 0
    o = 0

    # fmt: off
    ns = [
        1, 2, 4,
        8, 16, 32,
        64, 128, 256
    ]
    # fmt: on

    loc = 0
    for row in rows:
        for component in row:
            assert isinstance(component, TicTacToe)

            if component.label == "X":
                x += ns[loc]
            elif component.label == "O":
                o += ns[loc]

            loc += 1

    wins = {7, 56, 448, 73, 146, 292, 273, 84}

    def is_win(num: int) -> bool:
        for win in wins:
            if num & win == win:
                return True
        return False

    if is_win(x):
        return CheckSolvedResult.PLAYER1
    if is_win(o):
        return CheckSolvedResult.PLAYER2

    if x + o == 511:
        return CheckSolvedResult.TIE

    return CheckSolvedResult.NOTHING


def disable_all(rows: t.MutableSequence[flare.Row]):
    for row in rows:
        for component in row:
            assert isinstance(component, TicTacToe)
            component.disabled = True


class TicTacToe(flare.Button, label=" "):
    # The column of this component.
    x: int
    # The row of this component.
    y: int

    # Player 1
    player_1: hikari.User
    # Player 2
    player_2: hikari.User

    # A bool to keep track of the turn.
    turn: bool = False

    async def callback(self, ctx: flare.MessageContext):

        rows = await ctx.get_components()

        if ctx.author != (self.player_1 if self.turn else self.player_2):
            await ctx.respond("You can't play! It is not your turn.", flags=hikari.MessageFlag.EPHEMERAL)
            return

        # Iterate through the components to find the one that caused the event.
        for row in rows:
            for component in row:
                # This is safe because only `TicTacToe` buttons are used in the message.
                assert isinstance(component, TicTacToe)

                # Only set the component label if it is the one that caused the event.
                if component.x == self.x and component.y == self.y:
                    component.set_label("X" if component.turn else "O").set_disabled(True)

                component.turn = not component.turn

        res = check_solved(rows)
        if res == CheckSolvedResult.NOTHING:
            content = f"{self.player_2.mention if self.turn else self.player_1.mention}'s Turn"
        elif res == CheckSolvedResult.PLAYER1:
            disable_all(rows)
            content = f"{self.player_1.mention} wins!"
        elif res == CheckSolvedResult.PLAYER2:
            disable_all(rows)
            content = f"{self.player_2.mention} wins!"
        else:
            await ctx.edit_response(
                f"Its a tie!",
                components=await asyncio.gather(*rows),
            )
            return

        await ctx.edit_response(
            content,
            # The components must be awaited to update their custom id's.
            components=await asyncio.gather(*rows),
        )


# This is a converter for `hikari.User`. It allows `hikari.User`
# to be used as a type hint.
class UserConverter(flare.Converter[hikari.User]):
    async def to_str(self, obj: hikari.User) -> str:
        return str(hikari.Snowflake(obj))

    async def from_str(self, obj: str) -> hikari.User:
        snowflake = hikari.Snowflake(obj)

        if isinstance(self.app, hikari.traits.CacheAware):
            if user := self.app.cache.get_user(snowflake):
                return user

        if isinstance(self.app, hikari.traits.RESTAware):
            return await self.app.rest.fetch_user(snowflake)

        raise Exception("Could not fetch user. Bot is not `RESTAware` and user is not cached.")


# Remember to add the converter to flare! Otherwise it will not work.
flare.add_converter(hikari.User, UserConverter)


# On message command thats triggered by typing `@<BOT> @<OPPONENT>`
@bot.listen()
async def on_message(event: hikari.MessageCreateEvent):
    if not event.is_human:
        return

    me = bot.get_me()

    if not event.message.content:
        return

    if me and me.mention not in event.message.content:
        return

    _, opponent_id = event.message.content.split(" ")

    opponent = await bot.rest.fetch_user(hikari.Snowflake(opponent_id[2:-1]))

    def get_tac(x: int, y: int) -> TicTacToe:
        return TicTacToe(x, y, event.message.author, opponent)

    # The bot replies with a 3x3 of message components.
    await event.message.respond(
        f"{event.message.author.mention}'s Turn",
        components=await asyncio.gather(
            flare.Row(
                get_tac(0, 0),
                get_tac(1, 0),
                get_tac(2, 0),
            ),
            flare.Row(
                get_tac(0, 1),
                get_tac(1, 1),
                get_tac(2, 1),
            ),
            flare.Row(
                get_tac(0, 2),
                get_tac(1, 2),
                get_tac(2, 2),
            ),
        ),
    )


bot.run()
