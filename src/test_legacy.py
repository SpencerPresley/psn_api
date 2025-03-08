from psnawp_api import PSNAWP
import os
from dotenv import load_dotenv

load_dotenv()

npsso = os.getenv("NPSSO")

client = PSNAWP(npsso)

user = client.user(online_id="mdicus96")
print(user)

print(user.trophy_summary())
