from utils import download_guild_history_raw_by_name
from dotenv import load_dotenv
import discord
import asyncio
import os
import json

load_dotenv(override=True)

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_GUILD = os.getenv('DISCORD_GUILD')
DISCORD_CHANNEL = os.getenv('DISCORD_CHANNEL')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    for guild in client.guilds:
        print(f'Hisotry download Guild: {guild.name}')
        for channel in guild.text_channels:
            print(f'History download Channel: {channel.name}')
    msg_list = await download_guild_history_raw_by_name(client, DISCORD_GUILD, DISCORD_CHANNEL)
    print(f'msg_list: {msg_list}')
    # save to file
    with open(f'{DISCORD_GUILD}_{DISCORD_CHANNEL}.json', 'w') as f:
        json.dump(msg_list, f)


# Schedule background task before starting the bot
async def main():
    await client.start(DISCORD_BOT_TOKEN)  # Replaces client.run()

asyncio.run(main())  # Start everything