#code by top

import json
import discord
from discord.utils import get
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands import Bot
from discord.ext.commands import Greedy
from discord import Interaction
from discord.app_commands import AppCommandError
import logging
import asyncio
from constants import *


class Events(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot=bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is online!")
        await self.bot.change_presence(activity=discord.Game(name="Avalon: The resistance", type=1))
        self.bot.server=self.bot.get_guild(server_id)
        self.bot.owner_id=owner_id
        self.bot.lobby = self.bot.get_channel(lobby_id) 
        self.bot.peochannel = self.bot.get_channel(peochannel_id)
        self.bot.annchannel = self.bot.get_channel(annchannel_id)
        self.bot.signed_up_role=discord.utils.get(self.bot.server.roles, id=signed_up_id)
        self.bot.player_role=discord.utils.get(self.bot.server.roles, id=players_id)
        await self.bot.annchannel.send("Bot is online!")

    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        await ctx.send(error)

async def setup(bot):
    await bot.add_cog(Events(bot=bot))