# TODO This bot needs to be recoded to use transfer-ai

import csv
import os
import shutil
import time

# This is a reddit bot that, when it is called by commenting its username,
# uses ai to figure out what template the meme above it is
import praw
import requests

# authenticate bot
reddit = praw.Reddit(client_id="XXXXXXXXXX",
                     client_secret="XXXXXXXXXXXXXX",
                     refresh_token="XXXXXXXXXXXXXXXXXXXXX",
                     user_agent="Meme finder by /u/TemplateFinderBot")

image_class = "_2_tDEnGMLxpM6uOa2kaDB3"

reddit.read_only = False


# This function takes the post from the comment it is passed, figures out if it's a photo or not, if it is, it runs the ai on it and returns
# Its confidence and class number.
# It also returns success codes:
# Code 0: All ok, proceed with comment formatting, returned in list with format [0, photo_class, confidence (scale 0-100)]
# Code 1: It cannot identify the class of the photo, returned in list with format[1]
# Code 2: The post is not a photo, returned in list with format [3]
# Code 3: The provided comment is not a top level comment
# Code 4: HTTP error, returned in list with format [4, status_code, message]


def get_class(comment_look):
    """
    Gets the class of a comment
    :param comment_look: praw Comment
    :return: See above
    """
    bad_gateway = True
    directory = r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Code\Reddit bot"
    image_formats = (".png", ".jpeg", ".jpg")

    api_url = "https://api.reddit.com/api/info/?id="

    if comment_look.parent_id[:3] == "t3_":
        id_to_get = comment_look.parent_id
    else:
        return [3]

    # This literally just loops the code if reddit has a bad gateway error, yes it happens that often
    while bad_gateway:
        # Sending the api request
        url_to_send = api_url + id_to_get
        # If it starts spitting out random HTTP errors, try to update this
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
        f = requests.get(url_to_send, headers=headers)
        if f.status_code >= 500:
            print("Reddits servers are being stupid again. There is no expection, just Reddit being Reddit.")
            print("We'll wait for 5 seconds and then try again.")
            time.sleep(5)
            bad_gateway = True
            continue
        elif f.status_code != 200 and f.status_code < 500:
            return [4, f.status_code, f.json()["message"]]
        else:
            parsed_json = f.json()
            # print(parsed_json)

            # Figure out if it is an image post by looking at its headers
            img_url = parsed_json["data"]["children"][0]["data"]["url"]
            print(img_url)

            # If it is an image, save it to the disk
            #                                          This check here is if the extension is 4 letters long, like jpeg
            if img_url[-4:] in image_formats or img_url[-5:] in image_formats:
                img_response = requests.get(img_url, stream=True)
                with open("img.png", "wb") as out_file:
                    shutil.copyfileobj(img_response.raw, out_file)
                del img_url
            else:
                return [2]
            bad_gateway = False

        # This just waits until the photo can process
        time.sleep(3)
        # Get the image

        # Delete the image
        os.remove("img.png")


replied_to = []
# Initialize replied_to from a csv file
with open("replied_to.csv", "r") as file:
    lines = file.readlines()

for line in lines:
    replied_to.append(line.replace("\n", ""))

print(lines)
print(replied_to)

# Loop through mentions
print(reddit.inbox.mentions(limit=10))
for comment in reddit.inbox.mentions(limit=10):
    # If its name is commented and it hasn't replied to the comment, reply to it and append the list to replied_to and a csv file
    if comment.id not in replied_to:
        replied_to.append(comment.id)

        with open("replied_to.csv", "a+", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([comment.id])

        print(f"Replied to {comment.id}")
        class_of_photo = get_class(comment)
        print(class_of_photo)
        comment.reply(class_of_photo)
