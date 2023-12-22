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
import datetime
from constants import *
from player_data import Player

class Game:

    def __init__(self,bot):
        self.bot=bot
        self.lobby_start_time=datetime.datetime.now()
        self.players=[]
        self.startcount=0
        self.playercount=0
        self.rounds=None
        self.current_round=1
        self.mode=None
        self.results=["PLACEHOLDER"]+[None]*5
        self.leader=0
        self.fails=0
        self.goods=0
        self.bads=0
        self.tempteam=[]
        self.team=[]
        self.lady_of_lake_enable=True
        self.lady_of_lake_holder=None


    def add_player(self,player:Player):
        self.players.append(player)
        self.playercount+=1

    def get_player(self,id:int):
        for player in self.players:
            if id==player.id:
                return player
        return None

    def del_player(self,player):
        if type(player)==int:
            player=self.get_player(player)
        if player==None:
            raise Exception("Invalid player")
        else:
            for iterplayer in self.players:
                if player==iterplayer:
                    self.players.remove(iterplayer)
                    self.playercount-=1
                    return 
                
    def get_player_by_order(self,order):
        for player in self.players:
            if order==player.order:
                return player
        return None
                
        



    


