from discord.ext import commands
from cogs.utils.dataIO import dataIO
import discord
import os
import asyncio


class Seen:
    '''Check when someone was last seen.'''
    def __init__(self, bot):
        self.bot = bot
        self.seen = dataIO.load_json("data/seen/seen.json")
        self.new_data = False

    async def listener(self, message):
        if not message.channel.is_private and self.bot.user.id != message.author.id:
            server = message.server
            channel = message.channel
            author = message.author
            ts = message.timestamp
            data = {}
            data['TIMESTAMP'] = '{} {}:{}:{}'.format(ts.date(), ts.hour, ts.minute, ts.second)
            data['MESSAGE'] = message.clean_content
            data['CHANNEL'] = channel.id
            if server.id not in self.seen:
                self.seen[server.id] = {}
            self.seen[server.id][author.id] = data
            self.new_data = True

    @commands.command(pass_context=True, no_pm=True, name='seen')
    async def _seen(self, context, username: discord.Member):
        '''seen <@username>'''
        server = context.message.server
        author = username
        if server.id in self.seen and author.id in self.seen[server.id]:
            data = self.seen[server.id][author.id]
            ts = data['TIMESTAMP']
            last_message = data['MESSAGE']
            channel = data['CHANNEL']
            em = discord.Embed(description='\a\n{}'.format(last_message), color=discord.Color.green())
            avatar = author.avatar_url if author.avatar else author.default_avatar_url
            em.set_author(name='{} was last seen on {} UTC'.format(author.display_name, ts), icon_url=avatar)
            em.add_field(name='\a', value='**Channel:** {}'.format(channel))
            await self.bot.say(embed=em)
        else:
            message = 'I haven\'t seen {} yet.'.format(author.display_name)
            await self.bot.say('{}'.format(message))

    async def data_writer(self):
        while self == self.bot.get_cog("Seen"):
            if self.new_data:
                await asyncio.sleep(60)
                print("Writing data to seen.json")
                dataIO.save_json("data/seen/seen.json", self.seen)
                self.new_data = False
            else:
                await asyncio.sleep(30)


def check_folder():
    if not os.path.exists('data/seen'):
        print('Creating data/seen folder...')
        os.makedirs('data/seen')


def check_file():
    if not dataIO.is_valid_json("data/seen/seen.json"):
        print("Creating seen.json...")
        dataIO.save_json("data/seen/seen.json", {})


def setup(bot):
    check_folder()
    check_file()
    n = Seen(bot)
    bot.add_listener(n.listener, 'on_message')
    loop = asyncio.get_event_loop()
    loop.create_task(n.data_writer())
    bot.add_cog(n)
