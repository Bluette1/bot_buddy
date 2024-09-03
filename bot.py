import discord

# Set up logging
import logging
logging.basicConfig(level=logging.INFO)

# Set up intents
intents = discord.Intents.default()
intents.message_content = True  # Enable additional intents as needed

# Initialize the client with intents
client = discord.Client(intents=intents)

# Event when the bot is ready
@client.event
async def on_ready():
  print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('!hello'):
    await message.channel.send('Hello!')

# Run the bot
client.run('MTI4MDEzMDk2MzY5NDk0ODM5NQ.GN6Cho.iT--kOo9AnUOgJ1rFf1WFuCaNERsEQ1eoHHJiw')
