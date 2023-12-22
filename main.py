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
from constants import token

intents = discord.Intents.all()

bot = commands.Bot(command_prefix = ";",intents=intents)
logging.basicConfig(level=logging.INFO)


@bot.hybrid_command()
@commands.is_owner()
async def reload(ctx:commands.Context):
  '''Use this to reload all commands! <Owner only>'''
  cogs=["events","admin","game_master","misc","game_commands","player_commands"]
  for cog in cogs:
      await bot.reload_extension(cog)
  await ctx.send("All cogs reloaded!")
   
async def main():  
    async with bot:
      cogs=["events","admin","game_master","misc","game_commands","player_commands"]
      for cog in cogs:
        await bot.load_extension(cog)
      await bot.start(token)  

if __name__=="__main__":
  asyncio.run(main())
