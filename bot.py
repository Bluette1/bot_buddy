import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from openai import OpenAI
import asyncio
import threading
from datetime import datetime
from FlaskServer import FlaskServer

load_dotenv()

# Environment Variables
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
PREMIER_CHANNEL_ID = int(os.getenv('PREMIER_CHANNEL_ID'))
ROLE_ID = int(os.getenv('ROLE_ID'))
GUILD_ID = int(os.getenv('GUILD_ID'))

# Logging setup
logging.basicConfig(level=logging.INFO)

# Discord bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# MongoDB setup
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client["discord_bot"]
conversations_collection = db["conversations"]
quotes_collection = mongo_client['quotes_db']['quotes']
# Collection to store the New Year message
messages_collection = db['messages']
client = OpenAI()


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    bot.loop.create_task(check_new_year())  # Start the New Year check task


def save_message_to_db(message_id, message):
    # Upsert: Insert if not exists, update if exists
    messages_collection.update_one(
        {"_id": message_id},
        {"$set": {"message": message}},
        upsert=True
    )



@bot.command(name='set_welcome_message', help='Set a custom welcome message for new members')
@commands.has_permissions(administrator=True)
async def set_welcome_message(ctx, *, message: str):
    guild_id = ctx.guild.id
    message_id = f"welcome_message_{guild_id}"
    save_message_to_db(message_id, message)
    await ctx.send(f"Welcome message updated to: {message}")

@bot.command(name='view_welcome_message', help='View the current welcome message')
async def view_welcome_message(ctx):
    guild_id = ctx.guild.id
    message_id = f"welcome_message_{guild_id}"
    message_data = messages_collection.find_one({"_id": message_id})
    message = message_data['message'] if message_data else "Welcome to the server! 🎉"
    await ctx.send(f"Current welcome message: {message}")

@bot.event
async def on_member_join(member):
    guild_id = member.guild.id
    message_id = f"welcome_message_{guild_id}"
    welcome_message_data = messages_collection.find_one({"_id": message_id})
    welcome_message = welcome_message_data['message'] if welcome_message_data else f"Welcome to the server, {member.mention}! 🎉 We're glad to have you here!"

    general_channel = discord.utils.get(member.guild.text_channels, name="general")
    if general_channel:
        await general_channel.send(welcome_message)
        await member.send(f"Hi {member.name}, welcome to our Discord server! Feel free to ask if you need any help.")


@bot.command(name="inspire")
async def inspire(ctx):
    quote_cursor = quotes_collection.aggregate([{"$sample": {"size": 1}}])
    quote_document = next(quote_cursor, None)
    if quote_document:
        await ctx.send(f'"{quote_document["text"]}" - {quote_document["author"]}')
    else:
        await ctx.send("Sorry, I couldn't find any quotes.")


@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"Pong! Latency is {round(bot.latency * 1000)}ms")


@bot.command(name="hello")
async def hello(ctx):
    await ctx.send("Hello!")

user_ask_mode = {}


@bot.command(name="ask")
async def ask(ctx):
    user_ask_mode[ctx.author.id] = True
    conversations_collection.update_one(
        {"user_id": ctx.author.id}, {"$set": {"messages": []}}, upsert=True
    )
    await ctx.send("Fire away!")


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

# Default celebratory message
default_message = "🎉 Happy New Year, everyone! Let's celebrate together and make this year amazing! 🎆"


@bot.command(name='set_newyear_message', help='Set a custom New Year\'s message')
@commands.has_permissions(administrator=True)
async def set_newyear_message(ctx, *, message: str):
    save_message_to_db("new_year_message", message)
    await ctx.send(f"New Year's message updated to: {message}")


@bot.command(name='view_newyear_message', help='View the current New Year\'s message')
async def view_newyear_message(ctx):
    message_data = messages_collection.find_one({"_id": "new_year_message"})
    message = message_data['message'] if message_data else default_message
    await ctx.send(f"Current New Year's message: {message}")


def load_message_from_db():
    message_data = messages_collection.find_one({"_id": "new_year_message"})
    return message_data['message'] if message_data else default_message


async def check_new_year():

    await bot.wait_until_ready()  # Ensure the bot is ready before starting the loop
    while not bot.is_closed():
        now = datetime.now()
        # Check if it's January 1st, 00:00
        # if now.month == 1 and now.day == 1 and now.hour == 0:
        if now.month == 10 and now.day == 25 and now.hour == 23:
            # Load the custom message from MongoDB
            new_year_message = load_message_from_db()
            # Send the message to a specific channel
            channel = discord.utils.get(bot.get_all_channels(), name="general")
            if channel:
                await channel.send(new_year_message)
        # Wait for 1 hour before checking again
        await asyncio.sleep(3600)


async def main():
    flask_server = FlaskServer(bot, GUILD_ID, ROLE_ID, PREMIER_CHANNEL_ID)
    threading.Thread(target=flask_server.run).start()
    await bot.start(DISCORD_BOT_TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
