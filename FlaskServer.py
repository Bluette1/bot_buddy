
from flask import Flask, request, jsonify
import os
import discord


class FlaskServer:
    def __init__(self, bot, guild_id, role_id, premier_channel_id):
        self.app = Flask(__name__)
        self.bot = bot
        self.guild_id = guild_id
        self.role_id = role_id
        self.premier_channel_id = premier_channel_id
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
        guild = self.bot.get_guild(self.guild_id)
        member = discord.utils.find(
            lambda m: m.name == donor_name, guild.members)

        if member:
            role = discord.utils.get(guild.roles, name="Donor")

            if role is None:
                # Create the role if it doesn't exist
                role = await guild.create_role(name="Donor", permissions=discord.Permissions(send_messages=True))
            if role not in member.roles:
                await member.add_roles(role)
                print(f"Assigned role to {member.name}")

        channel = self.bot.get_channel(self.premier_channel_id)
        if channel:
            await channel.send(f"🎉 **{donor_name}** just donated **${amount}** on Ko-Fi! {message}")

    def run(self):
        print("Starting Flask server...")
        self.app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
