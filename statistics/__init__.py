from .statistics import Statistics


def setup(bot):
    bot.add_cog(Statistics(bot))
