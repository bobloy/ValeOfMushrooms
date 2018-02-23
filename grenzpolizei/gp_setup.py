import asyncio
import discord
from redbot.core.i18n import CogI18n

_ = CogI18n('GrenzpolizeiSetup', __file__)


class GrenzpolizeiSetup:
    def __init__(self, bot, context):
        self.context = context
        self.bot = bot

        self.green = discord.Color.green()
        self.orange = discord.Color.orange()
        self.red = discord.Color.red()
        self.blue = discord.Color.blue()

    async def _yes_no(self, question, context):
        channel = context.channel

        def check(message):
            return context.author.id == message.author.id

        bot_message = await channel.send(question)
        try:
            message = await self.bot.wait_for('message', timeout=120, check=check)
        except TimeoutError:
            print('Timeout!')
        if message:
            if any(n in message.content.lower() for n in ['yes', 'y']):
                await bot_message.edit(content=_('**{} Yes**').format(question))
                try:
                    await message.delete()
                except:
                    pass
                return True
        await bot_message.edit(content=_('**{} No**').format(question))
        try:
            await message.delete()
        except:
            pass
        return False

    async def _what_channel(self, question, context):
        channel = context.channel

        def check(message):
            return context.author.id == message.author.id

        bot_message = await channel.send(question)
        try:
            message = await self.bot.wait_for('message', timeout=120, check=check)
        except TimeoutError:
            print('Timeout!')
        if message:
            channel = message.raw_channel_mentions[0] if message.raw_channel_mentions else False
            if channel:
                await bot_message.edit(content='**{}**'.format(question))
                return channel
            else:
                await bot_message.edit(content=_('**That\'s not a valid channel! Please mention a channel.**'))
                return False
        return False

    async def auto_setup(self):
        events = {}
        channels = {}
        guild_config = {}
        overwrites = {
            self.context.guild.default_role: discord.PermissionOverwrite(send_messages=False),
            self.context.guild.me: discord.PermissionOverwrite(send_messages=True)
        }
        message = await self.context.send(_('Creating Grenzpolizei category...'))
        big_brother_category = await self.context.guild.create_category('Grenzpolizei', reason=_('Grenzpolizei needs this to put all event channels in.'), overwrites=overwrites)
        await message.edit(content=_('Creating event channels...'))
        member_event_channel = await self.context.guild.create_text_channel('member-events', category=big_brother_category, reason=_('Grenzpolizei will put all member events in this channel.'))
        message_event_channel = await self.context.guild.create_text_channel('message-events', category=big_brother_category, reason=_('Grenzpolizei will put all message events in this channel.'))
        guild_event_channel = await self.context.guild.create_text_channel('server-events', category=big_brother_category, reason=_('Grenzpolizei will put all server events in this channel.'))
        mod_event_channel = await self.context.guild.create_text_channel('mod-events', category=big_brother_category, reason=_('Grenzpolizei will put all mod events in this channel.'))
        await message.edit(content=_('Setting up all events...'))
        # Member events
        events['on_member_join'] = True
        events['on_member_ban'] = True
        events['on_member_unban'] = True
        events['on_member_remove'] = True
        events['on_member_update'] = True
        events['on_voice_state_update'] = True

        # Message events
        events['on_message_delete'] = True
        events['on_raw_bulk_message_delete'] = True
        events['on_message_edit'] = True

        # Server events
        events['on_guild_channel_create'] = True
        events['on_guild_channel_delete'] = True
        events['on_guild_channel_update'] = True
        events['on_guild_update'] = True

        events['on_guild_role_create'] = True
        events['on_guild_role_delete'] = True
        events['on_guild_role_update'] = True

        # Warning events
        events['on_warning'] = True
        events['on_kick'] = True
        events['on_ban'] = True

        channels['member_event_channel'] = member_event_channel.id
        channels['message_event_channel'] = message_event_channel.id
        channels['guild_event_channel'] = guild_event_channel.id
        channels['mod_event_channel'] = mod_event_channel.id

        guild_config['channels'] = channels
        guild_config['events'] = events
        await message.edit(content=_('And we\'re all done!'))
        return guild_config

    async def setup(self):
        channel = self.context.channel
        instructions = _('You\'re required to answer them with either **\'yes\'** or **\'no\'** answers.\n\n'
                         'You get **2 minutes** to answer each question. If not answered it will be defaulted to **\'no\'**.\n\n'
                         'Then you\'re required to give a channel for each event category, these categories are:\n\n'
                         '**- member events**\n**- message events**\n**- server events**\n**- warning events.**\n\n'
                         'Each channel _needs_ to be a channel mention, otherwise it won\'t work. You can use the same channel for all event types.\n'
                         'Make also sure to give proper permissions to the bot to post and embed messages in these channels.\n\n'
                         '**Good luck!**')

        embed = discord.Embed(title=_('**Welcome to the setup for Grenzpolizei**'), description=instructions, color=self.green)
        await channel.send(embed=embed)
        await asyncio.sleep(10)

        events = {}
        channels = {}
        guild_config = {}

        # Member events
        events['on_member_join'] = await self._yes_no(_('Do you want to track members joining? [y]es/[n]o'), self.context)
        events['on_member_ban'] = await self._yes_no(_('Do you want to track members being banned? [y]es/[n]o'), self.context)
        events['on_member_unban'] = await self._yes_no(_('Do you want to track members being unbanned? [y]es/[n]o'), self.context)
        events['on_member_remove'] = await self._yes_no(_('Do you want to track members leaving this server? [y]es/[n]o'), self.context)
        events['on_member_update'] = await self._yes_no(_('Do you want to track member changes? [y]es/[n]o'), self.context)
        events['on_voice_state_update'] = await self._yes_no(_('Do you want to track voice channel changes? [y]es/[n]o'), self.context)

        # Message events
        events['on_message_delete'] = await self._yes_no(_('Do you want to track message deletion? [y]es/[n]o'), self.context)
        events['on_raw_bulk_message_delete'] = await self._yes_no(_('Do you want to track bulk message deletion? [y]es/[n]o'), self.context)
        events['on_message_edit'] = await self._yes_no(_('Do you want to track message editing? [y]es/[n]o'), self.context)

        # Server events
        events['on_guild_channel_create'] = await self._yes_no(_('Do you want to track channel creation? [y]es/[n]o'), self.context)
        events['on_guild_channel_delete'] = await self._yes_no(_('Do you want to track channel deletion? [y]es/[n]o'), self.context)
        events['on_guild_channel_update'] = await self._yes_no(_('Do you want to track channel updates? [y]es/[n]o'), self.context)
        events['on_guild_update'] = await self._yes_no(_('Do you want to track server updates? [y]es/[n]o'), self.context)

        events['on_guild_role_create'] = await self._yes_no(_('Do you want to track role creation? [y]es/[n]o'), self.context)
        events['on_guild_role_delete'] = await self._yes_no(_('Do you want to track role deletion? [y]es/[n]o'), self.context)
        events['on_guild_role_update'] = await self._yes_no(_('Do you want to track role updates? [y]es/[n]o'), self.context)

        # Warning events
        events['on_warning'] = await self._yes_no(_('Do you want to track member warnings? [y]es/[n]o'), self.context)
        events['on_kick'] = await self._yes_no(_('Do you want to track member kicks? [y]es/[n]o'), self.context)
        events['on_ban'] = await self._yes_no(_('Do you want to track member bans? [y]es/[n]o'), self.context)

        if any([events['on_member_join'], events['on_member_ban'], events['on_member_unban'], events['on_member_remove'], events['on_voice_state_update']]):
            channels['member_event_channel'] = await self._what_channel(_('Which channel do you want to use for member events? (please mention the channel)'), self.context)
        else:
            channels['member_event_channel'] = False

        if any([events['on_message_delete'], events['on_message_edit']]):
            channels['message_event_channel'] = await self._what_channel(_('Which channel do you want to use for message events? (please mention the channel)'), self.context)
        else:
            channels['message_event_channel'] = False

        if any([events['on_guild_channel_create'], events['on_guild_channel_delete'], events['on_guild_channel_update'], events['on_guild_role_create'],
                events['on_guild_role_delete'], events['on_guild_role_update'], events['on_raw_bulk_message_delete']]):
            channels['guild_event_channel'] = await self._what_channel(_('Which channel do you want to use for server events? (please mention the channel)'), self.context)
        else:
            channels['guild_event_channel'] = False

        if any([events['on_warning'], events['on_kick'], events['on_ban']]):
            channels['mod_event_channel'] = await self._what_channel(_('Which channel do you want to use for modding events? (please mention the channel)'), self.context)
        else:
            channels['mod_event_channel'] = False

        guild_config['channels'] = channels
        guild_config['events'] = events

        return guild_config
