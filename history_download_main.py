from utils import download_guild_history_by_name
from dotenv import load_dotenv
import discord
import asyncio
import os
import json


ENV_FILE='.env_history_download'
load_dotenv(dotenv_path=ENV_FILE, override=True)

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
    guild = discord.utils.get(client.guilds, name=DISCORD_GUILD)

    for guild in client.guilds:
        print(f'Hisotry download Guild: {guild.name}')
        for channel in guild.text_channels:
            print(f'History download Channel: {channel.name}')

    output_file = f'{DISCORD_GUILD}_{DISCORD_CHANNEL}.json'
    try:
        msg_list, msg_dict = await download_guild_history_by_name(client, DISCORD_GUILD, DISCORD_CHANNEL)
        print(f'msg_list: {msg_list}')
        # save to file
        with open(output_file, 'w') as f:
            json.dump(msg_list, f, indent=2)
        print(f'History download saved to {output_file}')
    except Exception as e:
        print(f'Error during history download: {e}')
    print(f'History download completed for {DISCORD_GUILD} - {DISCORD_CHANNEL}')

    try:
        # read the list of messages from the file
        # and convert to discord.Message objects
        with open(output_file, 'r') as f:
            msg_list = json.load(f)
    except Exception as e:
        print(f'Error reading messages from file: {e}')




# Schedule background task before starting the bot
async def main():
    await client.start(DISCORD_BOT_TOKEN)  # Replaces client.run()

asyncio.run(main())  # Start everything