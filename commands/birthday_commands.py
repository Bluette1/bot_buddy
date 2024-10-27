from discord.ext import commands, tasks
from datetime import datetime
import discord
from repositories.birthday_repository import Birthday

class BirthdayCommands(commands.Cog):
    def __init__(self, bot, birthday_repo):
        self.bot = bot
        self.birthday_repo = birthday_repo
        self.check_birthdays.start()

    # Your commands here...

    @commands.command(name='setbirthday')
    async def set_birthday(self, ctx, birthday_date: str):
        """Set your birthday using the format YYYY-MM-DD"""
        try:
            # Validate date format
            datetime.strptime(birthday_date, '%Y-%m-%d')
            
            # Create and save birthday
            birthday = Birthday(ctx.author.id, birthday_date)
            await self.birthday_repo.save_birthday(birthday)
            
            await ctx.send(f'Birthday saved successfully! I will remember to wish you on {birthday_date}')
        
        except ValueError:
            await ctx.send('Invalid date format. Please use YYYY-MM-DD (e.g., 2024-12-31)')
        except Exception as e:
            await ctx.send(f'An error occurred: {str(e)}')


    @commands.command(name='getbirthday')
    async def get_birthday(self, ctx):
        """Get your saved birthday"""
        try:
            birthday = await self.birthday_repo.get_birthday(ctx.author.id)
            if birthday:
                await ctx.send(f'Your birthday is set to: {birthday.birthday}')
            else:
                await ctx.send('You haven\'t set your birthday yet. Use !setbirthday YYYY-MM-DD')
        except Exception as e:
            await ctx.send(f'An error occurred: {str(e)}')

    
    @commands.command(name='upcoming_birthdays')
    async def upcoming_birthdays(self, ctx, days: int = 7):
        """Show birthdays coming up in the next X days"""
        try:
            all_birthdays = await self.birthday_repo.get_all_birthdays()
            today = datetime.now()
            upcoming = []
            
            for birthday in all_birthdays:
                bday = datetime.strptime(birthday.birthday, '%Y-%m-%d')
                # Set year to current year for comparison
                bday = bday.replace(year=today.year)
                
                # If birthday has passed this year, check next year
                if bday < today:
                    bday = bday.replace(year=today.year + 1)
                
                days_until = (bday - today).days
                
                if 0 <= days_until <= days:
                    user = await self.bot.fetch_user(birthday.user_id)
                    upcoming.append((user.name, bday.strftime('%B %d'), days_until))
            
            if upcoming:
                message = "**Upcoming Birthdays:**\n"
                for name, date, days_left in sorted(upcoming, key=lambda x: x[2]):
                    message += f"• {name} - {date} (in {days_left} days)\n"
            else:
                message = f"No birthdays in the next {days} days!"
                
            await ctx.send(message)
            
        except Exception as e:
            await ctx.send(f'An error occurred: {str(e)}')


    @commands.command(name='birthday_stats')
    async def birthday_stats(self, ctx):
        """Show birthday statistics for the server"""
        try:
            all_birthdays = await self.birthday_repo.get_all_birthdays()
            total_birthdays = len(all_birthdays)
            
            if total_birthdays == 0:
                await ctx.send("No birthdays have been set yet!")
                return
                
            # Count birthdays by month
            month_counts = {}
            for birthday in all_birthdays:
                month = datetime.strptime(birthday.birthday, '%Y-%m-%d').strftime('%B')
                month_counts[month] = month_counts.get(month, 0) + 1
                
            # Format statistics
            stats = "**Birthday Statistics**\n"
            stats += f"Total birthdays registered: {total_birthdays}\n\n"
            stats += "Birthdays by month:\n"
            for month in sorted(month_counts.keys()):
                count = month_counts[month]
                bar = "█" * (count * 2)  # Simple visualization
                stats += f"{month}: {bar} ({count})\n"
                
            await ctx.send(stats)
            
        except Exception as e:
            await ctx.send(f'An error occurred: {str(e)}')

    @commands.command(name='remove_birthday')
    async def remove_birthday(self, ctx):
        """Remove your birthday from the database"""
        try:
            await self.birthday_repo.remove_birthday(ctx.author.id)
            await ctx.send("Your birthday has been removed from the database.")
        except Exception as e:
            await ctx.send(f'An error occurred: {str(e)}')    

    @tasks.loop(hours=24)
    async def check_birthdays(self):
        """Check for birthdays daily"""
        today = datetime.now().strftime('%m-%d')
    
        try:
            birthdays = await self.birthday_repo.get_all_birthdays()

            birthday_messages = [
                "🎉 Happy Birthday {}! Have a wonderful day! 🎂",
                "🎈 Wishing you a fantastic birthday, {}! 🎊",
                "🎂 Hope your day is filled with joy and celebration, {}! 🎉",
                "✨ Another year of awesome memories! Happy Birthday, {}! 🎁",
                "🌟 May your special day be filled with happiness, {}! 🎈"
            ]

            for birthday in birthdays:
                birthday_month_day = datetime.strptime(birthday.birthday, '%Y-%m-%d').strftime('%m-%d')
                
                if birthday_month_day == today:
                    user = await self.bot.fetch_user(birthday.user_id)
                    message = birthday_messages[hash(str(birthday.user_id)) % len(birthday_messages)]
                    try:
                        await user.send(message.format(user.name))
                    except discord.errors.Forbidden:
                        print(f"Couldn't send birthday message to {user.name}")

        except Exception as e:
            print(f"Error in check_birthdays: {str(e)}")


    def cog_unload(self):
        self.check_birthdays.cancel()