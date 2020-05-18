import discord
import asyncio
import json

# create constants with configuration file
with open('config.json', 'r') as config:
    # open the file
    information = json.load(config)

    # load the data into constants
    TOKEN = information['token']

# create the bot
client = discord.Client()

# create some initial output


@client.event
async def on_ready():
    print('Readying up')
    for guild in client.guilds:
        print(f"Guild: {guild}")


# create an event for when people join games
@client.event
async def on_member_update(before, after):
    print('Member updated.')
    old_activities = before.activities
    new_activities = after.activities


client.run(TOKEN)
