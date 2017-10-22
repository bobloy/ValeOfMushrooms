from redbot.core.data_manager import cog_data_path
from redbot.core.i18n import CogI18n
from .utils.dataIO import dataIO
import aiohttp
import inspect
import discord

from .gp_setup import GrenzpolizeiSetup

_ = CogI18n("Grenzpolizei", __file__)


class GrenzpolizeiCore:
    def __init__(self, bot):
        self.settings_file = str(cog_data_path()) + "\\CogManager\\cogs\\grenzpolizei\\data\\settings.json"
        self.ignore_file = str(cog_data_path()) + "\\CogManager\\cogs\\grenzpolizei\\data\\ignore.json"

        self.settings = dataIO.load_json(self.settings_file)
        self.ignore = dataIO.load_json(self.ignore_file)

        self.bot = bot

        self.event_types = {}

        self.event_types["on_member_update"] = "member_event_channel"
        self.event_types["on_voice_state_update"] = "member_event_channel"

        self.event_types["on_message_edit"] = "message_event_channel"
        self.event_types["on_message_delete"] = "message_event_channel"

        self.event_types["on_guild_channel_create"] = "guild_event_channel"
        self.event_types["on_guild_channel_delete"] = "guild_event_channel"
        self.event_types["on_guild_channel_update"] = "guild_event_channel"
        self.event_types["on_guild_update"] = "guild_event_channel"

        self.event_types["on_guild_role_create"] = "guild_event_channel"
        self.event_types["on_guild_role_delete"] = "guild_event_channel"
        self.event_types["on_guild_role_update"] = "guild_event_channel"

        self.event_types["on_warning"] = "mod_event_channel"
        self.event_types["on_member_ban"] = "mod_event_channel"
        self.event_types["on_member_unban"] = "mod_event_channel"
        self.event_types["on_member_kick"] = "mod_event_channel"
        self.event_types["on_member_remove"] = "mod_event_channel"
        self.event_types["on_member_join"] = "mod_event_channel"

    async def _save_settings(self):
        dataIO.save_json(self.settings_file, self.settings)

    async def _save_ignore(self):
        dataIO.save_json(self.ignore_file, self.ignore)

    async def _ignore_server_check(self, guild):
        if str(guild.id) not in self.ignore:
            self.ignore[str(guild.id)] = {}
            self.ignore[str(guild.id)]["members"] = {}
            self.ignore[str(guild.id)]["channels"] = {}
            self.ignore[str(guild.id)]["roles"] = {}
        return True

    async def ignoremember(self, guild, author):
        await self._ignore_server_check(guild)
        if str(author.id) in self.ignore[str(guild.id)]['members']:
            del self.ignore[str(guild.id)]['members'][str(author.id)]
            await self._save_ignore()
            return _("Tracking {} again").format(author.mention)
        else:
            self.ignore[str(guild.id)]['members'][str(author.id)] = True
            await self._save_ignore()
            return _("Not tracking {} anymore").format(author.mention)

    async def ignorechannel(self, guild, channel):
        await self._ignore_server_check(guild)
        if str(channel.id) in self.ignore[str(guild.id)]['channels']:
            del self.ignore[str(guild.id)]['channels'][str(channel.id)]
            await self._save_ignore()
            return _("Tracking {} again").format(channel.mention)
        else:
            self.ignore[str(guild.id)]['channels'][str(channel.id)] = True
            await self._save_ignore()
            return _("Not tracking {} anymore").format(channel.mention)

    async def ignorerole(self, guild, role):
        await self._ignore_server_check(guild)
        if str(role.id) in self.ignore[str(guild.id)]['roles']:
            del self.ignore[str(guild.id)]['roles'][str(role.id)]
            await self._save_ignore()
            return _("Tracking {} again").format(role.mention)
        else:
            self.ignore[str(guild.id)]['roles'][str(role.id)] = True
            await self._save_ignore()
            return _("Not tracking {} anymore").format(role.mention)

    async def _ignore(self, guild, author=None, channel=None):
        await self._ignore_server_check(guild)
        if channel:
            if str(channel.id) in self.ignore[str(guild.id)]["channels"]:
                return False
        if author:
            if str(author.id) in self.ignore[str(guild.id)]["members"]:
                return False
            if [role.id for role in author.roles if str(role.id) in self.ignore[str(guild.id)]["roles"]]:
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
        f = open('cogs/grenzpolizei/attachments/{}'.format(filename), 'wb')
        f.write(data)
        f.close()
        return filename

    async def downloadattachment(self, url, filename, message_id):
        session = aiohttp.ClientSession(connector=aiohttp.TCPConnector())
        async with session.get(url) as r:
            data = await r.read()
        session.close()
        filename = await self.saveattachement(data, filename, message_id)
        return filename

    async def _start_setup(self, context):
        guild = context.guild
        if guild.id not in self.settings:
            self.settings[str(guild.id)] = {}
        self.settings[str(guild.id)] = await GrenzpolizeiSetup(self.bot, context).setup()
        await self._save_settings()
        return True
