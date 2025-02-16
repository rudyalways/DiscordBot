# instructions:
# create your .env_bot_rudy_server and .env_bot_rudy_private
# example:
# DISCORD_BOT_TOKEN=your_token_here
# OPENAI_API_KEY=your_openai_key_here
# GUILD=your_guild_name_here
# CHANNEL=your_channel_name_here

import subprocess
import os
import time
import pickle

PIPE_FILE_PUBLIC_TO_PRIVATE = "message_public_to_private.pipe"
PIPE_FILE_PRIVATE_TO_PUBLIC = "message_private_to_public.pipe"

# Ensure a clean pipe file
if os.path.exists(PIPE_FILE_PUBLIC_TO_PRIVATE):
    os.remove(PIPE_FILE_PUBLIC_TO_PRIVATE)
os.mkfifo(PIPE_FILE_PUBLIC_TO_PRIVATE)

if os.path.exists(PIPE_FILE_PRIVATE_TO_PUBLIC):
    os.remove(PIPE_FILE_PRIVATE_TO_PUBLIC)
os.mkfifo(PIPE_FILE_PRIVATE_TO_PUBLIC)

# Define bot configurations
bot1_env = ".env_bot_rudy_server"
bot2_env = ".env_bot_rudy_private"

# Start two Discord bot instances
# read message from server and write to pipe
bot1 = subprocess.Popen(["python", "bot_on_server.py",  bot1_env, PIPE_FILE_PUBLIC_TO_PRIVATE, PIPE_FILE_PRIVATE_TO_PUBLIC])
# read message from pipe and process it
bot2 = subprocess.Popen(["python", "bot_in_private.py",  bot2_env, PIPE_FILE_PUBLIC_TO_PRIVATE, PIPE_FILE_PRIVATE_TO_PUBLIC])

print("Main script is running, two bots started")

# Keep the main script alive to monitor processes
try:
    while True:
        time.sleep(10)
        #print(f"Main script is running bot1: {bot1.pid}, bot2: {bot2.pid}")
except KeyboardInterrupt:
    print("Shutting down bots...")
    bot1.terminate()
    bot2.terminate()
