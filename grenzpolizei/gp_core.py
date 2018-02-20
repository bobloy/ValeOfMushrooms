import aiohttp
import inspect
import discord
import json

from gp_setup import GrenzpolizeiSetup
from redbot.core import Config


class GrenzpolizeiCore:
    def __init__(self, bot):
        self.bot = bot

        self.config = Config.get_conf(
            self, identifier=78631113035100160, force_registration=True)
        self.config.register_global(settings={})
        self.bot.loop.create_task(self.load_settings())

        self.event_channels = ['member_event_channel', 'message_event_channel', 'guild_event_channel', 'mod_event_channel']

        self.event_types = {}

        self.event_types["on_member_update"] = "member_event_channel"
        self.event_types["on_voice_state_update"] = "member_event_channel"

        self.event_types["on_message_edit"] = "message_event_channel"
        self.event_types["on_message_delete"] = "message_event_channel"
        self.event_types["on_raw_bulk_message_delete"] = "guild_event_channel"

        self.event_types["on_guild_channel_create"] = "guild_event_channel"
        self.event_types["on_guild_channel_delete"] = "guild_event_channel"
        self.event_types["on_guild_channel_update"] = "guild_event_channel"
        self.event_types["on_guild_update"] = "guild_event_channel"

        self.event_types["on_guild_role_create"] = "guild_event_channel"
        self.event_types["on_guild_role_delete"] = "guild_event_channel"
        self.event_types["on_guild_role_update"] = "guild_event_channel"

        self.event_types["on_member_ban"] = "mod_event_channel"
        self.event_types["on_member_unban"] = "mod_event_channel"
        self.event_types["on_member_kick"] = "mod_event_channel"
        self.event_types["on_member_remove"] = "mod_event_channel"
        self.event_types["on_member_join"] = "mod_event_channel"

        self.event_types["on_warning"] = "mod_event_channel"

    async def load_settings(self):
        self.settings = await self.config.settings()

    async def save_settings(self):
        await self.config.settings.set(self.settings)

    async def _ignore_server_check(self, guild):
        if 'ignore' not in self.settings[str(guild.id)]:
            self.settings[str(guild.id)] = {}
            self.settings[str(guild.id)]['ignore'] = {}
            self.settings[str(guild.id)]['ignore']['members'] = {}
            self.settings[str(guild.id)]['ignore']['channels'] = {}
            self.settings[str(guild.id)]['ignore']['roles'] = {}
        return True

    async def ignoremember(self, guild, author):
        await self._ignore_server_check(guild)
        if str(author.id) in self.ignore[str(guild.id)]['ignore']['members']:
            del self.settings[str(guild.id)]['ignore']['members'][str(author.id)]
            await self.save_settings()
            return "Tracking {} again".format(author.mention)
        else:
            self.settings[str(guild.id)]['ignore']['members'][str(author.id)] = True
            await self.save_settings()
            return "Not tracking {} anymore".format(author.mention)

    async def ignorechannel(self, guild, channel):
        await self._ignore_server_check(guild)
        if str(channel.id) in self.ignore[str(guild.id)]['ignore']['channels']:
            del self.settings[str(guild.id)]['ignore']['channels'][str(channel.id)]
            await self.save_settings()
            return "Tracking {} again".format(channel.mention)
        else:
            self.settigns[str(guild.id)]['ignore']['channels'][str(channel.id)] = True
            await self.save_settings()
            return "Not tracking {} anymore".format(channel.mention)

    async def ignorerole(self, guild, role):
        await self._ignore_server_check(guild)
        if str(role.id) in self.settings[str(guild.id)]['ignore']['roles']:
            del self.settings[str(guild.id)]['ignore']['roles'][str(role.id)]
            await self.save_settings()
            return "Tracking {} again".format(role.mention)
        else:
            self.settings[str(guild.id)]['ignore']['roles'][str(role.id)] = True
            await self.save_settings()
            return "Not tracking {} anymore".format(role.mention)

    async def _ignore(self, guild, author=None, channel=None):
        await self._ignore_server_check(guild)
        if channel:
            if str(channel.id) in self.settings[str(guild.id)]['ignore']["channels"]:
                return False
        if author:
            if str(author.id) in self.settings[str(guild.id)]['ignore']["members"]:
                return False
            if [role.id for role in author.roles if str(role.id) in self.settings[str(guild.id)]['ignore']["roles"]]:
                return False
        return True

    async def _validate_server(self, guild):
        return True if str(guild.id) in self.settings else False

    async def _validate_event(self, guild):
        try:
            return self.settings[str(guild.id)]["events"][inspect.stack()[1][3]] if await self._validate_server(guild) else False
        except KeyError:
            return False

    async def _get_channel(self, guild):
        return discord.utils.get(self.bot.get_all_channels(), id=self.settings[str(guild.id)]["channels"][self.event_types[inspect.stack()[2][3]]])

    async def _send_message_to_channel(self, guild, content=None, embed=None, attachment=None):
        channel = await self._get_channel(guild)
        if channel:
            if embed:
                await channel.send(content=content, embed=embed)
            elif attachment:
                await channel.send(content=content, file=discord.File(attachment))
            elif content:
                await channel.send(content=content)
        else:
            pass  # needs error!

    async def saveattachement(self, data, filename, message_id):
        filename = "{}-{}".format(str(message_id), filename)
        with open('attachments/'+filename, 'wb') as f:
            f.write(data)
        return filename

    async def downloadattachment(self, url, filename, message_id):
        session = aiohttp.ClientSession()
        async with session.get(url) as r:
            data = await r.read()
        await session.close()
        filename = await self.saveattachement(data, filename, message_id)
        return filename

    async def _start_setup(self, context):
        guild = context.guild
        if guild.id not in self.settings:
            self.settings[str(guild.id)] = {}
        self.settings[str(guild.id)] = await GrenzpolizeiSetup(self.bot, context).setup()
        await self.save_settings()
        return True

    async def _start_auto_setup(self, context):
        guild = context.guild
        if guild.id not in self.settings:
            self.settings[str(guild.id)] = {}
        self.settings[str(guild.id)] = await GrenzpolizeiSetup(self.bot, context).auto_setup()
        await self.save_settings()
        return True
