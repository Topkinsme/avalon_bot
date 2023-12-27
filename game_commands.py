#code by top

import json
import discord
from discord.utils import get
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands import Bot
from discord.ext.commands import Greedy
from discord.ext.commands.cooldowns import BucketType
from discord import Interaction
from discord.app_commands import AppCommandError
from discord.ui import Select
import logging
import asyncio
import datetime
import random
from typing import Any
from datetime import timedelta
from constants import *
from game_data import Game
from player_data import Player

class Game_Cmds(commands.Cog):
    def __init__(self,bot):
        '''Init class of came commands.
        State 0= No lobby
        1=Lobby
        2=Game start
        3=Team selection
        4=Adventure
        5=Lady Of Luck
        6=Assassin
        
        '''
        self.bot=bot
        self.bot.game_data=self
        self.state=0
        self.game=None
        self.timeoutloop.start()

    @tasks.loop(minutes=1)
    async def timeoutloop(self):
        if self.game==None or self.state!=1:
            pass
        else:
            if datetime.datetime.now()-self.game.lobby_start_time>timedelta(minutes=30):
                await self.lsender("The game has taken too long to start! Lobby deleted. ","",self.bot.signed_up_role.mention)
                for player in self.game.players:
                    await player.user.remove_roles(self.bot.signed_up_role)
                self.state=0
                self.game=None
                
    async def lsend(self,msg1,msg2="",msg0=""):
        '''Use this function to send a successful message to lobby'''
        message=discord.Embed(color=discord.Color.blue())
        message.add_field(name=msg1,value=msg2)
        await self.bot.lobby.send(msg0,embed=message)

    async def lsender(self,msg1,msg2="",msg0=""):
        '''Use this function to send a unsuccessful message to lobby'''
        message=discord.Embed(color=discord.Color.red())
        message.add_field(name=msg1,value=msg2)
        await self.bot.lobby.send(msg0,embed=message)

    async def psend(self,ctx,msg1,msg2="",msg0=""):
        '''Use this function to send a successful message to a person'''
        message=discord.Embed(color=discord.Color.blue())
        message.add_field(name=msg1,value=msg2)
        await ctx.send(msg0,embed=message,ephemeral=True)

    async def psender(self,ctx,msg1,msg2="",msg0=""):
        '''Use this function to send a unsuccessful message to a person'''
        message=discord.Embed(color=discord.Color.red())
        message.add_field(name=msg1,value=msg2)
        await ctx.send(msg0,embed=message,ephemeral=True)

    async def dm(self,person,msg1,msg2="",msg0=""):
        '''Use this function to send a successful direct message to a person'''
        message=discord.Embed(color=discord.Color.blue())
        message.add_field(name=msg1,value=msg2)
        try:
            await person.send(msg0,embed=message)
        except Exception as e:
            print("Cannot dm this user!")
            print(e)


    @commands.hybrid_command()
    async def join(self,ctx:commands.Context,mode:int=2):
        '''Use this command to create a lobby or join an existing lobby.'''
        if mode>5:
            await self.psender(ctx,"Invalid mode.")
            return
        if self.state==0:
            self.state=1
            self.game=Game(self.bot)
            await self.lsend("A new lobby has been created!")
            await self.psend(ctx,"You have joined the game!")
            #notify?
        elif self.state==1:
            if self.game.get_player(ctx.author.id):
                await self.psender(ctx,"You are already in the game!")
                return
            else:
                await self.psend(ctx,"You have joined the game!")
        else:
            await self.psender(ctx,"Either games have been turned off or a game is happening right now. Please wait for another game to start.")
            return
        await ctx.author.add_roles(self.bot.signed_up_role)
        new_player=Player(self.bot,ctx.author.id,mode)
        self.game.add_player(new_player)
        

    @commands.hybrid_command()
    async def lobby(self,ctx:commands.Context):
        '''Use this command to check the lobby members and their mode votes.'''
        if self.state==0:
            await self.psender(ctx,"There's currently no one in the lobby! Use the /join command to create a lobby!")
        else:
            content="\n".join((":white_check_mark:" if x.start else "")+f"<@{str(x.id)}> - Mode {x.mode}" for x in self.game.players)
            await self.psend(ctx,"The players currently in the lobby are-",content)

    @commands.hybrid_command()
    async def leave(self,ctx:commands.Context):
        '''Use this command to leave the lobby.'''
        if self.state>1:
            await self.psender("You cannot leave the lobby mid-game!")
            return
        player=self.game.get_player(ctx.author.id)
        if player:
            self.game.del_player(player)
        else:
            await self.psender(ctx,"You are not currently in the lobby!")
            return
        msg2=""
        if len(self.game.players)<1:
            self.state=0
            self.game=None
            await self.lsender("Lobby has been deleted.")
        await ctx.author.remove_roles(self.bot.signed_up_role)
        await self.psender(ctx,"You have left the lobby.")

    @commands.hybrid_command()
    async def mode(self,ctx:commands.Context,mode:int):
        '''Use this to change the gamemode you voted for.'''
        if self.state>1:
            await self.psender("You cannot change the gamemode vote mid-game!")
            return
        player=self.game.get_player(ctx.author.id)
        if not player:
            await self.psender(ctx,"You are not currently in the lobby!")
            return
        if mode>5:
            await self.psender(ctx,"Invalid mode.")
            return
        player.mode=mode
        await self.psend(ctx,"Mode changed!")

    @commands.hybrid_command()
    async def modes(self,ctx:commands.Context,mode:int=None):
        '''Use this to get modes info.'''
        if not mode:
            await self.psend(ctx,"Mode 0 = Classic. (No special roles.)\nMode 1 = Merlin only.\nMode 2 = Merlin, Percival and Morgana.\nMode 3 = Oberon only.\nMode 4 = Merlin, Percival, Morgana and Mordred.\nMode 5 = All roles.")
        else:
            try:
                await self.psend(ctx,f"Role info for mode {mode}-","\n".join(rolelists[mode]))
            except:
                await self.psender("Invalid mode.")
            

    @commands.hybrid_command()
    @commands.cooldown(1,10,BucketType.user) 
    async def votestart(self,ctx:commands.Context):
        '''Use this to vote to start the game.'''
        if self.state>1:
            await self.psender(ctx,"There is no lobby in waiting.")
            return
        player=self.game.get_player(ctx.author.id)
        if not player:
            await self.psender(ctx,"You are not currently in the lobby!")
            return
        if self.game.playercount<5:
            await self.psender(ctx,"There aren't enough people in this lobby to start the game!")
            return
        if player.start==False:
            player.start=True
            self.game.startcount+=1
        await self.psend(ctx,"You have voted to start the game!")
        if self.game.startcount==len(self.game.players) and self.game.startcount>4:
            self.state=2
            await self.gamestart()
    
    @commands.hybrid_command()
    @commands.cooldown(1,10,BucketType.user) 
    async def unvotestart(self,ctx:commands.Context):
        '''Use this to revoke your vote to start the game.'''
        if self.state>1:
            await self.psender(ctx,"There is no lobby in waiting.")
            return
        player=self.game.get_player(ctx.author.id)
        if not player:
            await self.psender(ctx,"You are not currently in the lobby!")
            return
        if player.start==True:
            player.start=False
            self.game.startcount-=1
        await self.psender(ctx,"You have unvoted to start the game!")

    @commands.hybrid_command()
    async def extend(self,ctx:commands.Context):
        '''Usr this to extend the lobby timeout timer.'''
        if self.state>1:
            await self.psender(ctx,"There is no lobby in waiting.")
            return
        player=self.game.get_player(ctx.author.id)
        if not player:
            await self.psender(ctx,"You are not currently in the lobby!")
            return
        try:
            if datetime.datetime.now()-(self.game.lobby_start_time +timedelta(minutes=5)) < timedelta(minutes=0):
                await self.psender(ctx,"You cannot extend the time beyond 30 mins. Please wait.")
                return
            self.game.lobby_start_time+=timedelta(minutes=5)
            await self.psend(ctx,"Done! The lobby timeout timer has been extended by 5 mins.")
        except:
            await self.psender(ctx,"Lobby empty or a game is going on. Or there was a error.")

    @commands.hybrid_command()
    async def time(self,ctx:commands.Context):
        '''Use this to check how much time is left before the lobby times out.'''
        if self.state>1:
            await self.psender(ctx,"There is no lobby in waiting.")
            return
        try:
            timeo = str(timedelta(minutes=30) - (datetime.datetime.now() - self.game.lobby_start_time))
            await self.psend(ctx,f"{timeo[:-7]} - time left before the lobby is timed out")
        except:
            await self.psend(ctx,"Lobby empty or a game is going on. Or there was a error.")

    async def gamestart(self):
        '''Does the initial stuff of the game'''
        for player in self.game.players:
            await player.user.remove_roles(self.bot.signed_up_role)
            await player.user.add_roles(self.bot.player_role)
        everyone_overwrites = self.bot.lobby.overwrites_for(self.bot.server.default_role)
        everyone_overwrites.update(send_messages=False,read_messages=True)
        await self.bot.lobby.set_permissions(self.bot.server.default_role,overwrite=everyone_overwrites)
        order=list(self.game.players)
        random.shuffle(order)
        num=1
        mode_votes=[]
        for player in order:
            player.order=num
            mode_votes.append(player.mode)
            num+=1
        self.game.rounds=rounds[self.game.playercount-5]
        self.game.lady_of_lake_holder=self.game.playercount
        self.game.mode=max(set(mode_votes), key=mode_votes.count)
        if self.game.mode>2 and self.game.playercount<7:
            await self.lsender("The lobby has less than 7 players! The mode has been set to 2.")
            self.game.mode=2
        else:
            await self.lsend(f"The game is starting with mode {self.game.mode}.")
        rolelist=rolelists[self.game.mode][:self.game.playercount]
        await self.lsend("The role list is-","\n".join(rolelist))
        random.shuffle(rolelist)
        evils=[]
        merlin=None
        morgana=None
        mordred=""
        
        for player in self.game.players:
            player.role=rolelist[player.order-1]
            await self.dm(player.user,
                          f"""This message has been sent to you to inform you of your role in the next upcoming game of Avalon!
                             Your role for this game is `{player.role}`!""",
                            """You are **__not__** allowed to share this message!
                               You are **__not__** allowed to share the screenshot of this message!
                               Breaking any of these rules can result in you being banned from the server.""",
                            "Role Info!")
            if player.role=="Minion of Mordred" or player.role=="Assassin":
                evils.append(player.user.display_name)
            elif player.role=="Merlin":
                merlin=player.user.display_name
            elif player.role=="Morgana":
                morgana=player.user.display_name
                evils.append(player.user.display_name)
            elif player.role=="Mordred":
                mordred=player.user.display_name
        for player in self.game.players:
            if player.role=="Loyal Servant of Arthur":
                player.loyalty="Arthur"
                message="As a *Loyal Servant of Arthur*, you have no idea about who is on your team."
            elif player.role=="Minion of Mordred":
                player.loyalty="Mordred"
                message=f"As a *Minion of Mordred*, your entire team is {','.join(evils)}." + (f"Mordred's identity is {mordred}" if mordred else "")
            elif player.role=="Assassin":
                player.loyalty="Mordred"
                message=f"As *Mordred's trusted assasin*, your entire team is {','.join(evils)}."  + (f"Mordred's identity is {mordred}" if mordred else "")
            elif player.role=="Merlin":
                player.loyalty="Arthur"
                message=f"As the wizard *Merlin*, your powers reveal to you that the minions of Mordred are {','.join(evils)}." +("However, you do not know who Mordred is." if mordred else "")
            elif player.role=="Oberon":
                player.loyalty="Mordred"
                message=f"As *Oberon*, your carelessness has led to your team forgetting you, and you forgetting them. However, Merlin does not know about you either."
            elif player.role=="Percival":
                player.loyalty="Arthur"
                shuffle=[merlin,morgana]
                random.shuffle(shuffle)
                message=f"As *Percival*, your powers tell you that among {shuffle[0]} and {shuffle[1]}, one is Merlin and another is Morgana. You're just not sure who is which."
            elif player.role=="Morgana":
                player.loyalty="Mordred"
                message=f"As *Morgana*, you appear as if you are Merlin to Percival. Your entire team is {','.join(evils)}." + (f"Mordred's identity is {mordred}" if mordred else "")
            elif player.role=="Mordred":
                player.loyalty="Mordred"
                message=f"As a *Mordred* himself, Merlin has no idea about your Identity. Your entire team is {','.join(evils)}, and yourself."
            else:
                message="???"
            await self.dm(player.user,message,
                              """Have a good game!
                                 *I am a bot and this action has been done automatically. Please contact the Game Masters if anything is unclear.*""")
        await self.round()

    @commands.hybrid_command()
    async def order(self,ctx:commands.Context):
        '''Use this command to check the player order'''
        if self.state<2:
            await self.psender(ctx,"There's currently no one in the lobby! Use the /join command to create a lobby!")
        else:
            content="\n".join(f"{emotes[x.order]} <@{str(x.id)}>" for x in sorted(self.game.players,key=lambda x:x.order))
            await self.psend(ctx,"The player order is-",content)


    async def round(self):
        '''Runs a round of avalon if the game is not over.'''
        if self.game.goods==3:
            if self.game.mode in [1,2,4,5]:
                await self.lsend("Aurthur's loyal captains have beaten the odds! But did Merlin reveal too much?? The Assassin can now try to kill Merlin for one last victory chance!","Use /kill to attempt to kill merlin.","")
                self.mode=6
                return
            else:
                await self.lsend("Aurthur's loyal captains have beaten the odds! Mordred and his minions have all been arresed and taken to the gallows!")
                await self.end("A")
                return
        elif self.game.bads==3 or self.game.fails==5:
            await self.lsend("Mordred and his minions have won the game!")
            await self.end("M")
            return
        self.mode=2
        self.game.leader+=1
        self.game.leader=((self.game.leader-1)%self.game.playercount)+1
        leader=self.game.get_player_by_order(self.game.leader)
        await self.board(self.bot.lobby)
        await self.lsend(f"The current leader is {leader.user.display_name}. They need to pick {self.game.rounds[self.game.current_round-1]} people for the next adventure.","Use /team to pick your team.",leader.user.mention)

    @commands.hybrid_command()
    async def team(self,ctx:commands.Context):
        '''Use this command to select the adventure team.'''
        if self.mode!=2:
            await self.psender(ctx,"Incorrect phase time.")
            return
        else:
            self.mode=3
        leader=self.game.get_player_by_order(self.game.leader).user
        if ctx.author!=leader:
            await self.psender(ctx,"You are not the current leader!")
            self.mode=2
            return
        self.game.tempteam=[]
        class SelectCus(Select):
            def __init__(self,master):
                self.master=master
                super().__init__(placeholder="Select adventureres....",
                                 min_values=self.master.game.rounds[self.master.game.current_round-1],
                                 max_values=self.master.game.rounds[self.master.game.current_round-1],
                                 options=[discord.SelectOption(label=f"{x.order} {x.user.name}",value=x.order) for x in sorted(self.master.game.players,key=lambda x:x.order)]) 
                
            async def callback(self, interaction: discord.Interaction) -> Any:
                if interaction.user.id!=ctx.author.id:
                    await interaction.response.send_message("You are not the current party leader!",ephemeral=True)
                else:
                    self.master.game.tempteam=[self.master.game.get_player_by_order(int(x)).user for x in self.values]
                    await interaction.response.send_message("Selection successful.",ephemeral=True)
                    self.view.stop()


        class View(discord.ui.View):
                    def __init__(self,master):
                        super().__init__(timeout=30)
                        self.add_item(SelectCus(master))

        teamview=View(self)
        await ctx.send(view=teamview,ephemeral=True)
        await teamview.wait()
        if len(self.game.tempteam)!=self.game.rounds[self.game.current_round-1]:
            await self.psender(ctx,"Incorrect team size/selection timed out. Please rerun the /team command.")
            self.mode=2
            return

        await self.lsend("The leader has choosen "+",".join([x.display_name for x in self.game.tempteam])+" as your team! Vote below if you approve of this team or not!")
        class Nom(discord.ui.View):
            def __init__(self,master):
                self.master=master
                super().__init__(timeout=60)
                self.yes_who = []
                self.no_who = []

            @discord.ui.button(emoji='✅', style=discord.ButtonStyle.green)
            async def yes(self, interaction: discord.Interaction,button: discord.ui.Button):
                if interaction.user.id not in list([x.user.id for x in self.master.game.players]):
                    await interaction.response.send_message('**PLEASE DO NOT ATTEMPT TO VOTE IF YOU ARE NOT PART OF THE GAME.**',ephemeral=True)
                else:
                    self.no_who.remove(interaction.user) if interaction.user in self.no_who else None
                    self.yes_who.append(interaction.user) if interaction.user not in self.yes_who else None
                    await interaction.response.send_message('Voting yes.', ephemeral=True)
                    await self.cstop()

            @discord.ui.button(emoji='❎', style=discord.ButtonStyle.red)
            async def no(self, interaction: discord.Interaction,button: discord.ui.Button):
                if interaction.user.id not in list([x.user.id for x in self.master.game.players]):
                    await interaction.response.send_message('**PLEASE DO NOT ATTEMPT TO VOTE IF YOU ARE NOT PART OF THE GAME.**',ephemeral=True)
                else:
                    self.yes_who.remove(interaction.user) if interaction.user in self.yes_who else None
                    self.no_who.append(interaction.user) if interaction.user not in self.no_who else None
                    await interaction.response.send_message('Voting no.', ephemeral=True)
                    await self.cstop()

            async def cstop(self):
                if len(self.yes_who + self.no_who) == len(self.master.game.players):
                    self.stop()

        voteview = Nom(self)
        await self.bot.lobby.send(view=voteview)
        await voteview.wait()
        yes = len(voteview.yes_who)
        no = len(voteview.no_who)
        yeswho = " ".join([f"{userr.mention} " for userr in voteview.yes_who])
        nowho = " ".join([f"{userr.mention} " for userr in voteview.no_who])
        await self.lsend("Results-",f"({int(yes)}) YES- {yeswho}\n({int(no)}) NO- {nowho}")
        if yes > no:
            self.game.team=self.game.tempteam
            await self.adventureapprove()
        else:
            await self.adventuredisapprove()

    async def adventureapprove(self):
        '''This function is fun when there is an adventure.'''
        self.mode=4
        self.game.fails=0
        await self.lsend("The group was approved! All the party members now have recieved their choice cards. Vote carefully. Once everyone votes, the results will be sent here.")
        class Choice(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=20)
                self.choice=1

            @discord.ui.button(emoji='✅', style=discord.ButtonStyle.green)
            async def yes(self, interaction: discord.Interaction,button: discord.ui.Button):
                self.choice=1
                await interaction.response.send_message('Helping out the group.')
                await self.cstop()

            @discord.ui.button(emoji='❎', style=discord.ButtonStyle.red)
            async def no(self, interaction: discord.Interaction,button: discord.ui.Button):
                self.choice=0
                await interaction.response.send_message('Sabotaging the group.')
                await self.cstop()

            async def cstop(self):
                self.stop()

        votes=[]
        success=0
        fails=0
        for player in self.game.team:
            choiceview = Choice()
            try:
                await player.send("Select your choice! Do you want to help the team succeed? Or not help them and watch them fail? Vote ✅ to help them out and ❎ to doom them.",view=choiceview)
            except:
                print("CANNOT DM THIS USER!")
            await choiceview.wait()
            if choiceview.choice==1:
                success+=1
            else:
                fails+=1
        await self.lsend(f"""The adventure is now over. There {"were" if success!=1 else "was"} {success} {"people" if success!=1 else "person"} trying to beat the dungeon, and {fails} {"people" if fails!=1 else "person"} trying to sabotage the mission.""")
        if self.game.playercount>6 and self.game.current_round==4:
            if fails>1:
                await self.adventurefail()
            elif fails>0:
                await self.lsend("But since in a game of 7 or more people, the 4th adventure requires 2 fails, this adventure wasn't sabotaged successfully.")
                await self.adventuresuccess()
            else:
                await self.adventuresuccess()
        else:
            if fails>0:
                await self.adventurefail()
            else:
                await self.adventuresuccess()

    async def adventuresuccess(self):
        '''Use this if the adventure was a success.'''
        await self.lsend("The adventure was an success!")
        self.game.goods+=1
        self.game.results[self.game.current_round]="A"
        self.game.current_round+=1
        if (self.game.current_round in [3,4,5]) and self.game.goods<3 and self.game.bads<3:
            await self.lsend("The lady of the lake holder must check a person before the game can proceed!"," Use /check to check the loyalty of a person!",self.game.get_player_by_order(self.game.lady_of_lake_holder).user.mention)
            self.mode=5
        else:
            await self.round()


    async def adventurefail(self):
        '''Use this if the adventure was a failure.'''
        await self.lsender("The adventure was sabotaged!")
        self.game.bads+=1
        self.game.results[self.game.current_round]="M"
        self.game.current_round+=1
        if (self.game.current_round in [3,4,5]) and self.game.goods<3 and self.game.bads<3:
            await self.lsend("The lady of the lake holder must check a person before the game can proceed!"," Use /check to check the loyalty of a person!",self.game.get_player_by_order(self.game.lady_of_lake_holder).user.mention)
            self.mode=5
        else:
            await self.round()

    async def adventuredisapprove(self):
        '''This function is fun when there isn't an adventure.'''
        self.game.fails+=1
        if self.game.fails<5:
            await self.lsender(f"The proposed group was not approved! The fail counter is at {self.game.fails}.","Note: On 5 fails, Mordred wins by default.")
        else:
            await self.lsender("You have failed to form a group 5 times. Mordred uses this confusion to launch his attack. Aurthur and his confused comrades lose this battle.")
        await self.round()
    
    @commands.hybrid_command()
    async def kill(self,ctx:commands.Context,merlin:discord.User):
        '''Use this command to try and assassinate Merlin!'''
        if self.mode!=6:
            await self.psender(ctx,"It is not the right time.")
            return
        if ctx.author==merlin:
            await self.psender(ctx,"You cannot kill yourself. Try and kill Merlin.")
            return
        player=self.game.get_player(ctx.author.id)
        if player.role!="Assassin":
            await self.psender(ctx,"You are not the assassin. Assassination is not easy, do not try your hand at it.")
            return
        merlinplayer=self.game.get_player(merlin.id)
        if merlinplayer==None:
            await self.psender(ctx,"That person is not in the game.")
            return
        await self.lsend("BANG!",f"{ctx.author.mention} the assassin has killed {merlin.mention}.")
        if merlinplayer.role!="Merlin":
            await self.lsend("They have killed the wrong person! The minions of mordred must now flee or be killed! Aurthur and his friends have won!")
            await self.end("A")
        else:
            await self.lsend("Merlin was killed! All is lost! Authur can no longer fight against the might of Mordred! Mordred and his minions have won!")
            await self.end("M")

    @commands.hybrid_command()
    async def check(self,ctx:commands.Context,player:discord.User):
        '''Use this command to check the loyalty of a person.'''
        if self.mode!=5:
            await self.psender(ctx,"It is not the right time.")
            return
        if ctx.author==player:
            await self.psender(ctx,"You already know your loyalty. Pick someone else.")
            return
        author=self.game.get_player(ctx.author.id)
        if author.order!=self.game.lady_of_lake_holder:
            await self.psender(ctx,"You do not currently hold a favour with the lady of the lake.")
            return
        target=self.game.get_player(player.id)
        if target==None:
            await self.psender(ctx,"That person is not in the game.")
            return
        if target.checked:
            await self.psender(ctx,"The lady of the lake has already spent time with this person. You cannot check their loyalty again.")
            return
        await self.lsend("Lady of the lake-",f"{ctx.author.mention} has asked the lady of the lake to check {player.mention}.")
        await self.dm(ctx.author,"The lady of the lake wispers to you-",f"{target.user.name}'s loyalty is to {target.loyalty}")
        self.game.lady_of_lake_holder=target.order
        author.checked=True
        target.checked=True
        await self.round()


    async def end(self,who):
        '''Use this to end the game.'''
        everyone_overwrites = self.bot.lobby.overwrites_for(self.bot.server.default_role)
        everyone_overwrites.update(send_messages=True,read_messages=True)
        await self.bot.lobby.set_permissions(self.bot.server.default_role,overwrite=everyone_overwrites)
        al=[]
        ml=[]
        for player in self.game.players:
            await player.user.remove_roles(self.bot.player_role)
            if player.loyalty=="Arthur":
                al.append(player)
            else:
                ml.append(player)
        if who=="A":
            await self.lsend("Winners are-","\n".join([x.user.mention+" "+x.role for x in al]))
            await self.lsender("Losers are-","\n".join([x.user.mention+" "+x.role for x in ml]))
        elif who=="M":
            await self.lsend("Winners are-","\n".join([x.user.mention+" "+x.role for x in ml]))
            await self.lsender("Losers are-","\n".join([x.user.mention+" "+x.role for x in al]))
        else:
            pass
        self.state=0
        self.game=None
        await self.lsend("The game has been reset.")

        

    @commands.hybrid_command()
    async def board(self,ctx:commands.Context):
        '''Use this to get the display board.'''
        if self.state>1:
            await self.send_board(ctx)
        else:
            await self.psender(ctx,"There's no game happening right now.")

    async def send_board(self,chat):
        '''Sends the board into the required chat.'''
        message=discord.Embed(color=discord.Color.brand_green())
        message.title="GAME BOARD"
        message.add_field(name="CURRENT LEADER",value=self.game.get_player_by_order(self.game.leader).user.mention,inline=False)
        message.add_field(name="ADVENTURE RESULTS",value=" ".join([f"""{":blue_square:" if self.game.results[x]=="A" else ":red_square:" if self.game.results[x]=="M" else emotes[self.game.rounds[x-1]]}""" for x in range(1,6)]),inline=False)
        message.add_field(name="FAIL COUNTER",value=str(self.game.fails)+" :white_circle:"*self.game.fails,inline=False)
        message.add_field(name="LADY OF THE LAKE HOLDER",value=self.game.get_player_by_order(self.game.lady_of_lake_holder).user.mention,inline=False)
        await chat.send(embed=message)
        
    

async def setup(bot):
    await bot.add_cog(Game_Cmds(bot=bot))
