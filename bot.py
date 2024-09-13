import discord
from discord.ext import commands
import logging

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the bot token from the environment
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up intents
intents = discord.Intents.default()
intents.message_content = True  # Enable additional intents as needed

# Initialize the bot with a command prefix and intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# Define a ping command
@bot.command(name='ping')
async def ping(ctx):
    # Send a message with the bot's latency
    await ctx.send(f'Pong! Latency is {round(bot.latency * 1000)}ms')

# Define a hello command
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send('Hello!')

# Run the bot
bot.run(TOKEN)
