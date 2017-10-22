from redbot.core.data_manager import cog_data_path
from .grenzpolizei import Grenzpolizei
from .utils.dataIO import dataIO
import os

DB_VERSION = 3
COG_FOLDER = str(cog_data_path()) + '\\data'
COG = '\\grenzpolizei\\'


def check_folder():
    if not os.path.exists(COG_FOLDER + COG):
        print('Creating data/grenzpolizei folder...')
        os.makedirs(COG_FOLDER + COG)


def check_file():
    data = {}

    data['db_version'] = DB_VERSION
    settings_file = COG_FOLDER + COG + 'settings.json'
    ignore_file = COG_FOLDER + COG + 'ignore.json'
    if not dataIO.is_valid_json(settings_file):
        print('Creating default settings.json...')
        dataIO.save_json(settings_file, data)
    else:
        check = dataIO.load_json(settings_file)
        if 'db_version' in check:
            if check['db_version'] < DB_VERSION:
                data = {}
                data['db_version'] = DB_VERSION
                print('GRENZPOLIZEI: Database version too old, please rerun the setup!')
                dataIO.save_json(settings_file, data)

    if not dataIO.is_valid_json(ignore_file):
        print('Creating default ignore.json...')
        dataIO.save_json(ignore_file, {})


def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(Grenzpolizei(bot))
