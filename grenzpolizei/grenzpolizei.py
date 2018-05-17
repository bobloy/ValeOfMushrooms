import discord
from redbot.core.i18n import Translator
from datetime import datetime
from discord.ext import commands
from .gp_core import GrenzpolizeiCore

_ = Translator('Grenzpolizei', __file__)

VERSION = 514181855

# TODO:
# Better error handling, especially to guild
# Documentation
# Disable all events
# Fix passport


class Grenzpolizei:
    def __init__(self, bot):
        self.bot = bot
        self.core = GrenzpolizeiCore(bot)

        self.green = discord.Color.green()
        self.orange = discord.Color.orange()
        self.red = discord.Color.red()
        self.blue = discord.Color.blue()
        self.black = discord.Color.from_rgb(15, 2, 2)

    @commands.group(name='grenzpolizei', aliases=['gp'])
    async def _grenzpolizei(self, context):
        '''
        The Grenzpolizei Cog
        '''
        if context.invoked_subcommand is None:
            await context.send_help()

    @_grenzpolizei.group(name='set')
    @commands.has_permissions(administrator=True)
    async def _grenzpolizei_set(self, context):
        '''
        Settings
        '''
        if context.invoked_subcommand is None or context.invoked_subcommand == self._grenzpolizei_set:
            await context.send_help()

    @_grenzpolizei_set.command(name='show')
    async def _set_show(self, context):
        '''
        Show all settings
        '''
        guild = context.guild
        if str(guild.id) in self.core.settings:
            all_settings = self.core.settings[str(guild.id)]
            message = '```'
            for key in all_settings:
                if key == 'compact':
                    message += 'Compact Mode: {}\n'.format(all_settings['compact'])
                if key == 'events':
                    message += 'Events:\n'
                    c = len(all_settings['events'])
                    for event in all_settings['events']:
                        message += '\t{}\n\t\tEnabled: {}\n\t\tChannel: #{}\n'.format(event, all_settings['events'][event]['enabled'], context.guild.get_channel(all_settings['events'][event]['channel']).name)
                        c -= 1
            message += '```'
            guild = context.guild
            await context.send(message)
        else:
            await context.send(_('Please run the setup first.'))

    @_grenzpolizei_set.command(name='compact')
    async def _compactmode(self, context):
        '''
        Toggle compact mode for smaller messages
        '''
        guild = context.guild
        await context.send(await self.core.compactmode(guild))

    @_grenzpolizei_set.group(name='event')
    async def _grenzpolizei_event(self, context):
        '''
        Manually control and change event settings
        '''
        if context.invoked_subcommand is None  or context.invoked_subcommand == self._grenzpolizei_event:
            await context.send_help()

    @_grenzpolizei_event.command(name='channel')
    async def _channel_event(self, context, channel: discord.TextChannel, event_type: str):
        '''
        Change an event's channel
        '''
        guild = context.guild
        if event_type.lower() in self.core.event_types:
            self.core.settings[str(guild.id)]['events'][event_type]['enabled'] = True
            self.core.settings[str(guild.id)]['events'][event_type]['channel'] = channel.id
            await self.core.save_settings()
            await context.send(_('Event \'{}\' enabled').format(event_type))
        else:
            await context.send(_('This event type does not exist.'))
            message = _('Copy these exactly in order enable or disable them.\n')
            for event in self.core.event_types:
                message += '\n**{}**'.format(event)
            embed = discord.Embed(title=_('Available event types'), description=message, color=self.green)
            await context.send(embed=embed)

    @_grenzpolizei_event.command(name='enable')
    async def _enable_event(self, context, event_type: str, channel: discord.TextChannel):
        '''
        Enable an event
        '''
        guild = context.guild
        if event_type.lower() in self.core.event_types:
            self.core.settings[str(guild.id)]['events'][event_type]['enabled'] = True
            self.core.settings[str(guild.id)]['events'][event_type]['channel'] = channel.id
            await self.core.save_settings()
            await context.send(_('Event \'{}\' enabled').format(event_type))
        else:
            await context.send(_('This event type does not exist.'))
            message = _('Copy these exactly in order enable or disable them.\n')
            for event in self.core.event_types:
                message += '\n**{}**'.format(event)
            embed = discord.Embed(title=_('Available event types'), description=message, color=self.green)
            await context.send(embed=embed)

    @_grenzpolizei_event.command(name='disable')
    async def _disable_event(self, context, *event_type: str):
        '''
        Disable an event
        '''
        guild = context.guild
        if event_type in self.core.event_types:
            guild = context.guild
            self.core.settings[str(guild.id)]['events'][event_type]['enabled'] = False
            await self.core.save_settings()
            await context.send(_('Event \'{}\' disabled').format(event_type))
        else:
            await context.send(_('This event type does not exist.'))
            message = _('Copy these exactly in order enable or disable them.\n')
            for event in self.core.event_types:
                message += '\n**{}**'.format(event)
            embed = discord.Embed(title=_('Available event types'), description=message, color=self.green)
            await context.send(embed=embed)

    @_grenzpolizei.command(name='setup')
    @commands.has_permissions(administrator=True)
    async def _grenzpolizei_setup(self, context):
        '''
        Begin your journey into authoritarianism
        '''
        x = await self.core._start_setup(context)
        if x:
            await context.channel.send(_('“Until they become conscious, they will never rebel”'))
        else:
            await context.channel.send(_('Please try again, it didn\'t go quite alright.'))

    @_grenzpolizei.command(name='autosetup')
    @commands.has_permissions(administrator=True)
    async def _grenzpolizei_autosetup(self, context):
        '''
        RECOMMENDED! Begin your journey into authoritarianism, automatically.
        '''
        try:
            x = await self.core._start_auto_setup(context)
            if x:
                await context.channel.send(_('“Until they become conscious, they will never rebel”'))
            else:
                await context.channel.send(_('Please try again, it didn\'t go quite alright.'))
        except discord.Forbidden:
            await context.send(_('I don\'t have the permissions to create channels.'))

    @_grenzpolizei.group(name='ignore')
    @commands.has_permissions(kick_members=True)
    async def _grenzpolizei_ignore(self, context):
        '''
        Ignore
        '''
        if context.invoked_subcommand is None  or context.invoked_subcommand == self._grenzpolizei_ignore:
            await context.send_help()

    @_grenzpolizei_ignore.command(name='member')
    async def _ignoremember(self, context, member: discord.Member):
        '''
        Ignore a member, this is a toggle
        '''
        guild = context.guild
        channel = context.channel
        await channel.send(await self.core.ignoremember(guild, member))

    @_grenzpolizei_ignore.command(name='channel')
    async def _ignorechannel(self, context, channel: discord.TextChannel):
        '''
        Ignore a channel, this is a toggle
        '''
        guild = context.guild
        channel = context.channel
        await channel.send(await self.core.ignorechannel(guild, channel))

    @_grenzpolizei.command(name='warn')
    @commands.has_permissions(kick_members=True)
    async def _warn(self, context, member: discord.Member, *, reason):
        '''
        Give out a warning
        '''
        author = context.author
        guild = context.guild
        warn = await self.on_warning(guild, author, member, reason)
        if warn:
            message = _('Done!')
        else:
            message = _('Something didn\'t go quite right.')
        await self.core._send_message_to_channel(guild, content=message)

    @_grenzpolizei.command(name='passport')
    @commands.has_permissions(kick_members=True)
    async def _passport(self, context, member: discord.Member):
        '''
        Get all logged events from a user
        '''
        await context.channel.send(_('This needs some extensive rework. Sorry!'))

        # def predicate(message):
        #    return message.author.id == self.bot.user.id and message.embeds

        # tmp = {}
        # event_channels = [channel for channel in [event['channel'] for event in self.core.settings[str(context.guild.id)]['events']]]
        # if context.channel.id not in [event_channels[channel] for channel in dict(event_channels.items())]:
        #    embed = discord.Embed(title=_('The passport of {0.name}#{0.discriminator} contains the following:').format(member), color=discord.Color.orange())
        #    await context.channel.send(embed=embed)
        #    for event_channel in ['mod_event_channel', 'member_event_channel']:
        #        channel = self.bot.get_channel(self.core.settings[str(context.guild.id)]['channels'][event_channel])
        #        if channel:
        #            async for message in channel.history(reverse=True):
        #                for embed in message.embeds:
        #                    embed_dict = str(embed.to_dict())
        #                    if str(member.id) in embed_dict:
        #                        if message.id not in tmp:
        #                            await context.channel.send(embed=embed)
        #                            tmp[message.id] = True
        # else:
        #    await context.channel.send(_('To prevent major issues, do this in a different channel and not in an event channel!'))

    async def on_warning(self, guild, mod, member, reason):
        if await self.core._validate_event(guild) and member.id != self.bot.user.id:
            avatar = member.avatar_url if member.avatar else member.default_avatar_url
            embed = discord.Embed(color=discord.Color.orange())
            embed.set_author(name=_('A warning has been issued'), icon_url=avatar)
            embed.add_field(name=_('**Member**'), value='{0.name}#{0.discriminator}\n({0.id}'.format(member))
            embed.add_field(name=_('**Mod**'), value=mod.name, inline=False)
            embed.add_field(name=_('**Reason**'), value=reason)
            embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
            await self.core._send_message_to_channel(guild, embed=embed)
            return True
        else:
            return False

    async def on_member_join(self, author):
        guild = author.guild
        if await self.core._validate_event(guild) and author.id != self.bot.user.id:
            avatar = author.avatar_url if author.avatar else author.default_avatar_url
            embed = discord.Embed(color=self.green, description=_('**{0.name}#{0.discriminator}** ({0.id})').format(author))
            embed.set_author(name=_('Member joined'), icon_url=avatar)
            embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
            await self.core._send_message_to_channel(guild, embed=embed)

    async def on_member_ban(self, guild, author):
        if await self.core._validate_event(guild) and author.id != self.bot.user.id:
            the_mod = None
            async for entry in guild.audit_logs(limit=2):
                if entry.target.id == author.id and entry.action is discord.AuditLogAction.ban:
                    the_mod = entry.user
                    if entry.reason:
                        reason = entry.reason
                    else:
                        reason = False
            avatar = author.avatar_url if author.avatar else author.default_avatar_url
            embed = discord.Embed(color=self.red)
            embed.set_author(name=_('Member has been banned'), icon_url=avatar)
            embed.add_field(name=_('**Mod**'), value='{0.display_name}').format(the_mod)
            embed.add_field(name=_('**Member**'), value='**{0.name}#{0.discriminator}** ({0.display_name} {0.id})'.format(author), inline=False)
            embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
            if reason:
                embed.add_field(name='Reason', value=reason)
            await self.core._send_message_to_channel(guild, embed=embed)

    async def on_member_unban(self, guild, author):
        if await self.core._validate_event(guild) and author.id != self.bot.user.id:
            async for entry in guild.audit_logs(limit=1):
                if entry.action is discord.AuditLogAction.unban:
                    the_mod = entry.user
            avatar = author.avatar_url if author.avatar else author.default_avatar_url
            embed = discord.Embed(color=self.orange)
            embed.set_author(name=_('Member has been unbanned'), icon_url=avatar)
            embed.add_field(name=_('**Mod**'), value='{0.display_name}'.format(the_mod))
            embed.add_field(name=_('**Member**'), value='**{0.name}#{0.discriminator}** ({0.display_name} {0.id})'.format(author), inline=False)
            embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
            await self.core._send_message_to_channel(guild, embed=embed)

    async def on_member_remove(self, author):
        guild = author.guild
        if await self.core._validate_event(guild) and author.id != self.bot.user.id:
            avatar = author.avatar_url if author.avatar else author.default_avatar_url
            embed = discord.Embed(color=self.red, description=_('**{0.name}#{0.discriminator}** ({0.display_name} {0.id})').format(author))
            embed.set_author(name=_('Member left'), icon_url=avatar)
            embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
            await self.core._send_message_to_channel(guild, embed=embed)

    async def on_member_update(self, before, after):
        guild = after.guild
        author = after
        if await self.core._ignore(guild, author=author):
            if await self.core._validate_event(guild) and after.id != self.bot.user.id:
                async for entry in guild.audit_logs(limit=1):
                    by_mod = False
                    if entry.action is discord.AuditLogAction.member_update:
                        the_mod = entry.user
                        by_mod = True
                if before.name != after.name:
                    embed = discord.Embed(color=self.blue, description=_('From **{0.name}** ({0.id}) to **{1.name}**').format(before, after))
                    embed.set_author(name=_('Name changed'), icon_url=guild.icon_url)
                    await self.core._send_message_to_channel(guild, embed=embed)
                if before.nick != after.nick:
                    embed = discord.Embed(color=self.blue, description=_('From **{0.nick}** ({0.id}) to **{1.nick}**').format(before, after))
                    if by_mod:
                        embed.set_author(name=_('Nickname changed by {0.display_name}').format(the_mod), icon_url=guild.icon_url)
                    else:
                        embed.set_author(name=_('Nickname changed'), icon_url=guild.icon_url)
                    await self.core._send_message_to_channel(guild, embed=embed)
                if before.roles != after.roles:
                    if len(before.roles) > len(after.roles):
                        for role in before.roles:
                            if role not in after.roles:
                                embed = discord.Embed(color=self.blue, description=_('**{0.display_name}** ({0.id}) lost the **{1.name}** role').format(before, role))
                                if by_mod:
                                    embed.set_author(name=_('Role removed by {0.display_name}').format(the_mod), icon_url=guild.icon_url)
                                else:
                                    embed.set_author(name=_('Role removed'), icon_url=guild.icon_url)
                    elif len(before.roles) < len(after.roles):
                        for role in after.roles:
                            if role not in before.roles:
                                embed = discord.Embed(color=self.blue, description=_('**{0.display_name}** ({0.id}) got the **{1.name}** role').format(before, role))
                                if by_mod:
                                    embed.set_author(name=_('Role applied by {0.display_name}').format(the_mod), icon_url=guild.icon_url)
                                else:
                                    embed.set_author(name=_('Role applied'), icon_url=guild.icon_url)
                    await self.core._send_message_to_channel(guild, embed=embed)

    async def on_message_delete(self, message):
        guild = message.guild
        author = message.author
        channel = message.channel
        if isinstance(channel, discord.abc.GuildChannel):
            if await self.core._ignore(guild, author=author, channel=channel):
                if await self.core._validate_event(guild) and author.id != self.bot.user.id:
                    the_mod = False
                    async for entry in guild.audit_logs(limit=1):
                        if entry.action is discord.AuditLogAction.message_delete:
                            the_mod = entry.user

                    embed = discord.Embed(color=self.red)
                    avatar = author.avatar_url if author.avatar else author.default_avatar_url
                    embed.set_author(name=_('Message removed'), icon_url=avatar)
                    embed.add_field(name=_('Member'), value='{0.display_name}#{0.discriminator} ({0.id})'.format(author))
                    if the_mod:
                        embed.add_field(name=_('Deleted By'), value='{0.display_name}#{0.discriminator} ({0.id})'.format(the_mod))
                    embed.add_field(name=_('Channel'), value=message.channel.mention)
                    if message.content:
                        embed.add_field(name=_('Message'), value=message.content, inline=False)

                    embed.set_footer(text=_('Message ID: {} | {}').format(message.id, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)
                    if message.attachments:
                        for attachment in message.attachments:
                            filename = await self.core.downloadattachment(attachment.url, attachment.filename, message.id)
                            message = _('Attachment file for message: {}').format(message.id)
                            await self.core._send_message_to_channel(guild, content=message, attachment=self.core.attachment_path+'/'+filename)

    async def on_raw_bulk_message_delete(self, messages, channel):
        channel = self.bot.get_channel(channel)
        guild = channel.guild
        if isinstance(channel, discord.abc.GuildChannel):
            if await self.core._validate_event(guild):
                embed = discord.Embed(title=_('{} messages have been purged in {}').format(len(messages), channel.name), color=self.red)
                await self.core._send_message_to_channel(guild, embed=embed)
                return True if 1 == 1 and 2 == 2 else False

    async def on_message_edit(self, before, after):
        guild = after.guild
        author = after.author
        channel = after.channel
        if isinstance(channel, discord.abc.GuildChannel):
            if await self.core._ignore(guild, author=author, channel=channel):
                if await self.core._validate_event(guild) and author.id != self.bot.user.id and before.clean_content != after.clean_content:
                    embed = discord.Embed(color=self.blue)
                    avatar = author.avatar_url if author.avatar else author.default_avatar_url
                    embed.set_author(name=_('Message changed'), icon_url=avatar)
                    embed.add_field(name=_('Member'), value='{0.display_name}#{0.discriminator}\n({0.id})'.format(author))
                    embed.add_field(name=_('Channel'), value=before.channel.mention)
                    embed.add_field(name=_('Before'), value=before.content, inline=False)
                    embed.add_field(name=_('After'), value=after.content, inline=False)
                    embed.set_footer(text=_('Message ID: {} | {}').format(after.id, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_channel_create(self, channel):
        if isinstance(channel, discord.abc.GuildChannel):
            guild = channel.guild
            if await self.core._validate_event(guild):
                async for entry in guild.audit_logs(limit=1):
                    if entry.action is discord.AuditLogAction.channel_create:
                        the_mod = entry.user
                if isinstance(channel, discord.CategoryChannel):
                    embed = discord.Embed(color=self.green)
                    embed.set_author(name=_('A new category has been created by {0.display_name}: #{1.name}').format(the_mod, channel), icon_url=guild.icon_url)
                else:
                    embed = discord.Embed(color=self.green)
                    embed.set_author(name=_('A new channel has been created by {0.display_name}: #{1.name}').format(the_mod, channel), icon_url=guild.icon_url)
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_channel_delete(self, channel):
        if isinstance(channel, discord.abc.GuildChannel):
            guild = channel.guild
            if await self.core._validate_event(guild):
                async for entry in guild.audit_logs(limit=1):
                    if entry.action is discord.AuditLogAction.channel_delete:
                        the_mod = entry.user
                if isinstance(channel, discord.CategoryChannel):
                    embed = discord.Embed(color=self.red)
                    embed.set_author(name=_('A category has been deleted by {0.display_name}: #{1.name}').format(the_mod, channel), icon_url=guild.icon_url)
                else:
                    embed = discord.Embed(color=self.red)
                    embed.set_author(name=_('A channel has been deleted by {0.display_name}: #{1.name}').format(the_mod, channel), icon_url=guild.icon_url)
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_channel_update(self, before, after):
        channel = after
        if isinstance(channel, discord.abc.GuildChannel):
            guild = after.guild
            if await self.core._validate_event(guild):
                async for entry in guild.audit_logs(limit=1):
                    if entry.action is discord.AuditLogAction.channel_update:
                        the_mod = entry.user
                if before.name != after.name:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_('#{0.name} renamed to #{1.name} by {2.display_name}').format(before, after, the_mod), icon_url=guild.icon_url)
                    embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)
                if not isinstance(channel, discord.VoiceChannel) and not isinstance(channel, discord.CategoryChannel):
                    if before.topic != after.topic:
                        embed = discord.Embed(color=self.blue)
                        embed.set_author(name=_('#{0.name} changed topic from \'{0.topic}\' to \'{1.topic}\'').format(before, after), icon_url=guild.icon_url)
                        embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                        await self.core._send_message_to_channel(guild, embed=embed)
                if before.position != after.position:
                    if isinstance(channel, discord.CategoryChannel):
                        embed = discord.Embed(color=self.blue)
                        embed.set_author(name=_('Category moved by #{0.name} from {0.position} to {1.position}').format(before, after), icon_url=guild.icon_url)
                        embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                        await self.core._send_message_to_channel(guild, embed=embed)
                    else:
                        embed = discord.Embed(color=self.blue)
                        embed.set_author(name=_('Channel moved  by #{0.name} from {0.position} to {1.position}').format(before, after), icon_url=guild.icon_url)
                        embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                        await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_role_create(self, role):
        guild = role.guild
        if await self.core._validate_event(guild):
            the_mod = False
            async for entry in guild.audit_logs(limit=1):
                if entry.action is discord.AuditLogAction.role_create:
                    the_mod = entry.user
            embed = discord.Embed(color=self.green)
            if the_mod:
                embed.set_author(name=_('Role created by {0.display_name}: {1.name}').format(the_mod, role), icon_url=guild.icon_url)
            else:
                embed.set_author(name=_('Role created by Discord: {1.name}').format(the_mod, role), icon_url=guild.icon_url)
            embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
            await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_role_delete(self, role):
        guild = role.guild
        if await self.core._validate_event(guild):
            async for entry in guild.audit_logs(limit=1):
                if entry.action is discord.AuditLogAction.role_delete:
                    the_mod = entry.user
            embed = discord.Embed(color=self.red)
            embed.set_author(name=_('Role deleted by {0.display_name}: {1.name}').format(the_mod, role), icon_url=guild.icon_url)
            embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
            await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_role_update(self, before, after):
        guild = after.guild
        if await self.core._validate_event(guild):
            the_mod = None
            async for entry in guild.audit_logs(limit=1):
                if entry.action is discord.AuditLogAction.role_update:
                    the_mod = entry.user
            if before.name != after.name and after:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_('Role {0.name} renamed to {1.name} by {2.display_name}').format(before, after, the_mod), icon_url=guild.icon_url)
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.color != after.color:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_('Role color for {0.name} changed from {0.color} to {1.color} by {2.display_name}').format(before, after, the_mod), icon_url=guild.icon_url)
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.mentionable != after.mentionable:
                embed = discord.Embed(color=self.blue)
                if after.mentionable:
                    embed.set_author(name=_('{0.display_name} made role {1.name} mentionable').format(the_mod, after), icon_url=guild.icon_url)
                else:
                    embed.set_author(name=_('{0.display_name} made role  {1.name} unmentionable').format(the_mod, after), icon_url=guild.icon_url)
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.hoist != after.hoist:
                embed = discord.Embed(color=self.blue)
                if after.hoist:
                    embed.set_author(name=_('{0.display_name} made role {1.name} to be shown seperately').format(the_mod, after), icon_url=guild.icon_url)
                else:
                    embed.set_author(name=_('{0.display_name} made role {1.name} to be shown seperately').format(the_mod, after), icon_url=guild.icon_url)
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.permissions != after.permissions:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_('Role permissions {0.name} changed from {0.permissions.value} to {1.permissions.value} by {2.display_name}').format(before, after, the_mod), icon_url=guild.icon_url)
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.position != after.position:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_('Role position {0} changed from {0.position} to {1.position} by {2.display_name}').format(before, after, the_mod), icon_url=guild.icon_url)
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_update(self, before, after):
        guild = after
        if await self.core._validate_event(guild):
            async for entry in guild.audit_logs(limit=1):
                if entry.action is discord.AuditLogAction.guild_update:
                    the_mod = entry.user
            if before.owner != after.owner:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_('Server owner changed from {0.owner.name} (id {0.owner.id})'
                                        'to {1.owner.name} (id {1.owner.id}) by {2.display_name}').format(before, after, the_mod), icon_url=guild.icon_url)
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.region != after.region:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_('Server region changed from {0.region} to {1.region} by {2.display_name}').format(before, after, the_mod), icon_url=guild.icon_url)
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.name != after.name:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_('Server name changed from {0.name} to {1.name} by {2.display_name}').format(before, after, the_mod), icon_url=guild.icon_url)
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.icon_url != after.icon_url:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_('Server icon changed from {0.icon_url} to {1.icon_url} by {2.display_name}').format(before, after, the_mod), icon_url=guild.icon_url)
                embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                await self.core._send_message_to_channel(guild, embed=embed)

    async def on_voice_state_update(self, author, before, after):
        guild = author.guild
        if await self.core._ignore(guild, author=author):
            if await self.core._validate_event(guild):
                if not before.afk and after.afk:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_('{0.display_name} is idle and has been sent to #{1.channel}').format(author, after), icon_url=author.avatar_url)
                    embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)
                elif before.afk and not after.afk:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_('{0.display_name} is active again in #{1.channel}').format(author, after), icon_url=author.avatar_url)
                    embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)
                if not before.self_mute and after.self_mute:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_('{0.display_name} muted themselves in #{1.channel}').format(author, after), icon_url=author.avatar_url)
                    embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)
                elif before.self_mute and not after.self_mute:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_('{0.display_name} unmuted themselves in #{1.channel}').format(author, after), icon_url=author.avatar_url)
                    embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)
                if not before.self_deaf and after.self_deaf:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_('{0.display_name} deafened themselves in #{1.channel}').format(author, after), icon_url=author.avatar_url)
                    embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)
                elif before.self_deaf and not after.self_deaf:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_('{0.display_name} undeafened themselves in #{1.channel}').format(author, after), icon_url=author.avatar_url)
                    embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)
                if not before.channel and after.channel:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_('{0.display_name} joined voice channel #{1.channel}').format(author, after), icon_url=author.avatar_url)
                    embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)
                elif before.channel and not after.channel:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_('{0.display_name} left voice channel #{1.channel}').format(author, before), icon_url=author.avatar_url)
                    embed.set_footer(text='{}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    await self.core._send_message_to_channel(guild, embed=embed)
