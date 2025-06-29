import discord
import pickle
import asyncio

async def async_pickle_load(pipe_name):
    def load_pickle():
        with open(pipe_name, "rb") as pipe:
            return pickle.load(pipe)  # Blocking call

    return await asyncio.to_thread(load_pickle)  # Run in a separate thread


# not working
#with open(pipe_name_private_to_public, "rb") as pipe:
#               print(f"pipe opened server: {pipe}")
#              message_data = await async_pickle_load2(pipe)
async def async_pickle_load2(pipe):
    """Runs pickle.load() asynchronously using a separate thread."""
    return await asyncio.to_thread(pickle.load, pipe)  # Non-blocking

# Not Tested yet
async def download_guild_history_by_name(client, guild_name, channel_name):
    guild = discord.utils.get(client.guilds, name=guild_name)
    channel = discord.utils.get(guild.text_channels, name=channel_name)
    return await download_channel_history(client, guild, channel)

# Not Tested yet
async def download_guild_history_raw_by_name(client, guild_name, channel_name):
    guild = discord.utils.get(client.guilds, name=guild_name)
    channel = discord.utils.get(guild.text_channels, name=channel_name)

    msg_list = []
    async for message in channel.history(limit=5, oldest_first=False):
        print(f"download_channel_history: message: {message}")
        msg_list.append(message)
    


async def download_channel_history(client, guild, channel):
    print(f"download_channel_history: {guild.name}, {channel.name}")
    msg_list = []
    message_dict = {}  # Dictionary to store messages by their IDs
    replied_to_message_ids = set()  # Set to keep track of message IDs that have replies

    # for tguild in client.guilds:
    #     print(f'Util Guild log: {tguild.name}')
    #     for tchannel in tguild.text_channels:
    #         print(f'Found channel log: {tchannel.name}')


    async for message in channel.history(limit=5, oldest_first=False):
        print(f"download_channel_history: message: {message}")
        message_data = {
            "id": str(message.id),
            "author": str(message.author),
            "content": message.content,
            "timestamp": str(message.created_at),
            "link": f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}",
            "is_thread": message.reference is None,  # Major thread if no reference
            "is_reply": message.reference is not None,  # Reply if there is a reference
            "author_is_bot": message.author.bot,  # Check if the author is a bot
            "guild_channel": f"{guild.name}_{channel.name}"
        }


        if message.reference:
            message_data["reply_to_message_id"] = message.reference.message_id
            replied_to_message_ids.add(message.reference.message_id)
            # Find the original thread
            original_thread = find_original_thread(message.reference.message_id, message_dict)
            message_data["original_thread_id"] = original_thread.get("id") if original_thread else None
        else:
            message_data["original_thread_id"] = message.id

        msg_list.append(message_data)
        message_dict[message.id] = message_data  # Add message to dictionary
    return msg_list, message_dict

def find_original_thread(message_id, message_dict):
    # Recursively find the original thread by following the chain of references
    while message_id in message_dict:
        message = message_dict[message_id]
        if message["is_thread"]:
            return message
        message_id = message.get("reply_to_message_id")
    return None