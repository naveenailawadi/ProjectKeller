import discord
import asyncio
import json

# create constants with configuration file
with open('config.json', 'r') as config:
    # open the file
    information = json.load(config)

    # load the data into constants
    TOKEN = information['token']
    GAMES = information['games']

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
    old_activities = list(before.activities)
    new_activities = list(after.activities)

    # only keep going if there is an item in the list
    if len(old_activities) > 0:
        # get the game
        old_activity = old_activities[0]
    else:
        return

    if 'activity' == str(type(old_activity)).split('.')[-1][:-2].lower():
        old_game = old_activity.name
    else:
        return

    if old_game in GAMES:
        old_party = old_activity.party
        if len(old_party) > 0:
            print(f"Party: {old_party}")
    else:
        return


client.run(TOKEN)


'''
NOTES
- sample activity response:
(<Activity type=<ActivityType.playing: 0> name='Grand Theft Auto V' url=None details=None
application_id=356876176465199104 session_id=None emoji=None>,

<Activity type=<ActivityType.playing: 0> name='Destiny 2' url=None details=None
application_id=438122941302046720 session_id=None emoji=None>)
'''
