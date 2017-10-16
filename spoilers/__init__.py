from .spoilers import Spoilers


def setup(bot):
    bot.add_cog(Spoilers(bot))
