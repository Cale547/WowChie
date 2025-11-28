import os
import discord
from discord import app_commands
from dotenv import load_dotenv
import datagetter
import json
import tools
import re
import time


class WowClient(discord.Client):
    #user: discord.ClientUser

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

MAX_NAME_LENGTH = 15
############################################################################################# COMMANDS
@client.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f"Hi, {interaction.user}")

@client.tree.command()
async def stjärnor(interaction: discord.Interaction):
    """Visar vilka stjärnor alla har (- för del 1 och + för båda delar)"""
    datagetter.fetch_data()
    head = f"```Användare{' '*(MAX_NAME_LENGTH - len("Användare"))}| Dagar    1111111111222222\n               | 1234567890123456789012345\n"

    with open("storedScores.json", 'r') as f:
        data = json.load(f)
    members = data["members"]
    local_scores = {}
    for member in members:
        score = members[member]["local_score"]
        if score != 0:
            local_scores[member] = score
    local_scores = dict(sorted(local_scores.items(), key=lambda tuple: tuple[1], reverse=True))

    member_progress = []
    for member in local_scores.keys():
        current_progress = ""
        member_dict = members[member]
        name = member_dict['name']
        current_progress += f"{name}{' '*(MAX_NAME_LENGTH - len(member_dict['name']))}| "
        for i in range(1,26):
            try:
                day = member_dict["completion_day_level"][str(i)]
                try:
                    both_parts_finished = day["2"]
                    current_progress += '+'
                except KeyError:
                    current_progress += '-'
            except KeyError:
                current_progress += ' '
        member_progress.append(current_progress)

    body = "\n".join(member_progress)
    body += "```"
    await interaction.response.send_message(head+body)

@client.tree.command()
async def topplista(interaction: discord.Interaction):
    """Visar poäng, antal stjärnor, och tid för senaste stjärna"""
    datagetter.fetch_data()
    head = "```Namn          | Poäng   | Stjärnor | Datum        | Tid \n"
    with open("storedScores.json", 'r') as f:
        data = json.load(f)
    members = data["members"]
    local_scores = {}
    for member in members:
        score = members[member]["local_score"]
        if score != 0:
            local_scores[member] = score
    local_scores = dict(sorted(local_scores.items(), key=lambda tuple: tuple[1], reverse=True))
    
    member_progress = []
    for member in local_scores.keys():
        current_progress = ""
        member_dict = members[member]
        name = member_dict['name']
        current_progress += f"{name}{' '*(MAX_NAME_LENGTH - 1 - len(member_dict['name']))}| "

        current_progress += str(member_dict["local_score"]) + ' '*(8-len(str(member_dict["local_score"]))) + "| "
        current_progress += str(member_dict["stars"]) + ' '*(9-len(str(member_dict["stars"]))) + "| "
        timestamp_unix = member_dict["last_star_ts"]
        timestamp = tools.unix_to_human(timestamp_unix)
        print(timestamp_unix)
        current_progress += timestamp[1] + ' '*(13-len(timestamp[1])) + "| "
        current_progress += timestamp[0]
        member_progress.append(current_progress)

    body = "\n".join(member_progress)
    body += "```"
    await interaction.response.send_message(head+body)

@client.tree.command()
@app_commands.describe(
    aoc_name="Ditt AoC-namn"
)
async def register(interaction: discord.Interaction, aoc_name: str):
    """Connects your discord name to your AoC name"""

    discord_name = interaction.user.name
    print(f"Tries to register {discord_name} to {aoc_name}")

    try:
        with open("userbase.json", "r") as f:
            userbase = json.load(f)
    except FileNotFoundError:
        userbase = {"users": []}

    for entry in userbase["users"]:
        if entry["discord"] == discord_name:
            await interaction.response.send_message("Ditt discord-namn är redan registrerat. Kontakta sysadmin (Kalle)",ephemeral=True)
            return
        if entry["aoc"] == aoc_name:
            await interaction.response.send_message("Det AoC-namnet är redan registrerat. Kontakta sysadmin (Kalle)",ephemeral=True)
            return
        
    datagetter.fetch_data()
    with open("storedScores.json", "r") as f:
        data = json.load(f)
    exists = any(
            member_data["name"] == aoc_name
            for member_data in data["members"].values())
    if not exists:
        await interaction.response.send_message("Det AoC-namnet finns inte på topplistan. Kontakta sysadmin (Kalle)",ephemeral=True)
        return
    
    userbase["users"].append({
        "discord": discord_name,
        "aoc": aoc_name
    })

    with open("userbase.json", "w") as f:
        json.dump(userbase, f, indent=4)
    await interaction.response.send_message(f"User {interaction.user.name} is now registered as {aoc_name}")

@client.tree.command()
@app_commands.describe(
    day="Vilken dag gör du? (1-12)",
    part="Vilken del gör du? (1-2)"
)
async def start(interaction: discord.Interaction, day: int, part: int):
    """Sparar ner en lokal start-tid som du själv väljer"""

    discord_name = interaction.user.name

    if not (1<=day<=12):
        await interaction.response.send_message("Den dagen finns ju inte!",ephemeral=True)
        return
    if not (1<=part<=2):
        await interaction.response.send_message("Den delen finns ju inte!",ephemeral=True)
        return
    
    try:
        with open("userbase.json", "r") as f:
            userbase = json.load(f)
    except FileNotFoundError:
        await interaction.response.send_message("Någon har ätit upp databasen, kontakta Kalle.",ephemeral=True)
        return
    
    users = userbase.get("users", [])
    user_entry = None

    for entry in users:
        if entry["discord"] == discord_name:
            user_entry = entry
            break
    
    if user_entry is None:
        await interaction.response.send_message("Registrera dig med /register innan du kör detta kommando.",ephemeral=True)
        return
    
    if "starts" not in user_entry:
        user_entry["starts"] = {}
    
    starts = user_entry["starts"]

    if str(day) not in starts:
        starts[str(day)] = {}
    
    if str(part) in starts[str(day)]:
        await interaction.response.send_message(f"Du har redan startat dag {day}, del {part}.",ephemeral=True)
        return
    
    timestamp = int(time.time())
    starts[str(day)][str(part)] = timestamp

    with open("userbase.json", "w") as f:
        json.dump(userbase, f, indent=4)

    await interaction.response.send_message(f"{discord_name} startade precis dag {day}, del {part}!")


@client.tree.command()
async def lokaltopplista(interaction: discord.Interaction):
    """Visar poäng, antal stjärnor, och tid för senaste stjärna (med tider från /start)"""

    try:
        with open("userbase.json", "r") as f:
            userbase = json.load(f)
    except FileNotFoundError:
        await interaction.response.send_message("Någon har ätit upp databasen. Kontakta Kalle", ephemeral=True)
        return
    
    datagetter.fetch_data()
    with open("storedScores.json", "r") as f:
        stored = json.load(f)

    members = stored["members"]
    LEADBOARD_LENGTH = len(members)

    aoc_info = {}
    for member_id, m in members.items():
        aoc_info[m["name"]] = {
            "stars": m["stars"],
            "last": m["last_star_ts"],
            "completion": m.get("completion_day_level", {})
        }
    
    points = {}

    for entry in userbase.get("users", []):
        discord_name = entry["discord"]
        points[discord_name] = 0
    
    for day in range(1,13):
        day = str(day)
        for part in["1", "2"]:
            solves = []

            for entry in userbase.get("users", []):
                discord_name = entry["discord"]
                aoc_name = entry["aoc"]

                if aoc_name not in aoc_info:
                    continue

                completion = aoc_info[aoc_name]["completion"]
                if day in completion and part in completion[day]:
                    finish_time = int(completion[day][part]["get_star_ts"])
                else:
                    continue

                starts = entry.get("starts", {})
                start_time = starts.get(day, {}).get(part, None)
                if start_time is None:
                    start_time = tools.get_default_start_time(2025, int(day))
                elif start_time > finish_time:
                        start_time = tools.get_default_start_time(2025, int(day))

                solve_time = finish_time - start_time
                if solve_time > 0:
                    solves.append((discord_name, solve_time))
            
            solves.sort(key = lambda x: x[1])
            n = LEADBOARD_LENGTH
            for rank, (discord_name, _) in enumerate(solves):
                points[discord_name] += (n - rank)
    
    sorted_users = sorted(points.items(), key=lambda x: x[1], reverse=True)
    head = "```Namn          | Poäng   | Stjärnor | Datum        | Tid \n"
    rows = []

    for discord_name, score in sorted_users:
        entry = next((u for u in userbase["users"] if u["discord"] == discord_name), None)
        if not entry:
            continue

        aoc_name = entry["aoc"]
        star_count = aoc_info[aoc_name]["stars"]
        last_ts = aoc_info[aoc_name]["last"]

        time_str, date_str = tools.unix_to_human(last_ts)

        name_col = f"{discord_name}{' ' * (14 - len(discord_name))}"
        score_col = f"{score}{' ' * (8 - len(str(score)))}"
        stars_col = f"{star_count}{' ' * (9 - len(str(star_count)))}"
        date_col = f"{date_str}{' ' * (13 - len(date_str))}"

        row = f"{name_col}| {score_col}| {stars_col}| {date_col}| {time_str}"
        rows.append(row)
    
    body = "\n".join(rows) + "```"
    await interaction.response.send_message(head + body)


client.run(str(os.environ.get("DISCORD_TOKEN")))