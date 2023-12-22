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

class Admin(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.hybrid_command()
    @commands.is_owner()
    @commands.guild_only()
    async def sync(self,ctx: commands.Context, guilds: Greedy[discord.Object], spec: typing.Optional[typing.Literal["~", "*", "^"]] = None) -> None:
        '''Use this command to sync your slash comamnds.

        !sync -> global sync
        !sync ~ -> sync current guild
        !sync * -> copies all global app commands to current guild and syncs
        !sync ^ -> clears all commands from the current guild target and syncs (removes guild commands)
        !sync id_1 id_2 -> syncs guilds with id 1 and 2'''
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @commands.hybrid_command()
    @commands.has_role("Admin")
    async def sudo(self,ctx:commands.Context,who: discord.User, *,command: str):
            """Run a command as another user optionally in another channel."""
            msg = copy.copy(ctx.message)
            channel = ctx.channel
            msg.channel = channel
            msg.author = channel.guild.get_member(who.id) or who
            msg.content = ctx.prefix + command
            new_ctx = await self.bot.get_context(msg, cls=type(ctx))
            #new_ctx._db = ctx._db
            await self.bot.invoke(new_ctx)
    
    @commands.hybrid_command(hidden=True)
    @commands.is_owner()
    async def evall(self,ctx:commands.Context,*,thing:str):
        '''Eval command <owner>'''
        env = {
                'bot': self.bot,
                'ctx': ctx,
                'channel': ctx.channel,
                'author': ctx.author,
                'guild': ctx.guild,
                'message': ctx.message,
            }

        env.update(globals())
        stdout = io.StringIO()
        if thing.startswith('```') and thing.endswith('```'):
                a = '\n'.join(thing.split('\n')[1:-1])
                thing = a.strip('` \n')
        to_compile = f'async def func():\n{textwrap.indent(thing, "  ")}'
        try:
                exec(to_compile, env)
        except Exception as e:
                await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
        func = env['func']
        try:
            ret = await func()
        except Exception as e:
                value = stdout.getvalue()
                await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
        else:
                value = stdout.getvalue()
                try:
                    await ctx.message.add_reaction('\u2705')
                except:
                    pass

                if ret is None:
                    if value:
                        await ctx.send(f'```py\n{value}\n```')
                else:
                    await ctx.send(f'```py\n{value}{ret}\n```')

    @commands.hybrid_command()
    @commands.has_role("Admin")
    async def logout(self,ctx: commands.Context):
        '''Logs out the bot'''
        await ctx.send("Logging out.", ephemeral=True)
        await self.bot.close()


async def setup(bot):
    await bot.add_cog(Admin(bot=bot))