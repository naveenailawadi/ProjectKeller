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

    try:
        # get the game
        old_game = old_activities.Activity
        new_game = new_activities.Activity

        print(f"old game: {old_game}")
        print(f"new game: {new_game}")

        # if the activity is different, get the
    except AttributeError:
        print(f'No new activity found. Instead found {old_activities}')


client.run(TOKEN)


'''
NOTES
- sample activity response:
(<Activity type=<ActivityType.playing: 0> name='Grand Theft Auto V' url=None details=None
application_id=356876176465199104 session_id=None emoji=None>,

<Activity type=<ActivityType.playing: 0> name='Destiny 2' url=None details=None
application_id=438122941302046720 session_id=None emoji=None>)
'''
