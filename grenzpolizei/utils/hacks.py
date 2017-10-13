import discord


class Hacks:
    def __init__(self):
        pass

    async def is_private(self, channel):
        return isinstance(channel, discord.abc.PrivateChannel)

    async def is_not_private(self, channel):
        return isinstance(channel, discord.abc.GuildChannel)

    async def is_voice(self, channel):
        return isinstance(channel, discord.VoiceChannel)
