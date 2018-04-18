import aiohttp
import inspect
import discord
import os
from .gp_setup import GrenzpolizeiSetup
import redbot.core.data_manager as datam
import json
from redbot.core.i18n import CogI18n

_ = CogI18n('GrenzpolizeiCore', __file__)


class GrenzpolizeiCore:
    def __init__(self, bot):
        self.bot = bot

        self.path = str(datam.cog_data_path(self)).replace('\\', '/')
        self.attachment_path = self.path + '/attachments'
        self.settings_file = 'settings'

        self.check_folder()
        self.check_file()

        self.bot.loop.create_task(self.load_settings())

        self.event_types = ['on_member_update', 'on_voice_state_update', 'on_message_edit', 'on_message_delete',
                            'on_raw_bulk_message_delete', 'on_guild_channel_create', 'on_guild_channel_delete',
                            'on_guild_channel_update', 'on_guild_update', 'on_guild_role_create', 'on_guild_role_delete',
                            'on_guild_role_update', 'on_member_ban', 'on_member_unban', 'on_member_kick',
                            'on_member_remove', 'on_member_join', 'on_warning']

    def check_folder(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        if not os.path.exists(self.attachment_path):
            os.mkdir(self.attachment_path)

    def check_file(self):
        if not os.path.exists(self.path + '/{}.json'.format(self.settings_file)):
            self.save_json(self.settings_file, {})

    def save_json(self, filename, data):
        with open(self.path + '/{}.json'.format(filename), encoding='utf-8', mode='w') as f:
            json.dump(data, f, indent=4, sort_keys=True, separators=(',', ' : '))
        return data

    def load_json(self, filename):
        with open(self.path + '/{}.json'.format(filename), encoding='utf-8', mode='r') as f:
            data = json.load(f)
        return data

    async def load_settings(self):
        self.settings = self.load_json(self.settings_file)

    async def save_settings(self):
        self.save_json(self.settings_file, self.settings)

    async def _ignore_server_check(self, guild):
        if str(guild.id) in self.settings:
            if 'ignore' in self.settings[str(guild.id)]:
                return True
        return False

    async def ignoremember(self, guild, author):
        if str(guild.id) in self.settings:
            if 'ignore' not in self.settings[str(guild.id)]:
                self.settings[str(guild.id)]['ignore'] = {}
                self.settings[str(guild.id)]['ignore']['members'] = {}
                self.settings[str(guild.id)]['ignore']['channels'] = {}

            if str(author.id) in self.settings[str(guild.id)]['ignore']['members']:
                del self.settings[str(guild.id)]['ignore']['members'][str(author.id)]
                await self.save_settings()
                return _('Tracking {} again').format(author.mention)
            else:
                self.settings[str(guild.id)]['ignore']['members'][str(author.id)] = True
                await self.save_settings()
                return _('Not tracking {} anymore').format(author.mention)
        else:
            return _('Please run the setup first!')

    async def ignorechannel(self, guild, channel):
        if str(guild.id) in self.settings:
            if 'ignore' not in self.settings[str(guild.id)]:
                self.settings[str(guild.id)]['ignore'] = {}
                self.settings[str(guild.id)]['ignore']['members'] = {}
                self.settings[str(guild.id)]['ignore']['channels'] = {}

            if str(channel.id) in self.settings[str(guild.id)]['ignore']['channels']:
                del self.settings[str(guild.id)]['ignore']['channels'][str(channel.id)]
                await self.save_settings()
                return _('Tracking {} again').format(channel.mention)
            else:
                self.settings[str(guild.id)]['ignore']['channels'][str(channel.id)] = True
                await self.save_settings()
                return _('Not tracking {} anymore').format(channel.mention)
        else:
            return _('Please run the setup first!')

    async def _ignore(self, guild, author=None, channel=None, role=None):
        if await self._ignore_server_check(guild):
            if channel:
                if str(channel.id) in self.settings[str(guild.id)]['ignore']['channels']:
                    return False
            if author:
                if str(author.id) in self.settings[str(guild.id)]['ignore']['members']:
                    return False
                # if [role.id for role in author.roles if str(role.id) in self.settings[str(guild.id)]['ignore']['roles']]:
                #    return False
        return True

    async def _validate_server(self, guild):
        return True if str(guild.id) in self.settings else False

    async def _validate_event(self, guild):
        try:
            return self.settings[str(guild.id)]['events'][inspect.stack()[1][3]]['enabled'] if await self._validate_server(guild) else False
        except KeyError:
            return False

    async def _get_channel(self, guild):
        if not inspect.stack()[2][3] in ['_warn']:
            return discord.utils.get(self.bot.get_all_channels(), id=self.settings[str(guild.id)]['events'][inspect.stack()[2][3]]['channel'])
        return False

    async def _send_message_to_channel(self, guild, content=None, embed=None, attachment=None):
        channel = await self._get_channel(guild)
        if channel:
            if embed:
                await channel.send(content=content, embed=embed)
            elif attachment:
                await channel.send(content=content, file=discord.File(attachment))
            elif content:
                await channel.send(content=content)

    async def saveattachement(self, data, filename, message_id):
        filename = '{}-{}'.format(str(message_id), filename)
        with open(self.attachment_path+'/'+filename, 'wb') as f:
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
