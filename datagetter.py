import time
import os
import json
import requests
from dotenv import load_dotenv
import schedule
import tools

load_dotenv()
def fetch_data(force:bool=False):
    try:
        if int(time.time()-os.path.getmtime("storedScores.json")) < 900 and not force:
            print("Data was not fetched: data is too recent and force was not used.")
            return -1
    except FileNotFoundError:
        print("storedScores doesn't exist, so what?")
    
    print("Fetching data at time", tools.unix_to_human(int(time.time())))
    url = f"https://adventofcode.com/{os.environ.get("YEAR")}/leaderboard/private/view/{os.environ.get("AOC_USER_ID")}.json"
    
    # Headers as "demanded by AoC staff, session cookie is necessary to even get access and needs to be once/month or so"
    headers = {
        "User-Agent": "github.com/Cale547 AoChie (Leaderboard manager)",
        "Cookie": os.environ.get("SESSION_COOKIE")
    }

    response = requests.get(url, headers=headers, timeout=20)
    if response.status_code == 200: # Success
        data = response.json()
        str_data = json.dumps(data)
        
        if os.path.isfile("storedScores.json"):
            os.remove("storedScores.json")
        stored_file = open("storedScores.json", "x",encoding="UTF8")
        stored_file.write(str_data)
        stored_file.close()

    else: # Fail
        print("Failed to retrieve data:", response.status_code)
        return -1

fetch_data(force=True) # Used when running this script by itself


# Unused scheduler for script
# Current implementation tries to fetch on each discord command used instead, decreasing load on AoC and only updating when users want recent data
#schedule.every(15).minutes.do(fetch_data)
#print("Scheduler started at",tools.unix_to_human(time.time()))
# while True:
#     #print(int(time.time()-os.path.getmtime("storedScores.json")),"seconds since last update")
#     schedule.run_pending()
#     time.sleep(5)
