import os
import random as ran
from random import *
import discord
import sqlite3

class MusicClient(discord.Client):

    def __init__(self,startupMessage,token,dbconnection):
        self.startupMessage = startupMessage
        self.run(token)

    async def on_ready(self):
        await startupMessage.channel.send("Entering playlist mode. Enter a playlist command. To see all playlist commands type $commands. To quit playlist mode type $quit")

    async def on_message(self,message):
        #when a message is recieved
        if message.author != self.user and len(message.content) > 0 and message.content[0] == '$':
            command = message.content.split(' ',1)[0].lower()
            self.loop.create_task(self.execute_command(command,message))

    async def execute_command(self,command,message):
        res = commands.get(command)
        self.loop.create_task(res(message))

    async def listCommands(self,message):
        f = open('docs/playlistcommands.txt','r')
        await message.channel.send(f.read())
        f.close()

    async def chooseFromList(self,message):
        #chooses a value from a given list
        players = message.content.split(' ')
        if len(players) > 1:
            players = players[1:]
        else:
            players = self.getPlayersInVoiceChannel(message)
        await message.channel.send(ran.choice(players) + ", I choose you!")



    def getPlayersInVoiceChannel(self,message):
        members = [c.members for c in message.guild.channels if (c.type == discord.ChannelType.voice and message.author in c.members)]
        if len(members) > 0:
            members = members[0]
            names = [m.name for m in members]
            if 'Rythm' in names:
                names.remove('Rythm')
            return names
        else:
            return ["Player not in Voice Channel"]
