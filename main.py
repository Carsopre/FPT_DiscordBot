from keep_alive import keep_alive
from typing import Optional, List
from pydatinc import BaseClass as DataClass
import discord
import datetime
import os

# Gif libraries.
import random
import json
import requests


client = discord.Client()
discord_key = os.getenv("DISCORD_TOKEN")


class SpamUser(DataClass):
    discriminator: int
    search_terms: List[str]
    last_mssg: Optional[datetime.datetime]


gabri_spam = SpamUser(
    **{
        "discriminator": os.getenv("gabri_discriminator"),
        "search_terms": ["coffee", "spaghetti", "pasta", "pineapple pizza"],
    }
)
tim_spam = SpamUser(
    **{
        "discriminator": os.getenv("tim_discriminator"),
        "search_terms": ["dance", "fresh-prince", "he-man", "mary-poppins"],
    }
)


def find_gif(search_term: str) -> str:
    # set the apikey and limit
    tenorgif_key = os.getenv("TENOR_TOKEN")
    lmt = 40

    # get the top "lmt" GIFs for the search term
    r = requests.get(
        f"https://api.tenor.com/v1/search?q={search_term}&key={tenorgif_key}&limit={lmt}"
    )

    if r.status_code == 200:
        # load the GIFs using the urls for the smaller GIF sizes
        results = json.loads(r.content)["results"]
        selected_gif = results[random.randint(0, len(results) - 1)]
        return selected_gif["url"]
    return ""


async def time_to_spam(message):
    spam_users: List[SpamUser] = [gabri_spam, tim_spam]
    user_to_spam = next(
        (
            spam_user
            for spam_user in spam_users
            if spam_user.discriminator == message.author.discriminator
        ),
        None,
    )
    if not user_to_spam:
        return

    now_time: datetime.datetime = datetime.datetime.now()
    if not user_to_spam.last_mssg or (
        now_time - user_to_spam.last_mssg > datetime.timedelta(minutes=60)
    ):
        search_idx = random.randint(0, len(user_to_spam.search_items) - 1)
        gif = find_gif(user_to_spam.search_items[search_idx])
        default_mssg = f"Ey {message.author.mention} bring me coffee."
        await message.channel.send(default_mssg)
        if gif:
            await message.channel.send(gif)
        # Update timestamp.
        user_to_spam.last_mssg = now_time


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        # Avoid infinite loop!
        return
    mssg_chn = message.channel
    if mssg_chn.category.name == "FPT INTERNAL" and mssg_chn.name == "general":
        time_to_spam(message)

    messages_to_filter = [
        "hail hydra",
        "heil hydra",
        "dhydro",
        "dhydra",
        "d-hydro",
        "d-hydra",
    ]
    mssg_contnt = message.content.lower()
    if any(mssg in mssg_contnt for mssg in messages_to_filter):
        gif = find_gif("hail-hydra")
        if gif:
            await mssg_chn.send(gif)
        else:
            await mssg_chn.send("Heil hydra (couldn't find gifs soz).")


keep_alive()
client.run(discord_key)
