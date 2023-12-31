from enum import Enum
from typing import Optional
from bowler import Bowler
from bowlers_table import BowlersTable
from canon_handler import Message, loadCanonData, saveCanonData
from enums import Commitment, Transport
from ROU_table import ROUTable
from SOI_table import SOITable
from lineup import Lineup
from misc import BowlerDisplayInfo
import passwords
import csv_writer
import io
import json


import discord
from discord.ext import commands
from discord import app_commands
import discord.utils
import sqlite3

CHANNEL_BOT_TEST = 1153536156651233341

con = sqlite3.connect("bowling.db")
cur = con.cursor()

bowlers = BowlersTable(con, cur)
rou = ROUTable(con, cur)
soi = SOITable(con, cur)

MY_GUILD = discord.Object(id=1012052441757397062)

NO_PINGS = discord.AllowedMentions.none()

class MyClient(discord.Client):
    def __init__(self, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    # synchronize the app commands to one guild.
    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

# GETS THE CLIENT OBJECT FROM DISCORD.PY. CLIENT IS SYNONYMOUS WITH BOT.
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

client = MyClient(intents)

def resetDatabase():
    bowlers.deleteTable()
    bowlers.createTable()
    rou.deleteTable()
    rou.createTable()
    soi.deleteTable()
    soi.createTable()

def initDatabase():

    if not bowlers.exists():
        bowlers.createTable()
    if not rou.exists():
        rou.createTable()
    if not soi.exists():
        soi.createTable()

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

# convert a message object to a discord.Message object, if it still exists
async def getMessageObjects(message: Message) -> list[discord.Message]:
    try:
        channel = client.get_channel(message.channelID)
        return [await channel.fetch_message(id) for id in message.messageIDs]
    except:
        return []
    
# Updates all messages in a list of messages with the same content, if message still exists
async def updateMessages(messages: list[Message], contents: list[str]):
    for message in messages:
        discordMessages = await getMessageObjects(message)

        for i in range(len(discordMessages)):
            if i < len(contents):
                text = contents[i]
            else:
                text = "."
            await discordMessages[i].edit(content=text, allowed_mentions = NO_PINGS)
    

def getBoolEmoji(value: bool) -> str:
    return ":white_check_mark:" if value else ":x:"

def generateProfileEmbed(bowler: Bowler):

    commit = f"Rostered (Team {bowler.getTeam()})" if bowler.getCommitment() == Commitment.ROSTERED else "Substitute"
    embed=discord.Embed(
        title=f"{bowler.getFullName()}",
        description=commit, color=0x852acf)
    
    embed.add_field(
        name="Email", value = bowler.getEmail(), inline=False)


    transport = "Bus" if bowler.getTransport() == Transport.BUS else "Other"
    embed.add_field(
        name="Transportation", value = transport, inline=False)
    
    isInSession = bowler.isInSession()
    embed.add_field(
        name=f"Bowling on DATE?",
        value= getBoolEmoji(isInSession), inline=False)

    return embed

async def makeAdminOnly(interaction: discord.Interaction):
    if not "exec" in [role.name.lower() for role in interaction.user.roles]:
        print("NO PERMISSION")
        await interaction.response.send_message("You do not have permission to use this command.")
        raise commands.MissingPermissions(["exec"])
    else:
        print("PERMISSION")
    
@client.tree.command(description="View a bowler profile")
async def profile(interaction: discord.Interaction, discord: Optional[discord.Member]):

    await interaction.response.defer(thinking = True)

    discordID = interaction.user.id if discord is None else discord.id
    bowler = bowlers.getBowlerByDiscord(discordID)

    if bowler is None:
        await interaction.followup.send("No profile registered. Use /register to register a profile.")
        return
    
    await interaction.followup.send(embed=generateProfileEmbed(bowler))

async def getBowler(interaction: discord.Interaction, discord: discord.Member, alreadyDeferred = False) -> Bowler | None:
    discordID = interaction.user.id if discord is None else discord.id
    bowler = bowlers.getBowlerByDiscord(discordID)

    if bowler is None:
        if alreadyDeferred:
            await interaction.followup.send("No profile registered. Use `/register` to register.")
        else:
            await interaction.response.send_message("No profile registered. Use `/register` to register.")
        return None

    return bowler

CUTOFF_TEAM = 15

# Generate the teams string
def getTeamsString() -> list[str]:

    responses = []

    response = "**WPI LEAGUE ROSTER**\n"
    response += formatCount(bowlers.countRostered(), bowlers.countSubs())

    teams = bowlers.getRosterTeams()
    for number in teams:


        if number == CUTOFF_TEAM:
            responses.append(response)
            response = "."

        teammates = teams[number]

        response += f"\n**TEAM {number}:**\n"

        for teammate in teammates:
            name = teammate.getFullName()
            response += f"{name} <@{teammate.getDiscord()}>\n"

    responses.append(response)
    response = "."

    response += "\n**SUBSTITUTES:**\n"
    subs = bowlers.getSubs()
    for bowler in subs:
        name = bowler.getFullName()
        response += f"{name} <@{bowler.getDiscord()}>\n"
    if len(subs) == 0:
        response += "[None]\n"

    responses.append(response)

    return responses

# Generate the lineup string
def getLineupString() -> list[str]:

    responses = []

    response = "**LINEUP FOR DATE**\n"
    response += formatCount(bowlers.countRostered() - rou.count(), soi.count())
    
    currentTeam = -1

    lineup = Lineup(cur)
    for bowlerInfo in lineup.getLineup():

        bowler = Bowler(con, cur, bowlerInfo.id)

        if bowlerInfo.team != currentTeam:

            if bowlerInfo.team == CUTOFF_TEAM:
                responses.append(response)
                response = "."

            currentTeam = bowlerInfo.team
            response += f"\n**TEAM {currentTeam}**\n"
        
        display = BowlerDisplayInfo(bowlerInfo.fullName, bowlerInfo.discord, bowlerInfo.transport)
        rosterAbsent = bowlerInfo.commitment == Commitment.ROSTERED and not bowler.isInSession()
        response += display.toString(rosterAbsent, bowlerInfo.commitment == Commitment.SUB)
    
    response += "\n**OVERFLOW**\n"
    overflow = lineup.getOverflow()
    for bowlerInfo in overflow:
        display = BowlerDisplayInfo(bowlerInfo.fullName, bowlerInfo.discord, bowlerInfo.transport)
        response += display.toString(False, False)
    if len(overflow) == 0:
        response += "[None]\n"

    responses.append(response)

    return responses


class PersistentMessageType(Enum):
    ROSTER = 1
    LINEUP = 2

async def createPersistentMessage(interaction: discord.Interaction, type: PersistentMessageType):
    await makeAdminOnly(interaction) # only admins can do this

    await interaction.response.send_message("Creating persistent message. Feel free to delete this message.")

    channel = client.get_channel(interaction.channel_id)

    contents = getLineupString() if type == PersistentMessageType.LINEUP else getTeamsString()

    messages = [await channel.send(content, allowed_mentions = NO_PINGS) for content in contents]

    canon = loadCanonData()
    msgs = canon.lineupMessages if type == PersistentMessageType.LINEUP else canon.rosterMessages
    msgs.append(Message(messages[0].channel.id, [message.id for message in messages]))
    saveCanonData(canon)


"""
Show all the rostered teams
"""
@client.tree.command(description="Show the master bowling league roster and list of substitutes")
@app_commands.choices(options=[
    app_commands.Choice(name="csv", value="csv"),
    app_commands.Choice(name="persistent", value="persistent"),
])
async def teams(interaction: discord.Interaction, options: Optional[str] = None):

    # write to csv and attach file instead
    if options == "csv":
        filename = csv_writer.csvRoster(cur)
        await interaction.response.send_message(file=discord.File(filename))
        return
    elif options == "persistent": # create message that gets persistently edited on changes 
        await createPersistentMessage(interaction, PersistentMessageType.ROSTER)
        return
    
    await interaction.response.defer(thinking = True)

    responses = getTeamsString()
    channel = interaction.channel

    first = True
    for response in responses:
        if first:
            await interaction.followup.send(response, allowed_mentions = NO_PINGS)
            first = False
        else:
            await channel.send(response, allowed_mentions = NO_PINGS)


@client.tree.command(description="Show the bowling league lineup for this week")
@app_commands.choices(options=[
    app_commands.Choice(name="csv", value="csv"),
    app_commands.Choice(name="persistent", value="persistent"),
])
async def lineup(interaction: discord.Interaction, options: Optional[str] = None):

    # write to csv and attach file instead
    if options == "csv":
        filename = csv_writer.csvLineup(cur)
        await interaction.response.send_message(file=discord.File(filename))
        return
    elif options == "persistent": # create message that gets persistently edited on changes 
        await createPersistentMessage(interaction, PersistentMessageType.LINEUP)
        return 
    
    await interaction.response.defer(thinking = True)

    responses = getLineupString()
    channel = interaction.channel

    first = True
    for response in responses:
        if first:
            await interaction.followup.send(response, allowed_mentions = NO_PINGS)
            first = False
        else:
            await channel.send(response, allowed_mentions = NO_PINGS)

# Updates all roster and lineup messages stored in canon data with the latest roster and lineup
async def updateCanon():
    canon = loadCanonData()
    await updateMessages(canon.rosterMessages, getTeamsString())
    await updateMessages(canon.lineupMessages, getLineupString())

@client.tree.command(description="Register a bowler as a rostered player or substitute")
@app_commands.describe(
    discord="Your @discord",
    fname='Your first name',
    lname='Your last name',
    team='For rostered players, your team number. For substitutes, 0.'
)
async def register(interaction: discord.Interaction, discord: discord.Member, fname: str, lname:str, team: int):
    
    await makeAdminOnly(interaction)

    await interaction.response.defer(thinking = True)

    bowler = bowlers.getBowlerByDiscord(discord.id)

    if bowler is None:
        bowler = bowlers.addBowler(fname, lname, discord.id, team)
        await updateCanon()
        if isinstance(bowler, str): # error message
            await interaction.followup.send(bowler)
            return

        await interaction.followup.send("Profile registered.", embed=generateProfileEmbed(bowler))
    else:
        await interaction.followup.send("Profile already registered. Use `/unregister` to unregister.")


@client.tree.command(description="Unregister a bowler. Removes all data associated with the bowler.")
async def unregister(interaction: discord.Interaction, discord: Optional[discord.Member]):
    
    await makeAdminOnly(interaction)

    await interaction.response.defer(thinking = True)

    bowler = await getBowler(interaction, discord, alreadyDeferred = True)

    if bowler is None:
        await interaction.followup.send("No such profile exists.")
        return

    bowlers.removeBowler(bowler)
    await updateCanon()

    await interaction.followup.send("Profile unregistered. Use `/register` to register a new profile.")

@client.tree.command(description="Opt in to bowling this week")
async def optin(interaction: discord.Interaction, discord: Optional[discord.Member]):

    bowler = await getBowler(interaction, discord)

    if bowler is None:
        return
    if interaction.user.id != int(bowler.getDiscord()): # only admins can modify other people
        await makeAdminOnly(interaction)

    await interaction.response.defer(thinking = True)

    if bowler.isInSession():
        await interaction.followup.send("You are already opted in. Use `/optout` to opt out.")

    else:
        if bowler.getCommitment() == Commitment.ROSTERED:
            rou.removeBowler(bowler)
        else:
            soi.addBowler(bowler)

        await updateCanon()   

        await interaction.followup.send("You are now opted in. Use `/optout` to opt out.")

@client.tree.command(description="Opt out of bowling this week")
async def optout(interaction: discord.Interaction, discord: Optional[discord.Member]):
    
    bowler = await getBowler(interaction, discord)

    if bowler is None:
        return
    
    if interaction.user.id != int(bowler.getDiscord()): # only admins can modify other people
        await makeAdminOnly(interaction)

    await interaction.response.defer(thinking = True)

    if not bowler.isInSession():
        await interaction.followup.send("You are already opted out. Use `/optin` to opt in.")

    else:
        if bowler.getCommitment() == Commitment.SUB:
            soi.removeBowler(bowler)
        else:
            rou.addBowler(bowler)

        await updateCanon()

        await interaction.followup.send("You are now opted out. Use `/optin` to opt in.")


@client.tree.command(description="Indicate taking WPI bus transportation this week")
async def buson(interaction: discord.Interaction, discord: Optional[discord.Member]):
    
    bowler = await getBowler(interaction, discord)

    if bowler is None:
        return
    
    if interaction.user.id != int(bowler.getDiscord()): # only admins can modify other people
        await makeAdminOnly(interaction)

    await interaction.response.defer(thinking = True)
    
    if bowler.getTransport() == Transport.BUS:
        await interaction.followup.send("Your transportation mode is already set to bus. Use `/busoff` for self-transportation.")
    else:
        bowler.setTransport(Transport.BUS)
        await updateCanon()
        await interaction.followup.send("Your transportation mode has been set to bus.")

@client.tree.command(description="Indicate providing your own transportation this week")
async def busoff(interaction: discord.Interaction, discord: Optional[discord.Member]):

    bowler = await getBowler(interaction, discord)

    if bowler is None:
        return
    
    if interaction.user.id != int(bowler.getDiscord()): # only admins can modify other people
        await makeAdminOnly(interaction)

    await interaction.response.defer(thinking = True)
    
    if bowler.getTransport() == Transport.SELF:
        await interaction.followup.send("Your transportation mode is already set to self. Use /buson for bus transportation.")
    else:
        bowler.setTransport(Transport.SELF)
        await updateCanon()
        await interaction.followup.send("Your transportation mode has been set to self.")
    

@client.tree.command(description="Set the email address for a bowler")
async def email(interaction: discord.Interaction, discord: Optional[discord.Member], email: str):
    
    bowler = await getBowler(interaction, discord)

    if bowler is None:
        return
    
    if interaction.user.id != int(bowler.getDiscord()):
        await makeAdminOnly(interaction)

    await interaction.response.defer(thinking = True)

    bowler.setEmail(email)
    await interaction.followup.send("Email address updated.", embed=generateProfileEmbed(bowler))

def formatCount(numRostered, numSub):
    total = numRostered + numSub
    return f"{total} bowlers ({numRostered} rostered, {numSub} subs)\n"

@client.tree.command(description="Adjust the master roster for rostered players, or lineup for substitutes")
@app_commands.describe(
    team="Assign a rostered player to a new team, or a sub temporarily to a team. Use 0 to unassign a sub."
)
async def assign(interaction: discord.Interaction, discord: discord.Member, team: int):
    
    await makeAdminOnly(interaction)

    await interaction.response.defer(thinking = True)
    
    bowler = await getBowler(interaction, discord, alreadyDeferred = True)

    if bowler is None:
        return

    # cast to None since discord command only allows ints
    if team == 0:
        team = None

    if bowler.getCommitment() == Commitment.ROSTERED:
        if team is None:
            await interaction.followup.send("Rostered players must have a team.")
            return
        bowlers.assignTeam(bowler, team)
        await updateCanon()
        await interaction.followup.send(f"{bowler.getFullName()} successfully moved to team {team}. See `/teams` for the updated roster.")
    else:
        if not bowler.isInSession():
            await interaction.followup.send("Substitutes must be opted in this week to be assigned to a temporary team.")
            return
        soi.assignTeam(bowler, team)
        await updateCanon()
        await interaction.followup.send(f"{bowler.getFullName()} successfully assigned to team {team} for this week. See `/lineup` for the updated lineup.")
    

@client.tree.command(description="Reset the lineup to original roster and opt-ins/opt-outs for the week")    
async def reset(interaction: discord.Interaction):
    
    await makeAdminOnly(interaction)

    await interaction.response.defer(thinking = True)
    
    rou.deleteTable()
    rou.createTable()
    soi.deleteTable()
    soi.createTable()
    await updateCanon()
    await interaction.followup.send("Lineup reset to original roster. Subs can use `/optin` to opt in.")

@client.tree.command(description="Back up database")
async def backup(interaction: discord.Interaction):

    await interaction.response.defer(thinking = True)

    filename = "export/backup.sql"
    with io.open(filename, 'w') as p:
        for line in con.iterdump():
            p.write('%s\n' % line)

    await interaction.followup.send(file=discord.File(filename))

@client.tree.command(description="Show all BowlingBot commands")
async def help(interaction: discord.Interaction):

    embed=discord.Embed(
        title="BowlingBot Help",
        description="A WPI league roster management tool. Store bowler info, organize teams, and determine lineups and substitutes each week."
    )

    embed.add_field(
        name="/register", value = "Register a bowler", inline=False)
    
    embed.add_field(
        name="/unregister", value = "Unregister a bowler", inline=False)
    
    embed.add_field(
        name="/profile", value = "View a bowler profile", inline=False)
    
    embed.add_field(
        name="/optin", value = "Opt in to bowling this week. Rostered players are opted in by default", inline=False)
    
    embed.add_field(
        name="/optout", value = "Opt out of bowling this week. Subs are opted out by default", inline=False)
    
    embed.add_field(
        name="/buson", value = "Indicate taking WPI bus transportation this week", inline=False)
    
    embed.add_field(
        name="/busoff", value = "Indicate providing your own transportation this week", inline=False)
    
    embed.add_field(
        name="/assign", value = "Assign a rostered player to a new team, or a sub temporarily to a team. Set 0 to team to unassign a sub", inline=False)
    
    embed.add_field(
        name="/teams", value = "View the rostered teams and substitutes", inline=False)
    
    embed.add_field(
        name="/lineup", value = "View the lineup for this week", inline=False)
    
    embed.add_field(
        name="/reset", value = "Reset the lineup to original roster and opt-ins/opt-outs for the week. Useful between bowling weeks", inline=False)
    
    embed.add_field(
        name="/backup", value = "Back up the database as an .sql file", inline=False)
    
    await interaction.response.send_message(embed=embed)

initDatabase()

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN.
client.run(passwords.TOKEN)