from keep_alive import keep_alive
import discord
import os

# Gif libraries.
import random
import json
import requests

client = discord.Client()
search_term = "hail-hydra"

def find_gif() -> str:
    # set the apikey and limit
    tenorgif_key = os.getenv("TENOR_TOKEN")
    lmt = 40

    # our test search

    # get the top 8 GIFs for the search term
    r = requests.get(
        f"https://api.tenor.com/v1/search?q={search_term}&key={tenorgif_key}&limit={lmt}")

    if r.status_code == 200:
        # load the GIFs using the urls for the smaller GIF sizes
        results = json.loads(r.content)['results']
        selected_gif = results[random.randint(0, len(results) - 1)]
        return selected_gif['url']
    return None    

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    messages_to_filter = ["hail hydra", "heil hydra", "dhydro", "dhydra", "d-hydro", "d-hydra"]
    mssg_contnt = message.content.lower()
    if any(mssg in mssg_contnt for mssg in messages_to_filter):
        gif = find_gif()
        if gif:
            await message.channel.send(gif)
        else:
            await message.channel.send("Heil hydra (couldn't find gifs soz).")
discord_key = os.getenv("DISCORD_TOKEN")
keep_alive()
client.run(discord_key)
