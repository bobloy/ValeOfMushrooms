import discord

from core.i18n import CogI18n
import asyncio

import psutil
import ipgetter
from aiohttp import web
import aiohttp_jinja2
import jinja2

from .utils.dataIO import dataIO

_ = CogI18n('Statistics', __file__)


class Statistics:
    def __init__(self, bot):
        self.bot = bot
        self.settings_file = 'cogs/statistics/settings/settings.json'
        self.settings = dataIO.load_json(self.settings_file)

        self.server_ip = ipgetter.myip()
        self.server_port = self.settings['server_port']

        self.app = web.Application()

        self.server = None
        self.handler = None
        self.dispatcher = {}

        self.bot.loop.create_task(self.make_webserver())

    async def retrieve_statistics(self):
        name = self.bot.user.name
        users = str(len(set(self.bot.get_all_members())))
        servers = str(len(self.bot.servers))
        commands_run = self.bot.counter['processed_commands']
        read_messages = self.bot.counter['messages_read']
        text_channels = 0
        voice_channels = 0

        process = psutil.Process()

        cpu_usage = psutil.cpu_percent()

        mem_v = process.memory_percent()
        mem_v_mb = process.memory_full_info().uss
        threads = process.num_threads()

        io_reads = process.io_counters().read_count
        io_writes = process.io_counters().write_count

        for channel in self.bot.get_all_channels():
            if channel.type == discord.ChannelType.text:
                text_channels += 1
            elif channel.type == discord.ChannelType.voice:
                voice_channels += 1
        channels = text_channels + voice_channels

        stats = {
            'name': name, 'users': users, 'total_servers': servers, 'commands_run': commands_run,
            'read_messages': read_messages, 'text_channels': text_channels,
            'voice_channels': voice_channels, 'channels': channels,
            'cpu_usage': cpu_usage, 'mem_v': mem_v, 'mem_v_mb': mem_v_mb, 'threads': threads,
            'io_reads': io_reads, 'io_writes': io_writes}
        return stats

    @aiohttp_jinja2.template('index.tpl')
    def page(req):
        response = aiohttp_jinja2.render_template('index.tpl', req, {'k': 'v'})
        return response

    async def make_webserver(self):

        await asyncio.sleep(10)

        aiohttp_jinja2.setup(self.app, loader=jinja2.FileSystemLoader('/cogs/statistics/template'))

        self.app.router.add_get('GET', '/', page)
        self.handler = self.app.make_handler()

        self.server = await self.bot.loop.create_server(self.handler, '0.0.0.0', self.server_port)

        message = 'Serving Web Statistics on http://{}:{}'.format(self.server_ip, self.server_port)

        print(message)
