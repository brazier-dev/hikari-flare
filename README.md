# Flare

Stateless component manager for hikari.


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

    # A planned feature is `ctx.update_state` to update the state of a button.

bot = crescent.Bot("...")
flare.install(bot)

@bot.include
@crescent.command
async def cmd(ctx: crescent.Context, n: int) -> None:
    await ctx.respond(components=[
        # Set custom state here.
        # NOTE: This isn't type safe.
        test_button.build(number=5)
    ])

bot.run()
```
