from PIL import Image, ImageDraw, ImageFont

from core.i18n import CogI18n
import time
import textwrap

import discord

import os

_ = CogI18n("Spoilers", __file__)


class Spoilers:
    def __init__(self, bot):
        self.bot = bot

    async def _make_gif(self, spoiler_text):
        limit = 50
        background = (54, 57, 62)
        y_text = 0
        line_height = 20
        max_width = 410
        font_size = 16

        spoiler_text = textwrap.wrap(spoiler_text, width=limit)
        width, height = (max_width, len(spoiler_text) * line_height)

        spoiler_warning_image = Image.new("RGBA", (width, height), background)
        spoiler_text_image = Image.new("RGBA", (width, height), background)

        spoiler_warning_draw = ImageDraw.Draw(spoiler_warning_image)
        spoiler_text_draw = ImageDraw.Draw(spoiler_text_image)

        font = ImageFont.truetype("cogs/spoilers/font/SourceSansPro-Regular.ttf", font_size)

        spoiler_warning = "( hover to reveal spoiler )"
        spoiler_warning_draw.text((0, 0), spoiler_warning, font=font)

        for line in spoiler_text:
            spoiler_text_draw.text((0, y_text), line, font=font)
            y_text += line_height

        filename = "{}.gif".format(str(time.time()).split(".")[0])
        spoiler_warning_image.save(filename, save_all=True, append_images=[spoiler_text_image], loop=1, duration=1000)

        return filename

    async def on_message(self, message):
        author = message.author
        content = message.clean_content
        channel = message.channel
        if author.id != self.bot.user.id:
            if content.startswith(">>>"):
                spoiler_text = content[3:]
                try:
                    await message.delete()
                except:
                    pass
                image = await self._make_gif(spoiler_text)
                await channel.send("{0.mention} hid the following spoiler:".format(author), file=discord.File(image))
                os.remove(image)
