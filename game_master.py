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
import typing
import copy
import io
import textwrap

class GM(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.hybrid_command()
    @commands.has_role("Game Master")
    async def poll(self,ctx:commands.Context,*,message:str):
        '''Creates a poll <Game master>'''
        poll = discord.Embed(colour=discord.Colour.blurple())
        poll.set_author(name="POLL")
        poll.add_field(name="Reg:- ",value=message,inline="false")
        poll.add_field(name="YES- ",value=" ",inline="false")
        poll.add_field(name="NO- ",value=" ",inline="false")
        poll.add_field(name="MAYBE- ",value=" ",inline="false")

        class Vote(discord.ui.View):
            def __init__(self,msg):
                super().__init__(timeout=None)
                self.yes_who=[]
                self.no_who=[]
                self.maybe_who=[]
                self.msg=msg

            @discord.ui.button(emoji='👍', style=discord.ButtonStyle.green)
            async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user in self.yes_who+self.no_who+self.maybe_who:
                    await interaction.response.send_message('You have already voted.', ephemeral=True)
                else:
                    self.yes_who.append(interaction.user)
                    poll.set_field_at(1,name="YES- ",value=f"({str(len(self.yes_who))})- "+",".join([x.name for x in self.yes_who]),inline="false")
                    await interaction.response.send_message('Voting yes.', ephemeral=True)
                    await self.msg.edit(embed=poll)


            @discord.ui.button(emoji='👎', style=discord.ButtonStyle.red)
            async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user in self.yes_who+self.no_who+self.maybe_who:
                    await interaction.response.send_message('You have already voted.', ephemeral=True)
                else:
                    self.no_who.append(interaction.user)
                    poll.set_field_at(2,name="NO- ",value=f"({str(len(self.no_who))})- "+",".join([x.name for x in self.no_who]),inline="false")
                    await interaction.response.send_message('Voting no.', ephemeral=True)
                    await self.msg.edit(embed=poll)

            @discord.ui.button(emoji='⛔', style=discord.ButtonStyle.grey)
            async def maybe(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user in self.yes_who+self.no_who+self.maybe_who:
                    await interaction.response.send_message('You have already voted.', ephemeral=True)
                else:
                    self.maybe_who.append(interaction.user)
                    poll.set_field_at(3,name="MAYBE- ",value=f"({str(len(self.maybe_who))})- "+",".join([x.name for x in self.maybe_who]),inline="false")
                    await interaction.response.send_message('Voting maybe.', ephemeral=True)
                    await self.msg.edit(embed=poll)

        msg=await ctx.send("Loading.")
        view = Vote(msg)
        await msg.edit(content="",embed=poll, view=view)
        await view.wait()
        

async def setup(bot):
    await bot.add_cog(GM(bot=bot))