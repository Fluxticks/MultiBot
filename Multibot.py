import json
import discord
from discord.ext import commands
import bot_util as bt
import sys
import os
import signal

class BotClient(commands.Bot):

    _channels = ['multibot-roles', 'multibot-music']

    async def on_ready(self):
        bt.SETUP('Logging In')
        bt.SETUP(f'\t name: {self.user.name}')
        bt.SETUP(f'\t id: {self.user.id}')
        bt.SETUP(f'\t guilds: {len(self.guilds)}')
        #bt.SETUP(f'\t cogs: {cogs}')
        self.load_data()
        print('--------------------------------')

    async def on_raw_reaction_add(self, payload):
        cog = self.get_cog('Roles')
        await cog.on_reaction(payload)

    @property
    def channels(self):
        return self._channels

    def load_data(self):
        data = load_data('data')
        if data is None:
            return

        react = {}
        music = {}
        category = {}

        for key in data.keys():
            music[key] = data[key]["music"]
            category[key] = data[key]["category"]
            react[key] = data[key]["react"]

        #bt.dprint(react)
        #bt.dprint(music)
        #bt.dprint(category)

        self.get_cog('Music').channels = music
        self.get_cog('Roles').channels = react
        self.get_cog('Misc').categories = category

    def gather_data(self):
        bt.INFO('Getting data')
        keys = [str(x.id) for x in self.guilds]
        roles = self.get_cog('Roles').channels
        category = self.get_cog('Misc').categories
        music = self.get_cog('Music').channels

        data = {}

        for key in keys:
            data[key] = {}

        for key in keys:
            data[key]["react"] = roles[key]
            data[key]["music"] = music[key]
            data[key]["category"] = category[key]

        with open('data.json', 'w') as f:
            json.dump(data, f)

bot = BotClient(command_prefix=commands.when_mentioned_or("!"), description="A multi-purpose bot")

list_extensions = ['Roles', 'Music', 'Misc']

@bot.command()
@commands.has_permissions(administrator=True)
async def reload(ctx):
    """Reloads the bots commands, Usage !reload"""
    bt.WARN('Reloading Extensions!')
    reload_extensions()
    bot.load_data()
    message = await ctx.send(embed=bt.embed_message('Done Reloading!', colour='green'))
    await message.delete(delay=3.0)
    bt.INFO('Done Reloading Extensions!')

def extensions(method):
    for extension in list_extensions:
        method(extension)

def load_extensions():
    extensions(bot.load_extension)

def reload_extensions():
    extensions(bot.reload_extension)

def keyboardInterruptHandler(signal, frame):
    bt.INFO('Doing cleanup')
    bot.gather_data()
    bt.INFO('Cleanup done!')
    exit(0)

def load_data(file):
    if '.json' not in file:
        file += '.json'
    try:
        with open(file, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        bt.ERROR(f'Unable to find file: {file}')
        return None

load_extensions()
signal.signal(signal.SIGINT, keyboardInterruptHandler)
#bot.run('NjgzMzYxMTg1OTc3OTkxMzAw.Xlqbyg.RAl2fKwwQfFV1eRageY1cOe8h2M')
bot.run('NjgzMzYxMTg1OTc3OTkxMzAw.XoII1Q.tLyAMRQUzB_hXabUrjTdmPhuxlA')