# TODO implement method for approving a subreddit, by being asked to be moderator, also make config file
# This is a reddit bot that, when it is called by commenting its username,
# uses ai to figure out what template the meme above it is

import csv
import os
import shutil
import time

import praw
import requests

import ai_related_scripts.image_ai as ai

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
# Code 0: All ok, proceed with comment formatting, returned in list with format [0, confidence (0-1000), photo_class, imgur_link, extra_info(if present)]
# Code 1: It cannot identify the class of the photo, returned in list with format[1]
# Code 2: The post is not a photo, returned in list with format [2]
# Code 3: The provided comment is not a top level comment, returned in format [3]
# Code 4: HTTP error, returned in list with format [4, status_code, message]
# Code 5, General error, returned with format [5, Exception]

def get_class(comment_look):
    """
    Gets the class of a comment
    :param comment_look: praw Comment
    :return: See above
    """
    # This try is to catch any and all errors that may occur
    try:
        # Set variables
        bad_gateway = True
        directory = r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Code\Reddit bot\Templates"
        image_formats = (".png", ".jpeg", ".jpg")

        api_url = "https://api.reddit.com/api/info/?id="

        # Top level comment check
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
            # This is if reddit is dumb
            if f.status_code >= 500:
                print(
                    "\033[0;33;40m [REDDIT DUMB] Reddit's servers are being stupid again. There is no exception, just Reddit being Reddit.")
                print("\033[0;33;40m [REDDIT DUMB] We'll wait for 5 seconds and then try again.")
                time.sleep(5)
                bad_gateway = True
                continue
            # If there is a normal http error
            elif f.status_code != 200 and f.status_code < 500:
                return [4, f.status_code, f.json()["message"]]
            # If everything is ok
            else:
                parsed_json = f.json()
                # print(parsed_json)

                # Figure out if it is an image post by looking at its headers
                img_url = parsed_json["data"]["children"][0]["data"]["url"]

                # print(img_url)

                # If it is an image, save it to the disk
                meme = ""

                if img_url[-4:] in image_formats:
                    img_response = requests.get(img_url, stream=True)

                    with open(f"img.{img_url[-4:]}", "wb") as out_file:
                        shutil.copyfileobj(img_response.raw, out_file)

                    meme = f"img.{img_url[-4:]}"
                    del img_url
                elif img_url[-5:] in image_formats:
                    img_response = requests.get(img_url, stream=True)

                    with open(f"img.{img_url[-5:]}", "wb") as out_file:
                        shutil.copyfileobj(img_response.raw, out_file)

                    meme = f"img.{img_url[-5:]}"
                    del img_url
                else:
                    return [2]
                bad_gateway = False

                # Loop through every template until a greater than 50 percent confidence
                for filename in os.listdir(directory):
                    if not file.endswith(".csv"):

                        template = os.path.join(directory, filename)
                        confidence = ai.check_match(template, meme)
                        # If there isn't an error
                        if confidence[0] == 0 and confidence[1] >= 50.0:
                            with open(r"Templates\templates.csv") as csv_file:
                                csv_reader = csv.reader(csv_file, delimeter=",")

                                for row in csv_reader:
                                    # Find the right things to return
                                    if row["file_name"] == template and row["extra_info"] is not None:
                                        return [0, confidence[1], row["class_name"], row["imgur_link"]]
                                    else:
                                        return [0, confidence[1], row["class_name"], row["imgur_link"],
                                                row["extra_info"]]
                        else:
                            # If there is an error
                            print("[ERROR] " + confidence[1])
                            return [5, confidence[1]]

                    # Class not found
                    return [1]

                # Delete the image
                os.remove(meme)
    except Exception as e:
        return [5, e]


approved_subs = ["TemplateFinderBott"]
replied_to = []
# Initialize replied_to from a csv file
with open("replied_to.csv", "r") as file:
    lines = file.readlines()

for line in lines:
    replied_to.append(line.replace("\n", ""))

# print(lines)
# print(replied_to)

# Loop through mentions
# print(reddit.inbox.mentions(limit=10))

while True:
    for comment in reddit.inbox.mentions(limit=10):
        # If its name is commented and it hasn't replied to the comment, reply to it and append the list to replied_to and a csv file
        if comment.id not in replied_to and comment.subreddit in approved_subs:
            replied_to.append(comment.id)

            with open("replied_to.csv", "a+", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([comment.id])

            reply = ""
            match_result = get_class(comment)
            # Set reply variable

            # If the function says to proceed
            if match_result[0] == 0:
                # If there isn't any extra info
                if len(match_result) == 3:
                    reply = f"""
                            I am {round(match_result[1])}% sure that this uses the {match_result[2]} template.
                            It can be found [here]({match_result[2]}).
                            [False positive?](https://www.reddit.com/message/compose/?to=TemplateFinderBot&subject=FALSE POSITIVE&message={{/"post_id/": /"{comment.parent_id}/", /"correct_meme/": /"PUT THE LINK TO THE CORRECT MEME HERE/"}})
                            """
                # If there is
                else:
                    reply = f"""
                            I am {round(match_result[1])}% sure that this uses the {match_result[2]} template.
                            It can be found [here]({match_result[2]}).
                            Some extra info: {match_result[3]}
                            [False positive?](https://www.reddit.com/message/compose/?to=TemplateFinderBot&subject=FALSE POSITIVE&message={{/"post_id/": /"{comment.parent_id}/", /"correct_meme/": /"PUT THE LINK TO THE CORRECT MEME HERE/"}})
                            """
            # If the class cannot be identified
            elif match_result[0] == 1:
                reply = f"""
                        Sadly, I don't know what template this meme is using.
                        [Want to include this in future searches?](https://www.reddit.com/message/compose/?to=TemplateFinderBot&subject=REQUEST&message={{/"post_id/": /"{comment.parent_id}/"}})
                        """
            # If it's not a photo
            elif match_result[0] == 2:
                print(f"\033[0;33;40m [WARNING] Not photo, {comment.parent_id}")
                reply = "That's not a photo!"
            # If it isn't a top level comment
            elif match_result[0] == 3:
                print(f"\033[0;33;40m [WARNING] Not top level comment, {comment.parent_id}")
            # If there is an http error
            elif match_result[0] == 4:
                print(f"\033[0;31;40m [ERROR] HTTP error, status code: {match_result[1]}, message: {match_result[2]}")
            # If there is a general error
            else:
                print(f"\033[0;31;40m [ERROR] General error, {match_result[1]}")

            # Replay to the comment and print some debug
            comment.reply(reply)
            print(f"\033[0;32;40m [REPLY] Replied to {comment.id} in {comment.subreddit}")
            print(f"[REPLY] Replied: {reply}")
