from pydantic.errors import DataclassTypeError
from keep_alive import keep_alive
from typing import Optional, List, Dict, Union
from pydantic import BaseModel as DataClass
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
    user_name: str
    discriminator: str
    search_terms: List[str]
    last_mssg: Optional[datetime.datetime]


class UsersToSpam(DataClass):
    users: List[SpamUser]

    def get_user_by_discriminator(self, discriminator: str) -> Union[SpamUser, None]:
        """Retrieves the user whose discriminator matches the one given.

        Args:
            discriminator (str): Discriminator to be found.

        Returns:
            Union[SpamUser, None]: Associated user to the discriminator or None if not found.
        """
        return next(
            (
                spam_user
                for spam_user in users_to_spam.users
                if spam_user.discriminator == discriminator
            ),
            None,
        )


default_starttime = datetime.datetime(2021, 1, 1)
default_goodboy_until = datetime.timedelta(
    seconds=300
)  # 5 minutes of silence in this channel
muted_channels: Dict[str, datetime.datetime] = {}


def get_users_to_spam() -> List[SpamUser]:
    """Retrieves the list of users that will be spammed.

    Returns:
        List[SpamUser]: List of users that can be spammed.
    """

    def get_spam_user(name: str, terms: List[str]) -> SpamUser:
        return SpamUser(
            user_name=name,
            discriminator=os.getenv(f"{name}_discriminator"),
            search_terms=terms,
            last_mssg=default_starttime,
        )

    return [
        get_spam_user("gabri", ["coffee", "spaghetti", "pasta", "pineapple pizza"]),
        get_spam_user("tim", ["god", "fresh-prince", "he-man", "all-mighty"]),
        get_spam_user("dennis", ["matrix", "unicorn", "dungeon", "spending-money"]),
        get_spam_user(
            "maarten", ["matrix", "frog", "breakingbad", "dexters laboratory"]
        ),
        get_spam_user("prisca", ["cat", "matrix"]),
        get_spam_user("robin", ["baby", "fire", "spongebob", "matrix"]),
    ]


users_to_spam = UsersToSpam(users=get_users_to_spam())


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


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


async def on_time_to_spam(message):
    last_time = max(spam_user.last_mssg for spam_user in users_to_spam.users)
    user_to_spam: SpamUser = users_to_spam.get_user_by_discriminator(
        message.author.discriminator
    )
    if user_to_spam is None:
        print(
            f"No user found to spam with discriminator {message.author.discriminator}"
        )
        return

    now_time = datetime.datetime.now()
    if (now_time - last_time) > datetime.timedelta(minutes=60):
        search_idx = random.randint(0, len(user_to_spam.search_terms) - 1)
        gif = find_gif(user_to_spam.search_terms[search_idx])
        default_mssg = f"Ey {message.author.mention} bring me coffee."
        # Update timestamp.
        user_to_spam.last_mssg = now_time
        await message.channel.send(default_mssg)
        if gif:
            await message.channel.send(gif)


async def on_reply_to_filter_mssg(message, filter_mssgs: List[str], find_str: str):
    mssg_contnt = message.content.lower()
    if any(mssg in mssg_contnt for mssg in filter_mssgs):
        gif = find_gif(find_str)
        if gif:
            await message.channel.send(gif)
        else:
            await message.channel.send(
                f"{find_str.capitalize()}! (Couldn't find gifs soz)."
            )


@client.event
async def on_message(message):

    mute_keywords = ["/badbot", "/badboy", "/mutebot"]
    unmute_keywords = ["/goodbot", "/goodboy", "/unmutebot"]

    if message.author == client.user:
        # Avoid infinite loop!
        return
    mssg_chn = message.channel
    if isinstance(mssg_chn, discord.DMChannel):
        # Don't talk to strangers :(
        return
    if (
        mssg_chn.category.name.lower() == "fpt internal"
        and mssg_chn.name.lower() == "general"
    ):
        await on_time_to_spam(message)

    def mute_until() -> datetime.datetime:
        return datetime.datetime.now() + default_goodboy_until

    if message.content.lower() in mute_keywords:
        muted_channels[mssg_chn] = mute_until()
        await message.channel.send(
            "Sorry, I'll be a good bot for a while :cry: :innocent:"
        )
        return
    if message.content.lower() in unmute_keywords:
        muted_channels.pop(message.channel, None)  # Remove from list if it was muted.
        await message.channel.send("Thank you good lord.")
        return

    mc = muted_channels.get(message.channel, None)
    if mc is not None:
        if mc > datetime.datetime.now():
            # Channel is still muted.
            return
        elif mc <= datetime.datetime.now():
            await message.channel.send("I was a good boy for a while now.")
            muted_channels.pop(message.channel)

    await on_reply_to_filter_mssg(
        message,
        ["hail hydra", "heil hydra", "dhydro", "dhydra", "d-hydro", "d-hydra",],
        "hail-hydra",
    )
    await on_reply_to_filter_mssg(
        message,
        ["good morning", "goodmorning", "goedemorgen", "buon giorno",],
        "good morning",
    )


keep_alive()
client.run(discord_key)
