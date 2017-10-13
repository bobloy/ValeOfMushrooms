from core.bot import Red
from .grenzpolizei import Grenzpolizei


def setup(bot: Red):
    bot.add_cog(Grenzpolizei(bot))
