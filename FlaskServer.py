# FlaskServer to handle Ko-Fi Webhook
from flask import Flask, request, jsonify
import os
import discord

class FlaskServer:
    def __init__(self, bot, role_name='Donor', premier_channel_name="Premier"):
        self.app = Flask(__name__)
        self.bot = bot
        self.role_name = role_name      # Store role name
        self.premier_channel_name = premier_channel_name  # Channel name to look for/create
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/kofi-webhook', methods=['POST'])
        def kofi_webhook():
            data = request.json
            donor_name = data.get('from_name', 'Anonymous')
            amount = data.get('amount', '0')
            message = data.get('message', '')

            # Call the process_donation method
            self.bot.loop.create_task(
                self.process_donation(donor_name, amount, message))
            return jsonify({'status': 'success'}), 200

    async def process_donation(self, donor_name, amount, message):
        # Look for the member in all guilds the bot is part of
        for guild in self.bot.guilds:
            # Try to find a member with the given donor name
            member = discord.utils.get(guild.members, name=donor_name)  # Fetch the member using their name
            if member:
                # Find the role by name
                role = discord.utils.get(guild.roles, name=self.role_name)

                if role is None:
                    # Create the role if it doesn't exist
                    role = await guild.create_role(name=self.role_name, permissions=discord.Permissions(send_messages=True))

                if role not in member.roles:
                    await member.add_roles(role)
                    print(f"Assigned role to {member.name} in guild {guild.name}.")

                # Look for a channel with the specified name
                channel = discord.utils.get(guild.channels, name=self.premier_channel_name)
                # If the channel doesn't exist, create it
                if channel is None:
                    channel = await guild.create_text_channel(self.premier_channel_name)

                # Send the donation message to the channel
                await channel.send(f"🎉 **{donor_name}** just donated **${amount}** on Ko-Fi! {message}")
                return  # Exit after processing donation for the member

        print(f"Member with name {donor_name} not found in any guild.")

    def run(self):
        print("Starting Flask server...")
        self.app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))