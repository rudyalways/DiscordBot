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
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_bots.log'),
        logging.StreamHandler()  # This will show in tmux session
    ]
)

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

logging.info("Starting Discord bots...")

# Start two Discord bot instances
# read message from server and write to pipe
bot1 = subprocess.Popen(["python", "bot_on_server.py",  bot1_env, PIPE_FILE_PUBLIC_TO_PRIVATE, PIPE_FILE_PRIVATE_TO_PUBLIC])
# read message from pipe and process it
bot2 = subprocess.Popen(["python", "bot_in_private.py",  bot2_env, PIPE_FILE_PUBLIC_TO_PRIVATE, PIPE_FILE_PRIVATE_TO_PUBLIC])

logging.info(f"Main script is running, two bots started - PID1: {bot1.pid}, PID2: {bot2.pid}")

# Keep the main script alive to monitor processes
try:
    while True:
        time.sleep(60)  # Check every minute
        
        # Check if processes are still alive
        if bot1.poll() is not None:
            logging.error(f"Bot1 (server) has died with return code {bot1.returncode}")
        if bot2.poll() is not None:
            logging.error(f"Bot2 (private) has died with return code {bot2.returncode}")
            
        logging.info(f"Bots status check - Bot1 alive: {bot1.poll() is None}, Bot2 alive: {bot2.poll() is None}")
        
except KeyboardInterrupt:
    logging.info("Received shutdown signal, terminating bots...")
    bot1.terminate()
    bot2.terminate()
    
    # Wait a bit for graceful shutdown
    time.sleep(2)
    
    # Force kill if still running
    if bot1.poll() is None:
        bot1.kill()
        logging.info("Force killed bot1")
    if bot2.poll() is None:
        bot2.kill()
        logging.info("Force killed bot2")
    
    logging.info("All bots terminated")
