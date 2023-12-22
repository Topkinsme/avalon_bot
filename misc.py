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


class Misc(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.hybrid_command()
    async def ping(self,ctx:commands.Context):
        '''Use to make sure the bot is online!'''
        await ctx.send("PING")

async def setup(bot):
    await bot.add_cog(Misc(bot=bot))