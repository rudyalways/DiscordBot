import asyncio
import os
import pickle
import sys
import aiohttp
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands
import autogen
import os
from autogen import AssistantAgent, ConversableAgent
from utils import download_channel_history, find_original_thread, async_pickle_load # type: ignore
# AFTER_WORK, ON_CONDITION, AfterWorkOption
from autogen.agentchat.contrib.swarm_agent import SwarmResult, initiate_swarm_chat
#from data_process import DataProcesser

import data_definition
from data_definition import MessageHistory

#   source ./venv/bin/activate

class DataProcesser:
    def __init__(self) -> None:
        pass
        
    def process(self, msg):
        msgstr = '[' + msg['timestamp'] + '] ' + msg['author'] + ': ' + msg['content'] + '\n'

        return msgstr


# rudy server token

env_file = sys.argv[1]
load_dotenv(dotenv_path=env_file, override=True)
open_ai_key = os.environ["OPENAI_API_KEY"]
config_list = [{"model": "gpt-4", "api_key": open_ai_key}]

# create an AssistantAgent instance named "assistant" with the LLM configuration.
assistant = AssistantAgent(name="assistant", llm_config={"config_list": config_list})

def history_split(context_variables: dict) -> SwarmResult:
    """Record the lesson plan"""

    # Returning the updated context so the shared context can be updated
    return SwarmResult(context_variables=context_variables)

conversation_split = ConversableAgent(
    name="conversation_split",
    system_message="You are a expert who can split the conversation history from several part. each part is a whole conversation of a topic.",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": open_ai_key}]},
    functions=[history_split]
)
topic_group = ConversableAgent(
    name="topic_group",
    system_message="you are a expert who can summarize the conversation topic and aggregate the same topic",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": open_ai_key}]},
)


user_proxy_agent = ConversableAgent(
    name="UserProxyAgent",
    system_message="You are a user who want to analyze the business themes from the discord channel.",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": open_ai_key}]},
)
assistant_agent = ConversableAgent(
    name="AsistantAgent",
    system_message="You are a business analyst who excels at discovering business themes in conversation transcripts.",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": open_ai_key}]},
)


TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD = os.getenv("DISCORD_GUILD") #"rudyrrr_server"
#GUILD = "AG2 (aka AutoGen)"
#GUILD = 'GroupManagerV1'
CHANNEL= 'general' #os.getenv("DISCORD_CHANNEL")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    print(TOKEN)
    print(f'Logged in as {client.user}!')

    for guild in client.guilds:
          for channel in guild.text_channels:
              print(f'guild:{guild.name}, channel: {channel.name}')
    print(f'Logged in as {client.user}!')
    await tree.sync()

    #await client.close()

@tree.command(name="tell-me-a-joke", description="Get a random dad joke")
async def tell_me_a_joke(interaction: discord.Interaction):
  print(f"interaction: {interaction}")
  async with aiohttp.ClientSession() as session:
    site = await session.get(
        "https://icanhazdadjoke.com/",
        headers={
            "Accept": "application/json",
        },
    )
  data = await site.json()
  #await interaction.response.send_message(data["joke"])

@tree.command(name="summarize", description="Summarize the history")
async def summarize(interaction: discord.Interaction):
  print(f"interaction: {interaction}")
  data_processer = DataProcesser()
  msg_list,msg_dict = await download_channel_history(client, GUILD, CHANNEL)

  history = ''
  for msgid, msg in msg_dict.items():
      print(msg)
    #   msgstr = 'timestamp:' + msg['timestamp'] + ', author:' + msg['author'] + ', content: ' + msg['content'] + '\n'
      msgstr = data_processer.process(msg)
      history+= msgstr

  print(history)


  #await interaction.response.send_message('got all messages')
  groupchat = autogen.GroupChat(
    agents=[user_proxy_agent, conversation_split, topic_group, assistant_agent], messages=[], max_round=4, speaker_selection_method='round_robin'
    )
  manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={"config_list": [{"model": "gpt-4o-mini", "api_key": open_ai_key}]})
  chat_result = user_proxy_agent.initiate_chat(
      manager,
      message="What are the top feature requests in the discord chat history: " + history,
      summary_method="reflection_with_llm",
      max_turns=1,
  )
  # TODO, post a message, got message id, update message
  
  # await interaction.response.send_message(chat_result.summary)


  #print(msgs)



@client.event
async def on_message(message):
    message_guild = message.guild
    message_channel = message.channel
    
    founder_list = ['rudyrrr'] # to update

    if message.author == client.user:  # ignore the message from the bot itself
        return
    if message.author in founder_list:  # ignore the message from the founder
        return
    if "@" in message.content:  # ignore the message from the founder
        # Extract user ID from message
        content = message.content
        start_idx = content.find('@') + 1
        end_idx = content.find(' ', start_idx) if ' ' in content[start_idx:] else len(content)
        mentioned_user = content[start_idx:end_idx]
        if mentioned_user not in founder_list:
            print(f"Mentioned user: {mentioned_user}")
            #return
    
    print(f"Message received: {message.content}, author: {message.author}, user: {client.user}")
    channel = message.channel
    pipe_name_public_to_private = sys.argv[2]
    print(f"pipe_name from bot_on_server: {pipe_name_public_to_private}")

    msg_list,msg_dict = await download_channel_history(client, message_guild, message_channel)

    print(f"msg_list: {msg_list}")

    if not os.path.exists(pipe_name_public_to_private):
        os.mkfifo(pipe_name_public_to_private)
    try:
        with open(pipe_name_public_to_private, "wb") as pipe:
            print(f"pipe_name opened: {pipe_name_public_to_private}")
            one_message = MessageHistory(msg_list,msg_dict)
            pickle.dump(one_message,pipe)
        print(f"Message sent to pipe: {message.content}")
    except Exception as e:
        print(f"Error sending message to pipe in server: {e}")

    #await channel.send('Echo from server:' + message.content)

print(f"TOKEN in bot_on_server: {TOKEN}")

@client.event
async def setup_hook():
  await tree.sync()




# not working
#with open(pipe_name_private_to_public, "rb") as pipe:
#               print(f"pipe opened server: {pipe}")
#              message_data = await async_pickle_load2(pipe)
async def async_pickle_load2(pipe):
    """Runs pickle.load() asynchronously using a separate thread."""
    return await asyncio.to_thread(pickle.load, pipe)  # Non-blocking

async def listen_private_pipe_message(client):
    await client.wait_until_ready()  # Wait until the bot is fully ready
    pipe_name_private_to_public = sys.argv[3]
    print(f"pipe_name from bot_on_server: {pipe_name_private_to_public}")

    general_channel = None

    while True:
        if general_channel is None:
            for guild in client.guilds:
                print(f'Server Guild: {guild.name}')
                for channel in guild.text_channels:
                    if channel.name == 'general':
                        general_channel = channel
                        print(f'Found general channel on server: {general_channel.name}')
                    print(f'guild:{guild.name}, channel: {channel.name}')
            print(f"general_channel: {general_channel}")
        else:
            print(f"general_channel: {general_channel}")
        try:
            print(f"inside server background_task, pipe_name: {pipe_name_private_to_public}")
            message_data = await async_pickle_load(pipe_name_private_to_public) 

            print(f"Processing message from pipe in server: {message_data}")
            # await general_channel.send('Received message from private in server:' + str(message_data))
        except Exception as e:
            print(f"Error processing message in server: {e}")
            await asyncio.sleep(1)  # Prevent excessive CPU usage

# Schedule background task before starting the bot
async def main():
    # asyncio.create_task(listen_private_pipe_message(client))  # Run in parallel
    await client.start(TOKEN)  # Replaces client.run()

asyncio.run(main())  # Start everything