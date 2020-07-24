import praw

r = praw.Reddit("Meme template finder bot by reddit-be0cool v 1.0.0"
                "Url: https://thatguydavid09.github.io/redirect/")


r.login()
already_done = []
while True:
    # TODO: implement the bot and the ai
    # Bot should activate if its name is called
    # Should take image, put it through api, and make a comment
