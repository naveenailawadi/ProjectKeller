import discord
from tokens import TOKEN, OWNER
import asyncio

# client object creation
client = discord.Client()

# continually checks for and kicks members that were inactive for 30 days


async def clean_server():
    await client.wait_until_ready()
    while (client.is_closed):
        for guild in client.guilds:
            members_kicked = await guild.prune_members(days=30, compute_prune_count=True, reason="30 days of inactivity")
            print(f'{members_kicked} members pruned')
        # wait 100 seconds before checking for inactive members again
        await asyncio.sleep(100)


# when you type ".stop" the program ends
@client.event
async def on_message(message):
    if message.author.name != OWNER:
        return

    if message.content.startswith('.stop'):
        await client.logout()

# lets you know that the bot is running


@client.event
async def on_ready():
    print("Bot is up and will contunually prune inactive users.")

# calls the background event that kicks inactive users
client.loop.create_task(clean_server())

# attempts to log in and catches errors
try:
    client.run(TOKEN)
except discord.DiscordException:
    print("Error: Failed to connect to discord. Check your token.")
