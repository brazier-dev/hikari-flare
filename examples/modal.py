import hikari

import flare

bot = hikari.GatewayBot("...")
flare.install(bot)


class ModalTest(flare.Modal, title="My Title"):
    # Values to save
    a: int
    b: str = "1234"

    # Your text inputs
    text_input: flare.TextInput = flare.TextInput(label="Test label")
    text_input_2: flare.TextInput = flare.TextInput(label="Test label 2")

    async def callback(self, ctx: flare.ModalContext) -> None:
        # You can access text inputs with `self.text_input`.
        # These will be the first two cells in `ctx.values`.
        print(self.text_input.value)
        print(self.text_input_2.value)

        # Access all text input values in an array.
        print(ctx.values)

        await ctx.respond(f"{self.text_input.value, self.text_input_2.value}")


# Function that has `interaction` as an arg.This represents a result from your command handler.
async def magic_entrypoint(interaction: hikari.CommandInteraction | hikari.ComponentInteraction):
    modal = ModalTest(5)
    await modal.send(interaction)


bot.run()
