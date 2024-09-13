import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv

from openai import OpenAI

load_dotenv()

client = OpenAI(
    # Defaults to os.environ.get("OPENAI_API_KEY")
)

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up intents
intents = discord.Intents.default()
intents.message_content = True  # Enable additional intents as needed

# Initialize the bot with a command prefix and intents
bot = commands.Bot(command_prefix="!", intents=intents)


# Event when the bot is ready
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


# Define a ping command
@bot.command(name="ping")
async def ping(ctx):
    # Send a message with the bot's latency
    await ctx.send(f"Pong! Latency is {round(bot.latency * 1000)}ms")


# Define a hello command
@bot.command(name="hello")
async def hello(ctx):
    await ctx.send("Hello!")


# Define the 'ask' command
@bot.command(name="ask")
async def ask(ctx):
    user_ask_mode[ctx.author.id] = True
    await ctx.send("Fire away!")


# Track whether the user is in 'ask' mode
user_ask_mode = {}


# Handle messages
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    if user_ask_mode.get(message.author.id):
        # Send the user's message to ChatGPT

        chat_completion = client.chat.completions.create(
            model="gpt-4", messages=[{"role": "user", "content": message.content}]
        )
        chatgpt_reply = chat_completion.choices[0].message.content
        await message.channel.send(chatgpt_reply)

        # Disable 'ask' mode for the user after receiving a response
        user_ask_mode[message.author.id] = False


# Run the bot
bot.run(TOKEN)
