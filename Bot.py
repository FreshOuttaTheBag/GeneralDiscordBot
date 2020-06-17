import os
import random as ran
from random import *
import discord
import sqlite3
from MusicClient import MusicClient
import TokenGetter.getToken

class Poll:
    #dto, could be replaced with a dict but meh
    def __init__(self,name,comment,choices):
        self.name = name
        self.choices = {i:0 for i in choices}
        self.membersWhoVoted = []
        self.comment = comment


class RockPaperScissors:
    #dto, could be replaced with a dict but meh
    def __init__(self,challenger,challenged,channel):
        self.p1 = challenger
        self.p2 = challenged
        self.channel = channel
        self.p1Response = None
        self.p2Response = None

class Client(discord.Client):

    def __init__(self):
        super().__init__()
        self.Polls = []
        self.Games = {'RockPaperScissors' : []}

    async def on_ready(self):
        #basically __init__
        print(str(client.user) + ' has connected to Discord!')

    async def on_message(self,message):
        #when a message is recieved
        if message.author != self.user and len(message.content) > 0 and message.content[0] == '$':
            command = message.content.split(' ',1)[0].lower()
            self.loop.create_task(self.execute_command(command,message))
        else:
            for rps in self.Games["RockPaperScissors"]:
                if (message.author == rps.p1 or message.author == rps.p2) and any(x == message.content.lower() for x in RPSChoices):
                    self.loop.create_task(self.handleRPS(message))

    async def execute_command(self,command,message):
        commands = {
                '$choose' : self.chooseFromList,
                '$suggest' : self.suggestion,
                '$coinflip' : self.coinFlip,
                '$chooseleagueroles' : self.leagueRoles,
                '$roll' : self.diceRoll,
                '$commands' : self.listCommands,
                '$cockrate' : self.cockRate,
                '$cockcompare' : self.cockCompare,
                '$8ball' : self.magicResponse,
                '$newpoll' : self.createNewPoll,
                '$pollchoices': self.showPollChoices,
                '$vote' : self.votePoll,
                '$polls' : self.listPolls,
                '$closepoll': self.closePoll,
                '$rps' : self.RPS,
                '$inventory' : self.showInventory,
                '$playlist' : self.playlist,
                '$fuck' : self.getPlayersInVoiceChannel
            }
        res = commands.get(command)
        self.loop.create_task(res(message))

    async def playlist(self,message):
        musicClient = MusicClient(message,TOKEN,conn)

    async def showInventory(self,message):
        c.execute("SELECT Item,Quantity FROM Inventory WHERE MemberID = ?",(message.author.id,))
        msg = "You own: \n"
        for i in c.fetchall():
            msg += i[0] + " : " + str(i[1])
        await message.channel.send(msg)


    async def RPS(self,message):
        if any(((message.author == x.p1 or message.author == x.p2) or (message.mentions[0] == x.p1) or (message.mention[0] == x.p2)) for x in self.Games['RockPaperScissors']):
            await message.channel.send("Either you, or your challengee is already challened to Rock Paper Scissors!")
            return
        game = RockPaperScissors(message.author,message.mentions[0],message.channel)
        self.Games['RockPaperScissors'].append(game)
        await message.channel.send(message.author.name + " has challenged " + message.mentions[0].name + " to RockPaperScissors!")
        await message.channel.send("Personal message me a rock paper or scissors to respond!")

    async def handleRPS(self,message):
        game = next(filter(lambda x: (x.p1 == message.author or x.p2 == message.author), self.Games['RockPaperScissors']))
        if message.author == game.p1:
            game.p1Response = message.content.lower()
        elif message.author == game.p2:
            game.p2Response = message.content.lower()
        if game.p1Response == None or game.p2Response == None:
            return
        else:
            if game.p1Response == game.p2Response:
                await game.channel.send(game.p1.name + " chose " + game.p1Response + " " + game.p2.name + " chose " + game.p2Response + "\nThat's a tie!")
                game.p1Response = None
                game.p2Response = None
                return
            winner = None
            if game.p1Response == "rock":
                if game.p2Response == "paper":
                    winner = game.p2
                elif game.p2Response == "scissors":
                    winner = game.p1
            elif game.p1Response == "paper":
                if game.p2Response == "scissors":
                    winner = game.p2
                elif game.p2Response == "rock":
                    winner = game.p1
            elif game.p1Response == "scissors":
                if game.p2Response == "rock":
                    winner = game.p2
                elif game.p2Response == "paper":
                    winner = game.p1

            await game.channel.send(game.p1.name + " chose " + game.p1Response + " " + game.p2.name + " chose " + game.p2Response + "\n" + winner.name + " wins!")
            self.Games['RockPaperScissors'].remove(game)


    async def listPolls(self,message):
        msg = "All open polls:\n"
        for i in self.Polls:
            msg += i.name + '\n'
        await message.channel.send(msg)

    async def showPollChoices(self,message):
        name = message.content.split(' ',1)[1].strip()
        if any(x.name == name for x in self.Polls):
            poll = next(filter(lambda x: x.name == name,  self.Polls))
            msg = poll.name + "\n\n" + poll.comment + "\n"
            msg += "\nChoices for %s:\n"%name
            for i in poll.choices:
                msg += i + "\n"
            await message.channel.send(msg)
        else:
            await message.channel.send('Poll "%s" not found, or does not exist'%name)

    async def votePoll(self,message):
        pol = message.content.split(' ',2)
        name = pol[1].strip()
        if any(x.name == name for x in self.Polls):
            choice = pol[2].strip()
            poll = next(filter(lambda x: x.name == name,  self.Polls))
            if message.author.id not in poll.membersWhoVoted:
                if choice in poll.choices:
                    poll.choices[choice] += 1
                    poll.membersWhoVoted.append(message.author.id)
                    await message.channel.send('Vote for %s submitted!'%choice)
                    return
                else:
                    await message.channel.send('"%s" is not a choice for %s. Use "$pollChoices %s" to see all choices for %s'%(choice,name,name,name))
                    return
            else:
                await message.channel.send("You've already voted in this poll!")
        else:
            await message.channel.send('Poll "%s" not found, or does not exist'%name)

    async def createNewPoll(self,message):
        poll = message.content.split(' ',1)[1:][0]
        poll = poll.split(',')
        name = poll[0].strip()
        comment = poll[1].strip()
        choices = poll[2:]
        choices = [i.strip() for i in choices]
        self.Polls.append(Poll(name,comment,choices))
        msg = 'Poll "%s" created.\n\n%s\n\nChoices:\n'%(name,comment)
        for c in choices:
            msg += c + "\n"
        msg += '\nUse "$pollChoices %s" to see the choices again. \nUse "$vote %s choice" to vote for a choice in the poll. \nUse "$closePoll %s" to stop the poll and display the results'%(name,name,name)
        await message.channel.send(msg)

    async def closePoll(self,message):
        name = message.content.split(' ',1)[1].strip()
        if any(x.name == name for x in self.Polls):
            poll = next(filter(lambda x: x.name == name,  self.Polls))
            results = sorted(poll.choices.items(),key=lambda x: x[1],reverse=True)
            await message.channel.send('Results are in for %s!'%name)
            msg = ""
            for res in results:
                msg += res[0] + ": " + str(res[1]) + "\n"
            msg += results[0][0] + " Wins!"
            await message.channel.send(msg)
            self.Polls.remove(poll)
        else:
            await message.channel.send('Poll "%s" not found, or does not exist'%name)


    async def magicResponse(self,message):
        await message.channel.send(ran.choice(magicResponces))

    async def listCommands(self,message):
        f = open('/docs /commands.txt','r')
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

    async def suggestion(self,message):
        #write suggestion to file
        try:
            f = open("docs/suggestions.txt","a")
            sugg = message.content[9:] + "\n"
            f.write(sugg)
            f.close()
        except:
            await message.channel.send("Woah there bud, I ran into an error!")
        return

    async def coinFlip(self,message):
        #send heads or tails
        r = randint(0,1)
        if r == 0:
            r = "Heads!"
        elif r == 1:
            r = "Tails!"
        await message.channel.send(r)

    async def leagueRoles(self,message):
        #if 5 players are given
        if len(message.content.split(' ')) > 1:
            players = message.content.split(' ')[1:]
        else:
            players = self.getPlayersInVoiceChannel(message)

        ran.shuffle(leagueRoles)
        ran.shuffle(players)
        roles = dict(zip(leagueRoles,players))
        res = ""
        for x in roles:
            res += x + ": " + roles[x] + "\n"
        await message.channel.send(res)

    async def diceRoll(self,message):
        #send a value from 0 to rng
        rng = 6
        try :
            rng = int(message.content.split(' ')[1])
        except:
            print("Error parsing number after roll")
            pass
        await message.channel.send(ran.randint(1,rng))

    def getPlayersInVoiceChannel(self,message):
        members = [i.members for i in message.guild.channels if (i.type == discord.ChannelType.voice and message.author in i.members)]
        if len(members) > 0:
            members = members[0]
            names = [m.name for m in members]
            if 'Rythm' in names:
                names.remove('Rythm')
            return names
        else:
            return ["Player not in Voice Channel"]

    async def cockRate(self,message):
        await message.channel.send("Alright, let's see it.")
        mID = message.author.id
        c.execute("SELECT Rating FROM CockRate WHERE MemberID = ?",(mID,))
        rating = c.fetchall()
        if len(rating) > 0:
            rating = rating[0][0]
        else:
            rating = ran.randint(0,10)
            c.execute('''INSERT INTO CockRate (MemberID,Rating)
                         VALUES (?,?);''',(mID,rating))
            conn.commit()

        res = "I'd give it a " + str(rating) + " out of 10. "
        modifier = ""
        if rating == 10:
            modifier = "Perfect cock!"
        elif 7 <= rating <= 9:
            modifier = "Nice cock!"
        elif 4 <= rating <= 6:
            modifier = "That's an okay cock."
        elif rating < 4:
            modifier = "You call that a cock?"
        res += modifier
        await message.channel.send(res)

    async def cockCompare(self,message):
        await message.channel.send("Alright, pull them out.")
        challenger = message.author
        challenged = message.mentions[0]
        sql = '''SELECT Rating FROM CockRate WHERE MemberID = ?'''
        c.execute(sql,(challenger.id,))
        r1 = c.fetchall()
        c.execute(sql,(challenged.id,))
        r2 = c.fetchall()
        if len(r1) == 0:
            await message.channel.send(challenger.name + " does not have a Cock Rating yet!")
            return
        elif len(r2) ==0:
            await message.channel.send(challenged.name + " does not have a Cock Rating yet!")
            return
        r1 = r1[0][0]
        r2 = r2[0][0]


        res = ""
        if r1 == r2:
            res = "I can barely tell the two cocks apart!"
        else:
            if r1 > r2:
                res = challenger.name + "'s cock is better than " + challenged.name + "'s cock!"
            else:
                res = challenged.name + "'s cock is better than " + challenger.name + "'s cock!"
        await message.channel.send(res)


if __name__ == "__main__":
    RPSChoices = ['rock','paper','scissors']
    client = discord.Client()
    TOKEN = getToken()
    leagueRoles = ['Jungle','Support','Bottom','Top','Mid']
    magicResponces = [ 'As I see it, yes.',
                     'Ask again later.',
                     'Better not tell you now.',
                     'Cannot predict now.',
                     'Concentrate and ask again.',
                    'Don’t count on it.',
                     'It is certain.',
                     'It is decidedly so.',
                     'Most likely.',
                     'My reply is no.',
                     'My sources say no.',
                     'Outlook not so good.',
                     'Outlook good.',
                     'Reply hazy, try again.',
                     'Signs point to yes.',
                     'Very doubtful.',
                     'Without a doubt.',
                     'Yes.',
                     'Yes – definitely.',
                     'You may rely on it.'
                    ]
    conn = sqlite3.connect('db/Data.db')
    c = conn.cursor()


    client = Client()
    client.run(TOKEN)
