from bowler import Bowler
from bowlers_table import BowlersTable
from dates_table import DatesTable
from enums import Attendance, Commitment, Transport
from session_bowlers_table import SessionBowlersTable
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
dates = DatesTable(cur)
session = SessionBowlersTable(cur)

bowlers.deleteTable()
bowlers.createTable()
dates.deleteTable()
dates.createTable()
session.deleteTable()
session.createTable()

john = bowlers.insert("John", "Doe", "email@com", "jd#1234", Commitment.ROSTERED)
jane = bowlers.insert("Jane", "Doe", "email@com", "jd#1234", Commitment.SUB)
session.addBowler(john)


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
    
    transport = "Bus" if bowler.getDefaultTransport() == Transport.BUS else "Other"
    embed.add_field(
        name="Transportation", value = transport, inline=False)
    
    isInSession = bowler.isInSession()
    embed.add_field(
        name=f"Bowling on {bowler._getActiveDate()}?",
        value= getBoolEmoji(isInSession), inline=False)

    if isInSession: # only relevant if the bowler is in the session
        attendance = bowler.getAttendance()
        if attendance == Attendance.AWAIT:
            emoji = ":question:"
        else:
            emoji = getBoolEmoji(attendance == Attendance.YES)
        embed.add_field(name="Attendance", value=emoji, inline=False)

    return embed

@client.tree.command()
async def profile(interaction: discord.Interaction):

    discordID = interaction.user.id
    bowler = bowlers.getBowlerByDiscord(discordID)

    if bowler is None:
        await interaction.response.send_message("No profile registered. Use /register to register a profile.")
        return
    
    await interaction.response.send_message(embed=generateProfileEmbed(bowler))

@client.tree.command()
@app_commands.describe(
    fname='Your first name',
    lname='Your last name',
    email='Your WPI email',
    commitment='Whether you are a rostered player or a substitute'
)
@app_commands.choices(commitment=[
    app_commands.Choice(name="rostered", value="rostered"),
    app_commands.Choice(name="sub", value="sub"),
])
async def register(interaction: discord.Interaction, fname: str, lname:str, email: str, commitment: str):
    discordID = interaction.user.id
    bowler = bowlers.getBowlerByDiscord(discordID)

    if bowler is None:
        bowler = bowlers.insert(fname, lname, email, discordID, Commitment(commitment))
        await interaction.response.send_message("Profile registered.", embed=generateProfileEmbed(bowler))
    else:
        await interaction.response.send_message("Profile already registered. Use /set commands to modify.", embed=generateProfileEmbed(bowler))
    
@client.tree.command()
async def optin(interaction: discord.Interaction):
    discordID = interaction.user.id
    bowler = bowlers.getBowlerByDiscord(discordID)

    if bowler.isInSession():
        if bowler.getCommitment() == Commitment.SUB:
            message = "You are already opted in. Use /optout to opt out."
        else:
            message = "You are already opted in. Use /optout to opt out. Note that you are a rostered player, so are opted in by default."
        await interaction.response.send_message(message, embed=generateProfileEmbed(bowler))

    else:
        session.addBowler(bowler)
        await interaction.response.send_message("You have opted in.", embed=generateProfileEmbed(bowler))

@client.tree.command()
async def optout(interaction: discord.Interaction):
    discordID = interaction.user.id
    bowler = bowlers.getBowlerByDiscord(discordID)

    if bowler.isInSession():
        session.removeBowler(bowler)
        
        if bowler.getCommitment() == Commitment.SUB:
            message = "You have opted out."
        else:
            message = "You have opted out. Note that you are a rostered player, so please do this infrequently"
        
        await interaction.response.send_message(message, embed=generateProfileEmbed(bowler))
    else:
        await interaction.response.send_message("You are already opted out. Use /optin to opt in.", embed=generateProfileEmbed(bowler))


@client.tree.command()
@app_commands.describe(
    first_value='The first value you want to add something to',
    second_value='The value you want to add to the first value',
)
async def add(interaction: discord.Interaction, first_value: int, second_value: int):
    """Adds two numbers together."""
    await interaction.response.send_message(f'{first_value} + {second_value} = {first_value + second_value}')



# EXECUTES THE BOT WITH THE SPECIFIED TOKEN.
client.run(passwords.TOKEN)