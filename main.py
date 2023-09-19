from typing import Optional
from bowler import Bowler
from bowlers_table import BowlersTable
from enums import Commitment, Transport
from ROU_table import ROUTable
from SOI_table import SOITable
from lineup import Lineup
from misc import BowlerDisplayInfo
from sql_table import SqlTable
import passwords


import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

CHANNEL_BOT_TEST = 1153536156651233341

con = sqlite3.connect("bowling.db")
cur = con.cursor()

bowlers = BowlersTable(cur)
rou = ROUTable(cur)
soi = SOITable(cur)

MY_GUILD = discord.Object(id=1012052441757397062)

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

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

def getBoolEmoji(value: bool) -> str:
    return ":white_check_mark:" if value else ":x:"

def generateProfileEmbed(bowler: Bowler):

    commit = "Rostered Player" if bowler.getCommitment() == Commitment.ROSTERED else "Substitute"
    embed=discord.Embed(
        title=f"{bowler.getFullName()} ~ {bowler.getEmail()}",
        description=commit, color=0x852acf)
        
    transport = "Bus" if bowler.getTransport() == Transport.BUS else "Other"
    embed.add_field(
        name="Transportation", value = transport, inline=False)
    
    isInSession = bowler.isInSession()
    embed.add_field(
        name=f"Bowling on DATE?",
        value= getBoolEmoji(isInSession), inline=False)

    return embed

@client.tree.command()
async def profile(interaction: discord.Interaction, discord: Optional[discord.Member]):

    discordID = interaction.user.id if discord is None else discord.id
    bowler = bowlers.getBowlerByDiscord(discordID)

    if bowler is None:
        await interaction.response.send_message("No profile registered. Use /register to register a profile.")
        return
    
    await interaction.response.send_message(embed=generateProfileEmbed(bowler))

@client.tree.command()
@app_commands.describe(
    discord="Your @discord",
    fname='Your first name',
    lname='Your last name',
    email='Your WPI email',
    commitment='Whether you are a rostered player or a substitute',
    team='For rostered players, your team number.'
)
@app_commands.choices(commitment=[
    app_commands.Choice(name="rostered", value="rostered"),
    app_commands.Choice(name="sub", value="sub"),
])
async def register(interaction: discord.Interaction, discord: discord.Member, fname: str, lname:str, email: str, commitment: str, team: int | None = None):
    print(discord, discord.id)
    bowler = bowlers.getBowlerByDiscord(discord.id)

    if bowler is None:
        bowler = bowlers.addBowler(fname, lname, email, discord.id, Commitment(commitment), team)
        if isinstance(bowler, str): # error message
            await interaction.response.send_message(bowler)
            return

        await interaction.response.send_message("Profile registered.", embed=generateProfileEmbed(bowler))
    else:
        await interaction.response.send_message("Profile already registered. Use /set commands to modify.", embed=generateProfileEmbed(bowler))
    
async def getBowler(interaction: discord.Interaction, discord: discord.Member) -> Bowler | None:
    discordID = interaction.user.id if discord is None else discord.id
    bowler = bowlers.getBowlerByDiscord(discordID)

    if bowler is None:
        await interaction.response.send_message("No profile registered. Use /register to register.")
        return None
    return bowler


@client.tree.command()
async def optin(interaction: discord.Interaction, discord: Optional[discord.Member]):
    bowler = await getBowler(interaction, discord)

    if bowler is None:
        return

    if bowler.isInSession():
        await interaction.response.send_message("You are already opted in. Use /optout to opt out.")

    else:
        if bowler.getCommitment() == Commitment.SUB:
            rou.removeBowler(bowler)
        else:
            soi.addBowler(bowler)

        await interaction.response.send_message("You are now opted in. Use /optout to opt out.")

@client.tree.command()
async def optout(interaction: discord.Interaction, discord: Optional[discord.Member]):
    bowler = await getBowler(interaction, discord)

    if bowler is None:
        return

    if not bowler.isInSession():
        await interaction.response.send_message("You are already opted out. Use /optin to opt in.")

    else:
        if bowler.getCommitment() == Commitment.SUB:
            soi.removeBowler(bowler)
        else:
            rou.addBowler(bowler)

        await interaction.response.send_message("You are now opted out. Use /optin to opt in.")


@client.tree.command()
async def buson(interaction: discord.Interaction, discord: Optional[discord.Member]):
    bowler = await getBowler(interaction, discord)

    if bowler is None:
        return
    
    if bowler.getTransport() == Transport.BUS:
        await interaction.response.send_message("Your transportation mode is already set to bus. Use /busoff for self-transportation.")
    else:
        bowler.setTransport(Transport.BUS)
        await interaction.response.send_message("Your transportation mode has been set to bus.")

@client.tree.command()
async def busoff(interaction: discord.Interaction, discord: Optional[discord.Member]):
    bowler = await getBowler(interaction, discord)

    if bowler is None:
        return
    
    if bowler.getTransport() == Transport.SELF:
        await interaction.response.send_message("Your transportation mode is already set to self. Use /buson for bus transportation.")
    else:
        bowler.setTransport(Transport.SELF)
        await interaction.response.send_message("Your transportation mode has been set to self.")
    
def formatCount(numRostered, numSub):
    total = numRostered + numSub
    return f"{total} bowlers ({numRostered} rostered, {numSub} subs)\n"

"""
Show all the rostered teams
"""
@client.tree.command()
async def teams(interaction: discord.Interaction):
    
    response = formatCount(bowlers.countRostered(), bowlers.countSubs())

    teams = bowlers.getRosterTeams()
    for number in teams:
        teammates = teams[number]

        response += f"TEAM {number}:\n"

        for teammate in teammates:
            name = teammate.getFullName()
            response += f"{name} <@{teammate.getDiscord()}>\n"

        response += "\n"

    response += "SUBSTITUTES:\n"
    subs = bowlers.getSubs()
    for bowler in subs:
        name = bowler.getFullName()
        response += f"{name} <@{bowler.getDiscord()}>\n"
    if len(subs) == 0:
        response += "[None]\n"
    
    allowed = discord.AllowedMentions.none()
    await interaction.response.send_message(response, allowed_mentions = allowed)

@client.tree.command()
async def lineup(interaction: discord.Interaction):

    response = "**LINEUP FOR DATE**\n"
    response += formatCount(bowlers.countRostered(), bowlers.countSubs())
    
    currentTeam = -1

    lineup = Lineup(cur)
    for bowlerInfo in lineup.getLineup():

        bowler = Bowler(bowlerInfo.id)

        if bowlerInfo.team != currentTeam:
            currentTeam = bowlerInfo.team
            response += f"\n**TEAM {currentTeam}**\n"
        
        display = BowlerDisplayInfo(bowlerInfo.fullName, bowlerInfo.discord, bowlerInfo.transport)
        rosterAbsent = bowlerInfo.commitment == Commitment.ROSTERED and not bowler.isInSession()
        response += display.toString(rosterAbsent, bowlerInfo.commitment == Commitment.SUB)
    
    response += "\n**OVERFLOW**\n"
    for bowlerInfo in lineup.getOverflow():
        display = BowlerDisplayInfo(bowlerInfo.fullName, bowlerInfo.discord, bowlerInfo.transport)
        response += display.toString(False, False)

    allowed = discord.AllowedMentions.none()
    await interaction.response.send_message(response, allowed_mentions = allowed)

@client.tree.command()
async def sql(interaction: discord.Interaction, query: str):
    cur.execute(query)
    await interaction.response.send_message(str(cur.fetchall()))


resetDatabase()

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN.
client.run(passwords.TOKEN)