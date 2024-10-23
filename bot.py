import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from pymongo import MongoClient
from flask import Flask, request, jsonify
import asyncio

load_dotenv()

# Environment Variables
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
PREMIER_CHANNEL_ID = int(os.getenv('PREMIER_CHANNEL_ID'))

# Logging setup
logging.basicConfig(level=logging.INFO)

# Discord bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Flask app to handle webhooks
app = Flask(__name__)

# MongoDB setup
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client["discord_bot"]
conversations_collection = db["conversations"]
quotes_collection = mongo_client['quotes_db']['quotes']

client = OpenAI()


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


@app.route('/kofi-webhook', methods=['POST'])
def kofi_webhook():
    data = request.json
    donor_name = data.get('from_name', 'Anonymous')
    amount = data.get('amount', '0')
    message = data.get('message', '')

    async def send_donation_alert():
        channel = bot.get_channel(PREMIER_CHANNEL_ID)
        if channel:
            await channel.send(f"🎉 **{donor_name}** just donated **${amount}** on Ko-fi! {message}")

    bot.loop.create_task(send_donation_alert())
    return jsonify({'status': 'success'}), 200


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        welcome_message = f"Welcome to the server, {member.mention}! 🎉 We're glad to have you here!"
        await channel.send(welcome_message)
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
    # Send a message with the bot's latency
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

        # Optionally, clear the ask mode
        # user_ask_mode[message.author.id] = False


async def main():
    async with bot:
        await bot.start(DISCORD_BOT_TOKEN)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
