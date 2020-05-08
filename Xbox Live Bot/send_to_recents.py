from bots import RecentScraper, XBot
from tools import ConfigManager, RecordManager
from requests.exceptions import ReadTimeout
import json
import time

DATA_CSV = 'sent.csv'
FRIENDS_CSV = 'friends.csv'
CONFIG_FILE = 'config.json'

# create constants to login with --> use configuration file
with open(CONFIG_FILE, 'r') as config:
    # open the file
    information = json.load(config)

    # load the data into constants
    EMAIL = information['email']
    PASSWORD = information['password']
    X_AUTH_KEY = information['X-Auth']
    MAX_RECENTS = information['max_recents']
    MAX_MESSAGES = information['max_messages']
    MESSAGE = information['message']
    GAMES = information['games']
    BLOCK_START_TIME_UTC = information['block_start_time_utc']
    BLOCK_STOP_TIME_UTC = information['block_stop_time_utc']


# create necessary objects
scraper = RecentScraper(EMAIL, PASSWORD)
xbot = XBot(EMAIL, PASSWORD, X_AUTH_KEY)
config_manager = ConfigManager(CONFIG_FILE)
record_manager = RecordManager(DATA_CSV, FRIENDS_CSV)

# create the driver, scrape, close the driver
scraper.create_webdriver()
scraper.login()
scraper.enter_xbox_homepage()
recents = set(scraper.get_recents(MAX_RECENTS))
print(recents)
scraper.close_webdriver()

# get people that have already been sent a message
removables = record_manager.get_removables(BLOCK_START_TIME_UTC, BLOCK_STOP_TIME_UTC)

# extrapolate of the current recents to get more potential games that play specific games
recents = recents | xbot.extrapolate(recents, GAMES, MAX_MESSAGES)
print(recents)

# this will keep the bot to always (at least slightly) underperform the max messages
to_send = list(recents - removables)

# send the messages to the appropriate gamertags
sent_messages = []

for gamertag in to_send:
    try:
        xbot.send_message(gamertag, MESSAGE)
        sent_messages.append(gamertag)
        print(f"Message sent to {gamertag}")
    except ReadTimeout:
        # sleep extra to avoid getting banned
        time.sleep(30)
        pass
    time.sleep(10)


# add the sent data to the dataframe
send_time = time.time()
record_manager.add_records(sent_messages, MESSAGE)

# update the json to the current time
config_manager.update_key('block_stop_time_utc', send_time)


'''
NOTES
- make a way to update the stop time to the current time
- create a tools file for creating classes to manage files easily
'''
