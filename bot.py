import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Get API keys and MongoDB URI from environment
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")  # e.g., 'mongodb://localhost:27017/'

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up intents
intents = discord.Intents.default()
intents.message_content = True  # Enable additional intents as needed

# Initialize the bot with a command prefix and intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Set up OpenAI API client
client = OpenAI()

# Set up MongoDB client
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client["discord_bot"]  # Database name
conversations_collection = db["conversations"]  # Collection name

# Track whether the user is in 'ask' mode
user_ask_mode = {}


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
    # Initialize conversation history in the database
    conversations_collection.update_one(
        {"user_id": ctx.author.id}, {"$set": {"messages": []}}, upsert=True
    )
    await ctx.send("Fire away!")


# Handle messages
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    if user_ask_mode.get(message.author.id):
        # Retrieve the user's conversation history from the database
        user_conversation = conversations_collection.find_one(
            {"user_id": message.author.id}
        )
        if user_conversation:
            conversation_history = user_conversation.get("messages", [])
        else:
            conversation_history = []

        # Append user message to conversation history
        conversation_history.append({"role": "user", "content": message.content})

        # Send the conversation history to ChatGPT
        chat_completion = client.chat.completions.create(
            model="gpt-4", messages=conversation_history
        )

        # Get the ChatGPT response
        chatgpt_reply = chat_completion.choices[0].message.content
        await message.channel.send(chatgpt_reply)

        # Append ChatGPT's reply to the conversation history
        conversation_history.append({"role": "assistant", "content": chatgpt_reply})

        # Update the conversation history in the database
        conversations_collection.update_one(
            {"user_id": message.author.id}, {"$set": {"messages": conversation_history}}
        )

        # Optionally, clear the ask mode
        # user_ask_mode[message.author.id] = False


# Run the bot
bot.run(DISCORD_TOKEN)
