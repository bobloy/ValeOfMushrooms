import os
import discord
from redbot.core import checks
from redbot.core.i18n import CogI18n
from datetime import datetime
from discord.ext import commands

from .utils.hacks import Hacks

from .gp_core import GrenzpolizeiCore


dh = Hacks()

_ = CogI18n("Grenzpolizei", __file__)


class Grenzpolizei:
    def __init__(self, bot):
        self.bot = bot

        self.core = GrenzpolizeiCore(bot)
        self.settings = self.core.settings
        self.ignore = self.core.ignore

        self.green = discord.Color.green()
        self.orange = discord.Color.orange()
        self.red = discord.Color.red()
        self.blue = discord.Color.blue()

    @commands.group(pass_context=True, name="grenzpolizei", aliases=["gp", "border"])
    async def _grenzpolizei(self, context):
        if context.invoked_subcommand is None:
            await self.bot.send_cmd_help(context)

    @_grenzpolizei.command(pass_context=True, name="setup")
    @checks.mod_or_permissions(administrator=True)
    async def _setup(self, context):
        channel = context.channel
        config = await self.core._start_setup(context)
        if config:
            message = _("You're all set up right now!")
        else:
            message = _("Something didn't go quite right.")
        await channel.send(message)

    @_grenzpolizei.command(pass_context=True, name='ignoremember')
    @checks.mod_or_permissions(administrator=True)
    async def _ignoremember(self, context, member: discord.Member):
        '''
        Ignore a member, this is a toggle
        '''
        guild = context.guild
        channel = context.channel
        done = await self.core.ignoremember(guild, member)
        message = done
        await channel.send(message)

    @_grenzpolizei.command(pass_context=True, name='ignorechannel')
    @checks.mod_or_permissions(administrator=True)
    async def _ignorechannel(self, context, channel: discord.TextChannel):
        '''
        Ignore a channel, this is a toggle
        '''
        guild = context.guild
        channel = context.channel
        done = await self.core.ignorechannel(guild, channel)
        message = done
        await channel.send(message)

    @_grenzpolizei.command(pass_context=True, name='ignorerole')
    @checks.mod_or_permissions(administrator=True)
    async def _ignorerole(self, context, role: discord.Role):
        '''
        Ignore a role, this is a toggle
        '''
        guild = context.guild
        channel = context.channel
        done = await self.core.ignorerole(guild, role)
        message = done
        await channel.send(message)

    async def on_member_join(self, author):
        guild = author.guild
        if await self.core._validate_event(guild) and author.id != self.bot.user.id:
            avatar = author.avatar_url if author.avatar else author.default_avatar_url
            embed = discord.Embed(color=self.green, description='**{0.name}#{0.discriminator}** ({0.id})'.format(author))
            embed.set_author(name=_("Member joined"), icon_url=avatar)
            await self.core._send_message_to_channel(guild, embed=embed)

    async def on_member_ban(self, guild, author):
        if await self.core._validate_event(guild) and author.id != self.bot.user.id:
            async for entry in guild.audit_logs(limit=1):
                if entry.target.id == author.id and entry.action is discord.AuditLogAction.ban:
                    the_mod = entry.user
                    if entry.reason:
                        reason = entry.reason
                    else:
                        reason = False
            avatar = author.avatar_url if author.avatar else author.default_avatar_url
            embed = discord.Embed(color=self.red, description='**{0.name}#{0.discriminator}** ({0.display_name} {0.id})'.format(author))
            embed.set_author(name=_("Member banned by {0.display_name}").format(the_mod), icon_url=avatar)
            if reason:
                embed.add_field(name=_("Reason"), value=reason)
            await self.core._send_message_to_channel(guild, embed=embed)

    async def on_member_unban(self, guild, author):
        if await self.core._validate_event(guild) and author.id != self.bot.user.id:
            async for entry in guild.audit_logs(limit=1):
                if entry.action is discord.AuditLogAction.unban:
                    the_mod = entry.user
            avatar = author.avatar_url if author.avatar else author.default_avatar_url
            embed = discord.Embed(color=self.orange, description='**{0.name}#{0.discriminator}** ({0.id})'.format(author))
            embed.set_author(name=_("Member unbanned by {0.display_name}").format(the_mod), icon_url=avatar)
            await self.core._send_message_to_channel(guild, embed=embed)

    async def on_member_remove(self, author):
        guild = author.guild
        if await self.core._validate_event(guild) and author.id != self.bot.user.id:
            avatar = author.avatar_url if author.avatar else author.default_avatar_url
            embed = discord.Embed(color=self.red, description='**{0.name}#{0.discriminator}** ({0.display_name} {0.id})'.format(author))
            embed.set_author(name=_("Member left"), icon_url=avatar)
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
                    embed = discord.Embed(color=self.blue, description=_("From **{0.name}** ({0.id}) to **{1.name}**").format(before, after))
                    if by_mod:
                        embed.set_author(name=_("Name changed by {0.display_name}").format(the_mod), icon_url=guild.icon_url)
                    else:
                        embed.set_author(name=_("Name changed"), icon_url=guild.icon_url)
                    await self.core._send_message_to_channel(guild, embed=embed)
                if before.nick != after.nick:
                    embed = discord.Embed(color=self.blue, description="From **{0.nick}** ({0.id}) to **{1.nick}**".format(before, after))
                    if by_mod:
                        embed.set_author(name=_("Nickname changed by {0.display_name}").format(the_mod), icon_url=guild.icon_url)
                    else:
                        embed.set_author(name=_("Nickname changed"), icon_url=guild.icon_url)
                    await self.core._send_message_to_channel(guild, embed=embed)
                if before.roles != after.roles:
                    if len(before.roles) > len(after.roles):
                        for role in before.roles:
                            if role not in after.roles:
                                embed = discord.Embed(color=self.blue, description=_("**{0.display_name}** ({0.id}) lost the **{1.name}** role").format(before, role))
                                if by_mod:
                                    embed.set_author(name=_("Role removed by {0.display_name}").format(the_mod), icon_url=guild.icon_url)
                                else:
                                    embed.set_author(name=_("Role removed"), icon_url=guild.icon_url)
                    elif len(before.roles) < len(after.roles):
                        for role in after.roles:
                            if role not in before.roles:
                                embed = discord.Embed(color=self.blue, description=_("**{0.display_name}** ({0.id}) got the **{1.name}** role").format(before, role))
                                if by_mod:
                                    embed.set_author(name=_("Role applied by {0.display_name}").format(the_mod), icon_url=guild.icon_url)
                                else:
                                    embed.set_author(name=_("Role applied"), icon_url=guild.icon_url)
                    await self.core._send_message_to_channel(guild, embed=embed)

    async def on_message_delete(self, message):
        guild = message.guild
        author = message.author
        channel = message.channel
        timestamp = datetime.utcnow()
        if await dh.is_not_private(channel):
            if await self.core._ignore(guild, author=author, channel=channel):
                if await self.core._validate_event(guild) and author.id != self.bot.user.id:
                    by_mod = False
                    the_mod = False
                    async for entry in guild.audit_logs(limit=1):
                        if entry.action is discord.AuditLogAction.message_delete:
                            the_mod = entry.user
                            by_mod = True
                    embed = discord.Embed(color=self.red)
                    avatar = author.avatar_url if author.avatar else author.default_avatar_url
                    if by_mod:
                        embed.set_author(name=_("Message removed by a moderator"), icon_url=avatar)
                    else:
                        embed.set_author(name=_("Message removed"), icon_url=avatar)
                    embed.add_field(name=_("Message ID"), value=message.id)
                    embed.add_field(name=_("Member"), value="{0.display_name}#{0.discriminator} ({0.id})".format(author))
                    embed.add_field(name=_("Channel"), value=message.channel.name)
                    if the_mod:
                        embed.add_field(name=_("Moderator"), value=the_mod.display_name, inline=False)
                    embed.add_field(name=_("Message timestamp"), value=message.created_at.strftime("%Y-%m-%d %H:%M:%S"))
                    embed.add_field(name=_("Removal timestamp"), value=timestamp.strftime("%Y-%m-%d %H:%M:%S"))
                    if message.content:
                        embed.add_field(name=_("Message"), value=message.content, inline=False)
                    await self.core._send_message_to_channel(guild, embed=embed)
                    if message.attachments:
                        for attachment in message.attachments:
                            filename = await self.core.downloadattachment(attachment.url, attachment.filename, message.id)
                            message = _("Attachment file for message: {}".format(message.id))
                            await self.core._send_message_to_channel(guild, content=message, attachment="cogs/grenzpolizei/attachments/{}".format(filename))
                            os.remove("cogs/grenzpolizei/attachments/{}".format(filename))

    async def on_message_edit(self, before, after):
        guild = after.guild
        author = after.author
        channel = after.channel
        if await dh.is_not_private(channel):
            if await self.core._ignore(guild, author=author, channel=channel):
                if await self.core._validate_event(guild) and author.id != self.bot.user.id and before.clean_content != after.clean_content:
                    embed = discord.Embed(color=self.blue)
                    avatar = author.avatar_url if author.avatar else author.default_avatar_url
                    embed.set_author(name=_("Message changed"), icon_url=avatar)
                    embed.add_field(name=_("Member"), value="{0.display_name}#{0.discriminator}\n({0.id})".format(author))
                    embed.add_field(name=_("Channel"), value=before.channel.name)
                    embed.add_field(name=_("Message timestamp"), value=before.created_at.strftime("%Y-%m-%d %H:%M:%S"))
                    embed.add_field(name=_("Edit timestamp"), value=after.edited_at.strftime("%Y-%m-%d %H:%M:%S"))
                    embed.add_field(name=_("Before"), value=before.content, inline=False)
                    embed.add_field(name=_("After"), value=after.content, inline=False)
                    await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_channel_create(self, channel):
        if await dh.is_not_private(channel):
            guild = channel.guild
            if await self.core._validate_event(guild):
                async for entry in guild.audit_logs(limit=1):
                    if entry.action is discord.AuditLogAction.channel_create:
                        the_mod = entry.user
                embed = discord.Embed(color=self.green)
                embed.set_author(name=_("A new channel has been created by {0.display_name}: #{1.name}").format(the_mod, channel), icon_url=guild.icon_url)
                await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_channel_delete(self, channel):
        if await dh.is_not_private(channel):
            guild = channel.guild
            if await self.core._validate_event(guild):
                async for entry in guild.audit_logs(limit=1):
                    if entry.action is discord.AuditLogAction.channel_delete:
                        the_mod = entry.user
                embed = discord.Embed(color=self.red)
                embed.set_author(name=_("A channel has been deleted by {0.display_name}: #{1.name}").format(the_mod, channel), icon_url=guild.icon_url)
                await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_channel_update(self, before, after):
        channel = after
        if await dh.is_not_private(channel):
            guild = after.guild
            if await self.core._validate_event(guild):
                async for entry in guild.audit_logs(limit=1):
                    if entry.action is discord.AuditLogAction.channel_update:
                        the_mod = entry.user
                if before.name != after.name:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_("#{0.name} renamed to #{1.name} by {2.display_name}").format(before, after, the_mod), icon_url=guild.icon_url)
                    await self.core._send_message_to_channel(guild, embed=embed)
                if not await dh.is_voice(channel):
                    if before.topic != after.topic:
                        embed = discord.Embed(color=self.blue)
                        embed.set_author(name=_("#{0.name} topic changed from \'{0.topic}\' to \'{1.topic}\'").format(before, after), icon_url=guild.icon_url)
                        await self.core._send_message_to_channel(guild, embed=embed)
                if before.position != after.position:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_("#{0.name} moved from {0.position} to {1.position}").format(before, after), icon_url=guild.icon_url)
                    await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_role_create(self, role):
        guild = role.guild
        if await self.core._validate_event(guild):
            async for entry in guild.audit_logs(limit=1):
                if entry.action is discord.AuditLogAction.role_create:
                    the_mod = entry.user
            embed = discord.Embed(color=self.green)
            embed.set_author(name=_("Role created by {0.display_name}: {1.name}").format(the_mod, role), icon_url=guild.icon_url)
            await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_role_delete(self, role):
        guild = role.guild
        if await self.core._validate_event(guild):
            async for entry in guild.audit_logs(limit=1):
                if entry.action is discord.AuditLogAction.role_delete:
                    the_mod = entry.user
            embed = discord.Embed(color=self.red)
            embed.set_author(name=_("Role deleted by {0.display_name}: {1.name}").format(the_mod, role), icon_url=guild.icon_url)
            await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_role_update(self, before, after):
        guild = after.guild
        if await self.core._validate_event(guild):
            the_mod = None
            async for entry in guild.audit_logs(limit=1):
                if entry.action is discord.AuditLogAction.role_update:
                    the_mod = entry.user
            if before.name != after.name:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_("Role {0.name} renamed to {1.name} by {2.display_name}").format(before, after, the_mod), icon_url=guild.icon_url)
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.color != after.color:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_("Role color '{0.name}' changed from {0.color} to {1.color} by {2.display_name}").format(before, after, the_mod), icon_url=guild.icon_url)
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.mentionable != after.mentionable:
                embed = discord.Embed(color=self.blue)
                if after.mentionable:
                    embed.set_author(name=_("{0.display_name} made role '{1.name}' mentionable").format(the_mod, after), icon_url=guild.icon_url)
                else:
                    embed.set_author(name=_("{0.display_name} made role  '{1.name}' unmentionable").format(the_mod, after), icon_url=guild.icon_url)
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.hoist != after.hoist:
                embed = discord.Embed(color=self.blue)
                if after.hoist:
                    embed.set_author(name=_("{0.display_name} made role '{1.name}' to be shown seperately").format(the_mod, after), icon_url=guild.icon_url)
                else:
                    embed.set_author(name=_("{0.display_name} made role '{1.name}' to be shown seperately").format(the_mod, after), icon_url=guild.icon_url)
            if before.permissions != after.permissions:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_("Role permissions '{0.name}' changed from {0.permissions.value} to {1.permissions.value} by {2.display_name}").format(before, after, the_mod), icon_url=guild.icon_url)
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.position != after.position:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_("Role position '{0}' changed from {0.position} to {1.position} by {2.display_name}").format(before, after, the_mod), icon_url=guild.icon_url)
                await self.core._send_message_to_channel(guild, embed=embed)

    async def on_guild_update(self, before, after):
        guild = after
        if await self.core._validate_event(guild):
            async for entry in guild.audit_logs(limit=1):
                if entry.action is discord.AuditLogAction.guild_update:
                    the_mod = entry.user
            if before.owner != after.owner:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_("Server owner changed from {0.owner.name} (id {0.owner.id})"
                                        "to {1.owner.name} (id {1.owner.id}) by {2.display_name}").format(before, after, the_mod), icon_url=guild.icon_url)
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.region != after.region:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_("Server region changed from {0.region} to {1.region} by {2.display_name}").format(before, after, the_mod), icon_url=guild.icon_url)
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.name != after.name:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_("Server name changed from {0.name} to {1.name} by {2.display_name}").format(before, after, the_mod), icon_url=guild.icon_url)
                await self.core._send_message_to_channel(guild, embed=embed)
            if before.icon_url != after.icon_url:
                embed = discord.Embed(color=self.blue)
                embed.set_author(name=_("Server icon changed from {0.icon_url} to {1.icon_url} by {2.display_name}").format(before, after, the_mod), icon_url=guild.icon_url)
                await self.core._send_message_to_channel(guild, embed=embed)

    async def on_voice_state_update(self, author, before, after):
        guild = author.guild
        if await self.core._ignore(guild, author=author):
            if await self.core._validate_event(guild):
                if not before.afk and after.afk:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_("{0.display_name} is idle and has been sent to #{1.channel}").format(author, after), icon_url=author.avatar_url)
                    await self.core._send_message_to_channel(guild, embed=embed)
                elif before.afk and not after.afk:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_("{0.display_name} is active again in #{1.channel}").format(author, after), icon_url=author.avatar_url)
                    await self.core._send_message_to_channel(guild, embed=embed)
                if not before.self_mute and after.self_mute:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_("{0.display_name} muted themselves in #{1.channel}").format(author, after), icon_url=author.avatar_url)
                    await self.core._send_message_to_channel(guild, embed=embed)
                elif before.self_mute and not after.self_mute:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_("{0.display_name} unmuted themselves in #{1.channel}").format(author, after), icon_url=author.avatar_url)
                    await self.core._send_message_to_channel(guild, embed=embed)
                if not before.self_deaf and after.self_deaf:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_("{0.display_name} deafened themselves in #{1.channel}").format(author, after), icon_url=author.avatar_url)
                    await self.core._send_message_to_channel(guild, embed=embed)
                elif before.self_deaf and not after.self_deaf:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_("{0.display_name} undeafened themselves in #{1.channel}").format(author, after), icon_url=author.avatar_url)
                    await self.core._send_message_to_channel(guild, embed=embed)
                if not before.channel and after.channel:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_("{0.display_name} joined voice channel #{1.channel}").format(author, after), icon_url=author.avatar_url)
                    await self.core._send_message_to_channel(guild, embed=embed)
                elif before.channel and not after.channel:
                    embed = discord.Embed(color=self.blue)
                    embed.set_author(name=_("{0.display_name} left voice channel #{1.channel}").format(author, before), icon_url=author.avatar_url)
                    await self.core._send_message_to_channel(guild, embed=embed)
