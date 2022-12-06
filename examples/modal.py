import hikari

import flare

bot = hikari.GatewayBot("...")
flare.install(bot)


class ModalTest(flare.Modal, title="My Title"):
    text_input: flare.TextInput = flare.TextInput(label="Test label")
    text_input_2: flare.TextInput = flare.TextInput(label="Test label 2")

    async def callback(self, ctx: flare.ModalContext) -> None:
        # You can access text inputs with `self.text_input`
        print(self.text_input.value)
        print(self.text_input_2.value)

        # Access all text input values in an array.
        print(ctx.values)

        await ctx.respond(f"{self.text_input.value, self.text_input_2.value}")


# Function that has `interaction` as an arg.This represents a result from your command handler.
async def magic_function(interaction: hikari.ModalResponseMixin):
    modal = ModalTest()
    await modal.send(interaction)


bot.run()
