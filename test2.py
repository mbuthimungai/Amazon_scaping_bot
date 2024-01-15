import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
from dotenv import load_dotenv


intents = discord.Intents.default()
intents.members = True
intents.presences = True  # If you need Presence Intent
intents.message_content = True
# Load environment variables
load_dotenv()
TOKEN = os.getenv('MY_TOKEN')  # Replace with your Discord token

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Create an instance of APScheduler
scheduler = AsyncIOScheduler()

# A sample function to be scheduled
async def scheduled_task():
    print("This is a scheduled task running periodically.")

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

    # Schedule the task
    scheduler.add_job(scheduled_task, 'interval', minutes=1)  # Runs every 1 minute
    scheduler.start()

# Add a simple command for interaction
@bot.command(name='hello', help='Responds with a greeting')
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.name}!')

# Run the bot
bot.run(TOKEN)
