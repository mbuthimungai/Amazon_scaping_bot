from .sendMessages import menu, on_ready, asin_isbn, getdataByLink, productReview, getdataByASIN, getDataByAsinSearch
import discord
import os
import re
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from pytz import utc

scheduler = AsyncIOScheduler(timezone="utc")

load_dotenv()
Token = os.getenv('MY_TOKEN')
intents = discord.Intents.default()
intents.members = True
intents.presences = True  # If you need Presence Intent
intents.message_content = True
client = discord.Client(intents = intents)


def run_discord_bot():
    """
    Function to run the Discord bot. Registers the event handlers.
    """
    # Event handler for when the bot ready:
   
           
    @client.event
    async def on_ready():
        """
        This function prints a message when the bot is ready to use.
        """
        scheduler.start()
        print(f"Buddy is now running.")
    # Event handler for when a message is received
    @client.event
    async def on_message(message):
        # Ignore messages ent by the bot itself:
        if message.author == client.user:
            return
        # Extract the username, user message, and channel from the message.
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)   
        
        print(f'{username} said: {user_message} {channel}.')
        # Define regular expressions to match the message:
        regex_pattern = r"""^hi|hello|hey|yo"""
        amazon_pattern = r'^!asin (https?://)?(www\.)?amazon\.(com|in|co\.uk|fr|com\.mx|com\.br|com\.au|co\.jp|se|de|it|com\.be)/.+'
        review_pattern = r"""^!rev https:\/\/www\.amazon\.(com|in|co\.uk|fr|com\.mx|com\.br|com\.au|co\.jp|se|de|it|com\.be)\/[^\s]+$"""
        info_pattern = r"""^!info https:\/\/www\.amazon\.(com|in|co\.uk|fr|com\.mx|com\.br|com\.au|co\.jp|se|de|it|com\.be)\/[^\s]+$"""
        asin_pattern = r"""^!info-asin \b[A-Z0-9]{10}\b"""
        search_channel_pattern = r"""^!search\s+https:\/\/www\.amazon\.(com|in|co\.uk|fr|com\.mx|com\.br|com\.au|co\.jp|se|de|it|com\.be)\/[^\s]+\s+!channel\s+\S+$"""
        
        # If the message is a greeting and is sent in a direct message:
        if message.guild is None and re.match(regex_pattern, message.content, re.IGNORECASE):
            await message.author.send(f"Hey {username}. Type '!general' or '!help' to know the overview of bot.")
        # If the message is !general and is sent in a direct message:
        elif message.content == '!commands' and message.guild is None:
            await menu(message.content, message.author)
        elif (message.content == '!general' or message.content == '!help') and message.guild is None:
            await menu(message.content, message.author)
        elif message.content == '!about' and message.guild is None:
            await menu(message.content, message.author)
        elif message.content == '!ping' and message.guild is None:
            await menu(message.content, message.author, client)
        elif message.content == '!status' and message.guild is None:
            await menu(message.content, message.author)
        # If the message is an Amazon ASIN and is sent in a direct message
        elif message.guild is None and re.search(asin_pattern, user_message):
            asin = user_message.split()[-1]
            await message.author.send(f"Please wait. Fetching data from Amazon.")
            await getdataByASIN(asin, message.author)            
        # If the message is an Amazon product link and is sent in a direct message:
        elif message.guild is None and re.search(amazon_pattern, user_message):
            url = user_message.split()[-1]
            await asin_isbn(url, message.author)
        # IF the message is an ASIN/ISBN and is sent in a direct message:
        elif message.guild is None and re.search(info_pattern, user_message):
            url = user_message.split()[-1]
            await message.author.send(f"Please wait. Fetching data from Amazon.")
            await getdataByLink(url, message.author)
        elif message.guild is None and (re.match(review_pattern, message.content)):
            url = user_message.split()[-1]
            await message.author.send(f"Please wait. Fetching reviews.")
            await productReview(url, message.author)
        else:  
            print(f'Message from {username} in guild channel {channel}: {user_message}')
            if message.guild and re.search(search_channel_pattern, user_message):
                search_channel = user_message.split()
                search_msg = search_channel[1]
                channel_name = search_channel[-1]                
                # Ensure the member has permissions to create a channel
                if message.author.guild_permissions.manage_channels:
                    channel = discord.utils.get(message.guild.channels, name=channel_name)                                                            
                    if channel:
                        await channel.send(f"Hello {channel}")                        
                    else:
                        await message.guild.create_text_channel(name=channel_name)
                        await message.channel.send(f'Channel "{channel_name}" created.')
                        channel = discord.utils.get(message.guild.channels, name=channel_name)                                                            
                    await getDataByAsinSearch(scheduler, search_msg, channel)
                    
                else:
                    await message.channel.send("You don't have permissions to create channels.")                
            
            elif message.guild and re.search(regex_pattern, user_message):
                await message.channel.send(f"Hey {username.title()}. Type '!general' or '!help' to know the overview of bot.")
            # If the message is !general and is sent in a direct message:
            elif message.content == '!commands':                
                await menu(message.content, message.channel)
            elif message.content == '!general' or message.content == '!help':
                await menu(message.content, message.channel)
            elif message.content == '!about':
                await menu(message.content, message.channel)
            elif message.content == '!ping':
                await menu(message.content, message.channel, client)
            elif message.content == '!status':
                await menu(message.content, message.channel)
            elif message.guild and re.search(asin_pattern, user_message):
                asin = user_message.split()[-1]
                await message.channel.send(f"Please wait. Fetching data from Amazon.")
                await getdataByASIN(asin, message.channel)            
            elif message.guild and re.search(amazon_pattern, user_message):
                url = user_message.split()[-1]
                await asin_isbn(url, message.channel)
            elif message.guild and re.search(info_pattern, user_message):
                url = user_message.split()[-1]
                await message.channel.send(f"Please wait. Fetching data from Amazon.")
                await getdataByLink(url, message.channel)
            elif message.guild and (re.match(review_pattern, message.content)):
                url = user_message.split()[-1]
                await message.channel.send(f"Please wait. Fetching reviews.")
                await productReview(url, message.channel)
            else:
                await message.channel.send(f"Invalid command. Type '!general | !help' or '!commands' to know the purpose of the bot.")
    
    # Start the scheduler
    
    # Run the client with the TOKEN:
    client.run(Token)

