from psnawp_api import PSNAWP
import os
from dotenv import load_dotenv

load_dotenv()

npsso = os.getenv("NPSSO")

client = PSNAWP(npsso)

user = client.user(online_id="mdicus96")
title_iterator = user.title_stats()
for title in title_iterator:
    print(f"Title: {title.name}")
    print(f"Title ID: {title.title_id}")
    print(f"Platform: {title.category}")
    print(f"Image URL: {title.image_url}")
    print(f"Play Count: {title.play_count}")
    print(f"First Played: {title.first_played_date_time}")
    print(f"Last Played: {title.last_played_date_time}")
    print(f"Play Duration: {title.play_duration}")
    print("------------------------")
