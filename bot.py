import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from pymongo import MongoClient

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True  
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

client = OpenAI()

mongo_client = MongoClient(MONGODB_URI)
db = mongo_client["discord_bot"]
conversations_collection = db["conversations"]

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
        user_conversation = conversations_collection.find_one(
            {"user_id": message.author.id}
        )
        if user_conversation:
            conversation_history = user_conversation.get("messages", [])
        else:
            conversation_history = []

        conversation_history.append(
            {"role": "user", "content": message.content})

        chat_completion = client.chat.completions.create(
            model="gpt-4", messages=conversation_history
        )

        chatgpt_reply = chat_completion.choices[0].message.content
        await message.channel.send(chatgpt_reply)

        conversation_history.append(
            {"role": "assistant", "content": chatgpt_reply})

        conversations_collection.update_one(
            {"user_id": message.author.id}, {
                "$set": {"messages": conversation_history}}
        )

        # Optionally, clear the ask mode
        # user_ask_mode[message.author.id] = False


# Run the bot


# Event that triggers when a member joins the server
@bot.event
async def on_member_join(member):
    print(f"New member joining server: {member.display_name} at {member.joined_at}")
    
    channel = bot.get_channel(CHANNEL_ID)
    
    if channel is None:
        print("Channel not found. Please check the CHANNEL_ID.")
        return

    welcome_message = f"Welcome to the server, {member.mention}! 🎉 We're glad to have you here!"
    
    try:
        await channel.send(welcome_message)
        print(f"Sent welcome message to {member.display_name} in channel {channel.name}.")
        
        # Optionally, send a DM to the new member
        await member.send(f"Hi {member.name}, welcome to our Discord server! Feel free to ask if you need any help.")
    except discord.Forbidden:
        print(f"Couldn't send a DM to {member.name} due to privacy settings.")
    except Exception as e:
        print(f"An error occurred: {e}")
bot.run(DISCORD_TOKEN)
