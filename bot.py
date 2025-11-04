import os
import discord
from discord import app_commands
from dotenv import load_dotenv
import datagetter
import json

class WowClient(discord.Client):
    user: discord.ClientUser

    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Guild-id Test-Server = 935927889373847552
        # Guild-id Cale's AoC server = 1305513708059103283
        guild = discord.Object(id=935927889373847552)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)


load_dotenv()
intents = discord.Intents.default()
#intents.message_content = True
client = WowClient(intents=intents)


@client.event
async def on_ready():
    print(f"Successfully logged in as {client.user}")

@client.event
async def on_message(message: str):
    if str(message.author) == ".cale1":
        await message.add_reaction('U+1F480')

    if message.author == client.user: # Disregards any messages sent by itself
        return
    if message.content.find("7") != -1:
        await message.channel.send("7")


############################################################################################# COMMANDS
@client.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f"Hi, {interaction.user}")

@client.tree.command()
async def stjärnor(interaction: discord.Interaction):
    datagetter.fetch_data()
    """Visar vilka stjärnor alla har (- för del 1 och + för båda delar)"""
    head = '```Användare      | Dagar    1111111111222222\n               | 1234567890123456789012345\n'

    with open("storedScores.json", 'r') as f:
        data = json.load(f)
        members = data['members']
        local_scores = {}        
        for member in members:
            local_scores[member] = members[member]["local_score"]
        sorted(local_scores, reverse=True)
        members = {k:v for k,v in}
        

    member_progress = [] 
    for member in members:
        current_progress = ""
        member_dict = members[member]
        if member_dict['stars'] == 0:
            continue
        name = member_dict['name']
        current_progress += name + ' '*(15 - len(member_dict['name'])) + "| "
        for i in range (1,26):
            try:
                day = member_dict["completion_day_level"][str(i)]
                try:
                    both_parts_finished = day["2"]
                    current_progress += '+'
                except KeyError:
                    current_progress += '-'
            except KeyError:
                current_progress += ' '
        member_progress.append((current_progress,member_dict["local_score"]))

    body += "```"
    await interaction.response.send_message(head+body)



client.run(os.environ.get("DISCORD_TOKEN"))