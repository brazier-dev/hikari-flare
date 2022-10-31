import asyncio
import typing as t

import hikari
import hikari.traits

import flare

bot = hikari.GatewayBot("...")
flare.install(bot)


def check_solved(rows: t.MutableSequence[flare.Row]) -> int:
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
        return 1
    if is_win(o):
        return 2

    if x + o == 511:
        return 3

    return False


def disable_all(rows: t.MutableSequence[flare.Row]):
    for row in rows:
        for component in row:
            assert isinstance(component, TicTacToe)
            component.disabled = True


class TicTacToe(flare.Button, label=" "):
    x: int
    y: int

    player_1: hikari.User
    player_2: hikari.User

    turn: bool = False

    async def callback(self, ctx: flare.Context):

        rows = await ctx.get_components()

        for row in rows:
            for component in row:
                assert isinstance(component, TicTacToe)

                component.turn = not component.turn

                if component.x == self.x and component.y == self.y:
                    component.set_label("X" if component.turn else "O").set_disabled(True)

        if num := check_solved(rows):
            if num == 1:
                disable_all(rows)
                await ctx.edit_response(
                    f"{self.player_1.username} wins!",
                    components=await asyncio.gather(*rows),
                )
                return
            elif num == 2:
                disable_all(rows)
                await ctx.edit_response(
                    f"{self.player_2.username} wins!",
                    components=await asyncio.gather(*rows),
                )
                return
            elif num == 3:
                await ctx.edit_response(
                    f"Its a tie!",
                    components=await asyncio.gather(*rows),
                )
                return
        await ctx.edit_response(
            f"{self.player_1.username if self.turn else self.player_2.username}'s Turn",
            components=await asyncio.gather(*rows),
        )


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


flare.add_converter(hikari.User, UserConverter)


@bot.listen()
async def on_message(event: hikari.MessageCreateEvent):
    if not event.is_human:
        return

    me = bot.get_me()

    if not event.message.content:
        return

    if me and me.mention not in event.message.content:
        print("here")
        return

    _, opponent_id = event.message.content.split(" ")

    opponent = await bot.rest.fetch_user(hikari.Snowflake(opponent_id[2:-1]))

    def get_tac(x: int, y: int) -> TicTacToe:
        return TicTacToe(x, y, event.message.author, opponent)

    await event.message.respond(
        f"{event.message.author}'s Turn",
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