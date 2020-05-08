from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from xbox.webapi.api.client import XboxLiveClient
from xbox.webapi.authentication.manager import AuthenticationManager
from xbox.webapi.api.provider.profile import ProfileProvider
from xbox.webapi.api.provider.people import PeopleProvider
from tools import ListManager
from xboxapi.client import Client
from random import shuffle
import requests
import time
import json

LOGIN = 'https://login.live.com/login.srf'
XBOX_SITE = 'https://account.xbox.com/en-US/social?xr=shellnav'
XBOX_HOME = 'https://www.xbox.com/en-US/'
MESSAGING_URL = 'https://account.xbox.com/en-us/SkypeMessages'


class RecentScraper:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    # function to open the driver
    def create_webdriver(self):
        # open a webdriver
        self.driver = webdriver.Firefox()
        time.sleep(2)

    # create a function login
    def login(self):
        # go to the login page
        self.driver.get(LOGIN)
        time.sleep(2)

        # send the email to the input box
        email_box = self.driver.find_element_by_xpath('//input[@type="email"]')
        email_box.send_keys(self.email)

        # click next
        next_button = self.driver.find_element_by_xpath('//input[@type="submit"]')
        next_button.click()
        time.sleep(2)

        # enter the password
        password_box = self.driver.find_element_by_xpath('//input[@type="password"]')
        password_box.send_keys(self.password)

        # click sign in
        sign_in_button = self.driver.find_element_by_xpath('//input[@type="submit"]')
        sign_in_button.click()
        time.sleep(2)

    def enter_xbox_homepage(self):
        self.driver.get(XBOX_SITE)
        time.sleep(5)

        # more code could go here in the future if it is necessary to navigate the xbox home page manually

    def get_recents(self, max_recents):
        # click recent friends tab
        friends_tab = self.driver.find_element_by_xpath('//a[@class="c-glyph glyph-people"]')
        friends_tab.click()
        time.sleep(2)

        # get recent friends by changing the tab
        friend_type_button = self.driver.find_element_by_xpath('//button[@class="c-action-trigger"]')
        friend_type_button.click()
        time.sleep(1)
        recent_players_button = self.driver.find_element_by_xpath('//button[@id="RecentPlayers"]')
        recent_players_button.click()
        time.sleep(5)  # a lot of sleep is required here as it could potentially lag

        # get the recents
        recents_raw = self.driver.find_elements_by_xpath('//ul//span[@class="name"]')[:max_recents + 1]
        recents = [tag.text for tag in recents_raw]

        return recents

    def send_message(self, gamertag, message):
        # click the correct account
        try:
            account = self.driver.find_element_by_xpath(f'//strong[@class="topic"][text()="{gamertag}"]')
        except NoSuchElementException:
            print(f"Unable to send message to {gamertag} (account not found)")
            return False
        account.click()
        time.sleep(3)

        # send the message to the message bar
        message_bar = self.driver.find_element_by_xpath('//input[@id="newmessageinput"]')
        message_bar.send_keys(message)

        # click send
        send_button = self.driver.find_element_by_xpath('//button[@id="newmessage"]')
        send_button.click()
        time.sleep(1)

        print(f"Message sent to {gamertag}")
        return True

    def send_messages(self, gamertags, message):
        # navigate to the xbox home
        self.driver.get(MESSAGING_URL)
        time.sleep(5)

        # for testing only
        gamertags = ['LaxShaan04']

        messaged_gamers = []

        for gamer in gamertags:
            sent = self.send_message(gamer, message)
            if sent:
                messaged_gamers.append(gamer)

        return messaged_gamers

    def scrape_and_send(self, max_recents, message):
        self.create_webdriver()

        self.login()

        self.enter_xbox_homepage()

        recents = self.get_recents(max_recents)

        messaged_gamers = self.send_messages(recents, message)

        self.close_webdriver()

        return messaged_gamers

    def close_webdriver(self):
        self.driver.close()


# this class will work when microsoft fixes this endpoint
class MicrosoftBot:
    def __init__(self, email, password):
        self.auth_mgr = AuthenticationManager()

        # set data for auth manager
        self.auth_mgr.email_address = email
        self.auth_mgr.password = password

        # authentication
        self.auth_mgr.authenticate(do_refresh=True)

        # set the new info to a xbl client
        self.xbl_client = XboxLiveClient(
            self.auth_mgr.userinfo.userhash, self.auth_mgr.xsts_token.jwt, self.auth_mgr.userinfo.xuid)
        self.profile_provider = ProfileProvider(self.xbl_client)  # not currently used but could be useful later
        self.people_provider = PeopleProvider(self.xbl_client)

    # sends message to list of multiple users
    def send_message(self, message, users):
        response = self.xbl_client.message.send_message(message, gamertags=users)

        return response

    # create a function that gets xuids
    def get_xuid(self, gamertag):
        profile = self.profile_provider.get_profile_by_gamertag(gamertag).json()
        try:
            xuid = profile['profileUsers'][0]['id']
        except KeyError:
            # this means the gamertag wasn't found
            return

        return xuid

    # create a function to convert xuids back to gamertags
    def get_gamertag(self, xuid):
        profile = self.profile_provider.get_profile_by_xuid(xuid).json()
        settings = profile['profileUsers'][0]['settings']
        info_dict = {pair['id']: pair['value'] for pair in settings}
        gamertag = info_dict['Gamertag']

        return gamertag

    # create a method to get the user's friends (use xuids to save time and maximize integration)
    def get_friends(self, gamertag):
        xuid = self.get_xuid(gamertag)
        response_json = self.people_provider.get_friends_by_xuid(xuid).json()

        try:
            friends_raw = response_json['people']
        except KeyError:
            print(f"{gamertag} is a certified loner")
            friends_raw = []
            # this often means that the api is blocking us
            time.sleep(61)

        xuids = {info['xuid'] for info in friends_raw}

        return xuids


# create a class that uses the third party API to send messages
class XBot(MicrosoftBot):
    def __init__(self, email, password, x_auth_key):
        self.x_auth_key = x_auth_key
        self.url = 'http://xapi.us/v2'
        self.client = Client(api_key=x_auth_key)

        # use the microsoft api to get the xuid info without using requests
        self.auth_mgr = AuthenticationManager()

        # set data for auth manager
        self.auth_mgr.email_address = email
        self.auth_mgr.password = password

        # authentication
        self.auth_mgr.authenticate(do_refresh=True)

        # set the new info to a xbl client
        self.xbl_client = XboxLiveClient(
            self.auth_mgr.userinfo.userhash, self.auth_mgr.xsts_token.jwt, self.auth_mgr.userinfo.xuid)
        self.profile_provider = ProfileProvider(self.xbl_client)
        self.people_provider = PeopleProvider(self.xbl_client)

    # must have a method here to get the recent activity of a user
    def get_games(self, gamertag):
        # this takes more time but saves api requests
        xuid = self.get_xuid(gamertag)
        gamer = self.client.gamer(gamertag=gamertag, xuid=xuid)

        titles = gamer.get('xboxonegames')['titles']

        games = [title['name'] for title in titles]

        return games

    def send_messages_url(self, gamertags, message):
        endpoint = f"{self.url}/messages"
        headers = {
            'X-Auth': self.x_auth_key,
            'Content-Type': 'application/json'
        }

        # convert the gamertags to xuids
        xuids = [self.get_xuid(gamertag) for gamertag in gamertags]

        body = {
            "to": xuids,
            "message": message
        }

        response = requests.post(url=endpoint, data=body, headers=headers)

        return response

    def send_message(self, gamertag, message):
        # create a game object
        xuid = self.get_xuid(gamertag)
        gamer = self.client.gamer(gamertag, xuid)

        # send the message
        gamer.send_message(message)

    # create a method that extrapolates on a set of gamers and adds to it
    # games --> particular games the gamer has to play to be added to the set
    def extrapolate(self, gamertags, games, max_messages):
        candidates = set()
        list_manager = ListManager(games)

        for gamer in gamertags:
            # find the frients and games --> build with a dict builder
            friends = self.get_friends(gamer)

            # use a set operator to add the friends
            candidates = candidates | friends
            time.sleep(2)

        # randomize the candidates to increase spread
        candidates = list(candidates)
        print(candidates)
        shuffle(candidates)

        # find overlapping games --> add to gamertags if it the gamer matches one of the games
        for gamer in candidates:
            gamertag = self.get_gamertag(gamer)
            print(f"found {gamertag}")

            # this protexts against getting nonetype errrors
            if not gamertag:
                continue
            elif not gamer:
                continue

            print(f"Checking what games {gamertag} plays")
            games = list(set(self.get_games(gamertag)))

            # check if any of the games are in the the list of games --> the list manager return
            if list_manager.find_any_overlap(games):
                gamertags.add(gamertag)
                print(f"Added {gamertag} from friends")

            # check if the gamertags has reached its max
            if len(gamertags) >= max_messages:
                break

            # sleep to avoid throttling
            time.sleep(5)

        # return the gamertags
        return gamertags


if __name__ == '__main__':
    # run some test stuff
    with open('config.json', 'r') as config:
        # open the file
        information = json.load(config)

        # load the data into constants
        EMAIL = information['email']
        PASSWORD = information['password']
        X_AUTH_KEY = information['X-Auth']
        MAX_RECENTS = information['max_recents']
        MESSAGE = information['message']
        BLOCK_START_TIME_UTC = information['block_start_time_utc']
        BLOCK_STOP_TIME_UTC = information['block_stop_time_utc']

    # initialize the extrapolator
    bot = XBot(EMAIL, PASSWORD, X_AUTH_KEY)

    # get the friends
    # friends = bot.get_friend_xuids('NJS26104')
    friends = bot.get_friends('NJS26104')
