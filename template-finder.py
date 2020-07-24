import praw
import requests

r = praw.Reddit("Meme template finder bot by reddit-be0cool v 1.0.0"
                "Url: https://thatguydavid09.github.io/redirect/")


r.login()
already_done = []
while True:
    # TODO: implement the bot and the ai
    # Bot should activate if its name is called
    # Should take image, put it through api, and make a comment

    if bot_is_summoned:
        # Get image url
        resp = requests.get(url="The reddit posts url")

        url = resp.json['data']['children'][0]['data']['url']
