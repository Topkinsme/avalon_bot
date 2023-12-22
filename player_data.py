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
import time
from constants import *

class Player:

    def __init__(self,bot,id,mode):
        self.bot=bot
        self.id=id
        self.user=discord.utils.get(self.bot.server.members, id=id)
        self.mode=mode
        self.start=False
        self.role=None
        self.order=None
        self.loyalty=None
        self.checked=False
    




