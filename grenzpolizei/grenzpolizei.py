import discord
from redbot.core import checks
from redbot.core.i18n import CogI18n
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
