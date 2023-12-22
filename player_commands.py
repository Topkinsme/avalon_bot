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

class Player(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

async def setup(bot):
    await bot.add_cog(Player(bot=bot))