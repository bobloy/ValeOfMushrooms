from discord.ext import commands
from core.i18n import CogI18n
import aiohttp
import re

_ = CogI18n("YouTube", __file__)


class YouTube:
    def __init__(self, bot):
        self.bot = bot
        self.youtube_regex = (
          r"(https?://)?(www\.)?"
          "(youtube|youtu|youtube-nocookie)\.(com|be)/"
          "(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})")

    async def _api_request(self, query):
        url = "https://www.youtube.com/results?"
        payload = {"search_query": "".join(query)}
        session = aiohttp.ClientSession()
        async with session.get(url, params=payload) as r:
            data = await r.text()
        session.close()
        yt_find = re.findall(r"href=\"\/watch\?v=(.{11})", data)
        if yt_find:
            message = "https://www.youtube.com/watch?v={}".format(yt_find[0])
        else:
            message = _("Couldn't find anything!")
        return message

    @commands.command(pass_context=True, name='youtube', no_pm=True)
    async def _youtube(self, context, *, query: str):
        channel = context.channel
        video = await self._api_request(query)
        await channel.send(video)
