import discord
from discord.errors import NotFound, Forbidden
import asyncio
import json
import datetime
import time

# create constants with configuration file
with open('config.json', 'r') as config:
    # open the file
    information = json.load(config)

    # load the data into constants
    TOKEN = information['token']
    OWNER = information['username']
    DAYS = information['days_inactive']
    WAIT = information['wait_time']
    MESSAGE = information['send_message']
    CHANNEL = information['channel']

# client object creation
client = discord.Client()


# continually checks for and kicks members that were inactive for 30 days
async def clean_server():
    await client.wait_until_ready()

    # setting time objects
    current = datetime.datetime.now()
    comparable = datetime.timedelta(days=DAYS)

    while (client.is_closed):
        start = time.time()
        for guild in client.guilds:
            members_kicked = 0

            users_with_msg = []

            # creating a list of users who recently sent messages
            for channel in guild.text_channels:
                try:
                    async for message in channel.history(limit=100000):
                        if((current - message.created_at) < comparable):
                            if (not(message.author in users_with_msg)):
                                users_with_msg.append(message.author)
                except NotFound:
                    print(f"Could not find channel: {str(channel)}")

            # checking each member individually
            for member in guild.members:
                # checking if they joined recently
                join_recently = ((current - member.joined_at) < comparable)

                # checking if they recently sent messages
                recent_message = False
                if member in users_with_msg:
                    recent_message = True

                # kicks and counts if user didnt send a message recently and didnt join recently
                if(not(recent_message or join_recently)):
                    # await guild.kick(member, reason=f"{DAYS} days of inactivity.")
                    print(f"Kicking {member}")
                    members_kicked = members_kicked + 1

            # send message if users are kicked and if client specifies
            if (MESSAGE and members_kicked):
                # plural in message
                if (members_kicked == 1):
                    kick_message = (
                        f'{members_kicked} member pruned for {DAYS} days of inactivity')
                else:
                    kick_message = (
                        f'{members_kicked} members pruned for {DAYS} days of inactivity')

                # send message to correct channel
                for channel in guild.text_channels:
                    if str(channel) == CHANNEL:
                        await channel.send(kick_message)
                        print(kick_message)

        end = time.time()
        # wait WAIT seconds before checking for inactive members again
        adjusted_wait = int(WAIT - (end - start))
        if adjusted_wait < 0:
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(adjusted_wait)


# when you type ".stop" the program ends
@client.event
async def on_message(message):
    if message.author.name != OWNER:
        return

    if (message.content.startswith('.stop')) and (str(message.channel) == CHANNEL):
        await client.logout()


# lets you know that the bot is running
@client.event
async def on_ready():
    for guild in client.guilds:
        print(f"Guild: {guild}")
        for channel in guild.text_channels:
            if str(channel).lower() in CHANNEL.lower():
                print(f"Channel found. Bot running in {channel}.")
                await channel.send("Bot is up and will contunually prune inactive users.")

# calls the background event that kicks inactive users
client.loop.create_task(clean_server())

# attempts to log in and catches errors
try:
    client.run(TOKEN)
except discord.DiscordException:
    print("Error: Failed to connect to discord. Check your token.")


'''
NOTES
- run in a tmux session perpetually
'''
