import asyncio
import os
import pickle
import sys
from typing import Annotated
import aiohttp
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands
import autogen
import os
from autogen import AssistantAgent, ConversableAgent
from autogen import AFTER_WORK, ON_CONDITION, AfterWorkOption, SwarmAgent, SwarmResult, initiate_swarm_chat

from autogen.agentchat.contrib.capabilities.teachability import Teachability
from pydantic import BaseModel

# used implicitly by pipe.load_pickle
import data_definition
from data_definition import MessageHistory
from utils import async_pickle_load # type: ignore
import json

#   source ./venv/bin/activate

class DataProcesser:
    def __init__(self) -> None:
        pass
        
    def process(self, msg):
        msgstr = '[' + msg['timestamp'] + '] ' + msg['author'] + ': ' + msg['content'] + '\n'

        return msgstr


# rudy server token

env_file = sys.argv[1]
print(f"env_file from bot_in_private: {env_file}")
load_dotenv(dotenv_path=env_file, override=True)
open_ai_key = os.environ["OPENAI_API_KEY"]
config_list = [{"model": "gpt-4o-mini", "api_key": open_ai_key}]

# create an AssistantAgent instance named "assistant" with the LLM configuration.
assistant = AssistantAgent(name="assistant", llm_config={"config_list": config_list})

def founder_mentioned(context_variables: dict) -> SwarmResult:
    # Returning the updated context so the shared context can be updated
    # how to access the message passed to the agent.
    # then decide to update context variables or not.
    context_variables["founder_mentioned"] = True
    return SwarmResult(context_variables=context_variables)


def history_split(context_variables: dict) -> SwarmResult:
    # Returning the updated context so the shared context can be updated
    # how to access the message passed to the agent.
    # then decide to update context variables or not.
    return SwarmResult(context_variables=context_variables)

teachability = Teachability(
    verbosity=0,  # 0 for basic info, 1 to add memory operations, 2 for analyzer messages, 3 for memo lists.
    reset_db=True,
    path_to_db_dir="./tmp/notebook/teachability_db",
    recall_threshold=1.5,  # Higher numbers allow more (but less relevant) memos to be recalled.
)


founder_list = []

llm_config = {"config_list": [{"model": "gpt-4", "api_key": os.environ["OPENAI_API_KEY"]}]}

context_variables = {
    "founder_mentioned": False,
    "business_theme": False,
}

user_proxy_agent = ConversableAgent(
    name="UserProxyAgent",
    system_message="You are a user who want to analyze the business themes from the chat history.",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": open_ai_key}]},
)



class ReplyFormat(BaseModel):
    need_human_reply_score: Annotated[int, "Must be between 1 and 10"]
    reason: str
    response: str

founder_actor_agent = SwarmAgent(
    name="Founder_Actor_Agent",
    system_message="""You are a founder actor of the company.
    """,
    llm_config={"config_list": [{
        "model": "gpt-4o-mini",
        "api_key": os.environ["OPENAI_API_KEY"],
        "response_format": ReplyFormat,
        }]},
    #summary_method="reflection_with_llm",
    #functions=[founder_mentioned]
)

# first time chat takes 10s of seconds  to load the vector database
teachability.add_to_agent(founder_actor_agent)

conversation_split = SwarmAgent(
    name="conversation_split",
    system_message="You are a expert who can split the conversation history from several part. each part is a whole conversation of a topic.",
    llm_config={"config_list": [{"model": "gpt-4o-mini", "api_key": open_ai_key}]},
    #functions=[history_split]
)

topic_group = SwarmAgent(
    name="topic_group",
    system_message="you are a expert who can summarize the conversation topic and aggregate the same topic",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": open_ai_key}]},
)

business_theme_agent = SwarmAgent(
    name="business_theme_agent",
    system_message="You are a business analyst who excels at discovering business themes in conversation transcripts.",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": open_ai_key}]},
)

nested_chats = [
    {
        "recipient": conversation_split,
        "summary_method": "reflection_with_llm",
        "summary_prompt": "Please split the conversation history into several parts, each part is a whole conversation of a topic.",
    },
    {
        "recipient": topic_group,
        "message": "Please organize the conversation history into topics.",
        "summary_method": "reflection_with_llm",
    },
    {
        "recipient": business_theme_agent,
        "message": "Please find the business theme from the conversation history or the last message.",
        "max_turns": 1,
        "summary_method": "last_msg",
    },
]

#founder_actor_agent.register_nested_chats(
#    nested_chats,
#    trigger=lambda sender: sender not in [conversation_split, topic_group, business_theme_agent],
#)


TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD = os.getenv("DISCORD_GUILD") #"rudyrrr_server"
#GUILD = "AG2 (aka AutoGen)"
#GUILD = 'GroupManagerV1'
CHANNEL= 'general' #os.getenv("DISCORD_CHANNEL")

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


#class Message:
#    def __init__(self, msg_list: list, msg_dict: dict):
#        self.msg_list = msg_list
#        self.msg_dict = msg_dict


@client.event
async def on_message(message):
    if message.author == client.user:  # ignore the message from the bot itself
        return
    print(f"Message received in private: {message.content}, author: {message.author}, user: {client.user}")
    channel = message.channel
    pipe_name_private_to_public = sys.argv[3]
    print(f"pipe_name from bot_in_private: {pipe_name_private_to_public}")

    # teach the message to the founder_actor_agent

    if not os.path.exists(pipe_name_private_to_public):
        os.mkfifo(pipe_name_private_to_public)
    try:
        with open(pipe_name_private_to_public, "wb") as pipe:
            print(f"pipe_name opened: {pipe_name_private_to_public}")
            pickle.dump(message.content,pipe)
        print(f"Message sent to pipe: {message.content}")
    except Exception as e:
        print(f"Error sending message to pipe in private: {e}")

    await channel.send('Echo from private:' + message.content)


@client.event
async def setup_hook():
  await tree.sync()

print(f"TOKEN in bot_in_private: {TOKEN}")





async def listen_public_pipe_message(client):
    await client.wait_until_ready()  # Wait until the bot is fully ready
    pipe_name_public_to_private = sys.argv[2]
    print(f"pipe_name from bot_in_private: {pipe_name_public_to_private}")

    general_channel = None

    while True:
        if general_channel is None:
            for guild in client.guilds:
                print(f'Private Guild: {guild.name}')
                for channel in guild.text_channels:
                    if channel.name == 'general':
                        general_channel = channel
                        print(f'Found general channel: {general_channel.name}')
                    print(f'guild:{guild.name}, channel: {channel.name}')
        else:
            print(f"general_channel: {general_channel}")
        try:
            print(f"inside background_task, pipe_name: {pipe_name_public_to_private}")
            message_data = await async_pickle_load(pipe_name_public_to_private) 
            print(f"Processing message from pipe in private: {message_data.msg_list}")
            last_msg = message_data.msg_list[0]['content']
            history = message_data.msg_list[0]['content']
            all_history = ''
            for msg in message_data.msg_list:
                all_history += 'author:' + msg['author'] + ' content:' + msg['content'] + '\n'
            print(f"all_history: {all_history}")

            use_group_chat = True
            if use_group_chat:
                chat_result, context_variables, last_agent = initiate_swarm_chat(
                    initial_agent=conversation_split,
                    agents=[conversation_split, topic_group, business_theme_agent],
                    messages="Please summarize the chat history." + all_history,
                    #context_variables=shared_context,
                )
                reply_result = user_proxy_agent.initiate_chat(
                    founder_actor_agent,
                    message=f"Please try to reply to the message based on the chat history summary.  {chat_result.summary}. ",
                    summary_method="reflection_with_llm",
                    max_turns=1,
                )
                print(f"reply_result: {reply_result.summary}")
                try:
                    parsed_json = json.loads(reply_result.summary)  # Invalid JSON (extra comma)
                    if parsed_json['need_human_reply_score'] > -1:
                        print(f'need_human_reply')
                        msg = f'Received message from server: {all_history} Suggested reply: {reply_result.summary}'
                        await general_channel.send(msg[:1900])
                        # at most 2000 characters
                    else:
                        print(f'no need_human_reply')
                        pipe_name_private_to_public = sys.argv[3]
                        print(f"pipe_name from bot_in_private: {pipe_name_private_to_public}")

                        if not os.path.exists(pipe_name_private_to_public):
                            os.mkfifo(pipe_name_private_to_public)
                        try:
                            with open(pipe_name_private_to_public, "wb") as pipe:
                                print(f"pipe_name opened: {pipe_name_private_to_public}")
                                pickle.dump(parsed_json['response'],pipe)
                            print(f"AI Reply Message sent to pipe in private:: {parsed_json['response']}")
                        except Exception as e:
                            print(f"Error sending message to pipe in private: {e}")
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error: {e}")
            else:
                chat_result = founder_actor_agent.generate_reply(
                    summary_method="reflection_with_llm",
                    max_turns=2,
                    messages=[{"role": "user",
                            "content": f"Please analyze the chat or chat history: {history}"}]
                )

                print(f"chat_result: {chat_result}")
                await general_channel.send('Received message from server:' + str('test') + ' summary: ' + chat_result.summary)

        except Exception as e:
            print(f"Error processing message in private: {e}")
            await asyncio.sleep(1)  # Prevent excessive CPU usage

# Schedule background task before starting the bot
async def main():
    asyncio.create_task(listen_public_pipe_message(client))  # Run in parallel
    await client.start(TOKEN)  # Replaces client.run()

asyncio.run(main())  # Start everything
