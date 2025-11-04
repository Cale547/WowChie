import json
import os
from dotenv import load_dotenv
import psycopg2 as pcg
import tools


def main():
    print("Recording latest scoreboard to database")
    with open("storedScores.json","r",encoding="UTF8") as f:
        data = json.load(f)
        data_members = dict(data['members'])
        f.close()

    load_dotenv()
    connection = pcg.connect(database = os.environ.get("pcgDatabse"),
                            user = os.environ.get("pcgUser"),
                            host= os.environ.get("localhost"),
                            password = os.environ.get("pcgPass"),
                            port = os.environ.get("pcgPort"))
    cursor = connection.cursor()

    # Checks if the player/days_completed table is empty, determines if the json data should be inserted or updated
    cursor.execute("""SELECT * FROM player
                   LIMIT 1;""")
    newPlayer = (len(cursor.fetchall()) == 0)

    for member in data_members:
        current_user = dict(data_members[member]) # current_user.keys() = {last_star_ts, name, global_score, stars, id, local_score, completion_day_level}
        user_id = current_user['id']
        name = current_user['name']
        local_score = current_user['local_score']
        last_star_ts = tools.unix_to_human(current_user['last_star_ts'])
        time = last_star_ts[0]
        date = last_star_ts[1]
        #if date == "1970-01-01":
        #    time = date = "n/a"
        stars = current_user['stars']
        global_score = current_user['global_score']

    # With current setup, new players will not be added since that only happens when the table is empty.
    # If someone joins, delete the table and go again. (Or just rewrite the code)
        if newPlayer:
            cursor.execute("""INSERT INTO player (user_id, username, local_score, last_star_time, last_star_date, stars, global_score)
            VALUES (%s,%s,%s,%s,%s,%s,%s);""", (user_id, name, local_score, time, date, stars, global_score))

        else:
            cursor.execute("""UPDATE player 
            SET local_score=%s, last_star_time=%s, last_star_date=%s, stars=%s, global_score=%s
            WHERE user_id=%s;""", (local_score, time, date, stars, global_score, user_id))

    ##################################################

        completion_table = current_user['completion_day_level']

        # day is the number of the day (1-25). May appear in wrong order but this can be fixed by sorting
        # in desired way when presenting database, storage is not as important
        for day in completion_table:
            dayDict = completion_table[day]

            # If the day exists in the completion_table, Part 1 is guaranteed to be in it. Part 2 may be missing
            # so we need to try-except it.
            part1 = dayDict['1']
            part2 = dict()
            try:
                part2 = dayDict['2']
            except KeyError:
                #print("No p2")
                part2 = 0

            # Fetches timestamp from Part 1 (star_index is used to determine ties where 2 people have the same timestamp)
            get_star_ts = tools.unix_to_human(part1['get_star_ts'])
            time = get_star_ts[0]
            date = get_star_ts[1]
            star_index = part1['star_index']

            cursor.execute("""INSERT INTO days_completed (user_id, calendar_day, part, get_star_time, get_star_date, star_index) 
            VALUES (%s,%s,1,%s,%s,%s)
            ON CONFLICT (user_id, calendar_day, part) DO NOTHING;""", (user_id, day, time, date, star_index))
                
            

            if part2:
                get_star_ts = tools.unix_to_human(part2['get_star_ts'])
                time = get_star_ts[0]
                date = get_star_ts[1]
                star_index = part2['star_index']
                cursor.execute("""INSERT INTO days_completed (user_id, calendar_day, part, get_star_time, get_star_date, star_index) 
                VALUES (%s,%s,2,%s,%s,%s )
                ON CONFLICT (user_id, calendar_day, part) DO NOTHING;""", (user_id, day, time, date, star_index))

    connection.commit()
    cursor.close()
    connection.close()

main()
