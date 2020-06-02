import discord
import asyncio
import json

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
    while (client.is_closed):
        for guild in client.guilds:
            # get all the roles to prune for
            roles = guild.roles

            members_kicked = await guild.prune_members(days=DAYS, compute_prune_count=True, roles=roles,
                                                       reason=f"{DAYS} days of inactivity")

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
                    if channel == CHANNEL:
                        await channel.send(kick_message)
                        print(kick_message)
        # wait WAIT seconds before checking for inactive members again
        await asyncio.sleep(WAIT)


# when you type ".stop" the program ends
@client.event
async def on_message(message):
    if message.author.name != OWNER:
        return

    if (message.content.startswith('.stop')) and (message.channel == CHANNEL):
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
