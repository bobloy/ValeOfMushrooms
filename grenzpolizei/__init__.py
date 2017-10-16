from .grenzpolizei import Grenzpolizei


def setup(bot):
    bot.add_cog(Grenzpolizei(bot))
