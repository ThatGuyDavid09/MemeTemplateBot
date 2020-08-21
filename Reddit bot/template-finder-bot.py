# TODO implement method for approving a subreddit, by being asked to be moderator, probs later
# This is a reddit bot that, when it is called by commenting its username,
# uses ai to figure out what template the meme above it is

import csv
import json
import os
import sys
import shutil
import time
import logging
from datetime import date
from json.decoder import JSONDecodeError

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


import praw
import requests
import webbrowser
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from praw.models import Message
from prawcore import ResponseException

import ai_related_scripts.image_ai

# Get today's day
todays_day = date.today().strftime("%d/%m/%Y")[:2]
# print(todays_day)

# Global config variables
do_debug = False
send_email = True
email_address = "TBD"


def config():
    global reddit
    global s
    global image_class

    # Authenticate email
    s = smtplib.SMTP(host="smtp.gmail.com", port=587)
    s.login("user", "password")

    # authenticate bot
    reddit = praw.Reddit(client_id="XXXXXXXXXX",
                         client_secret="XXXXXXXXXXXXXX",
                         refresh_token="XXXXXXXXXXXXXXXXXXXXX",
                         user_agent="Meme finder by /u/TemplateFinderBot")

    image_class = "_2_tDEnGMLxpM6uOa2kaDB3"

    reddit.read_only = False

    # Set up logger
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='templateFinderBot.log', level=logging.DEBUG)


def load_config(config_file_name):
    """
    Loads config and sets variables
    :param config_file_name: String, name of config file
    """
    # Load config file
    try:
        with open(config_file_name) as config_file:
            config_data = json.load(config_file)
        # Set config variables
        send_email = config_data["send_email"]
        email_address = config_data["email_address"]
    except KeyError:
        config_dict = {"send_email": True, "email_address": "TBD"}

        with open(config_file_name, "w") as config_file:
            json.dump(config_dict, config_file)

        with open("config.json") as config_file:
            config_data = json.load(config_file)
        send_email = config_data["send_email"]
        email_address = config_data["email_address"]


# This function takes the post from the comment it is passed, figures out if it's a photo or not, if it is, it runs the ai on it and returns
# Its confidence and class number.
# It also returns success codes:
# Code 0: All ok, proceed with comment formatting, returned in list with format [0, confidence (0-1000), photo_class, imgur_link, extra_info(if present)]
# Code 1: It cannot identify the class of the photo, returned in list with format[1]
# Code 2: The post is not a photo, returned in list with format [2]
# Code 3: The provided comment is not a top level comment, returned in format [3]
# Code 4: HTTP error, returned in list with format [4, status_code, message]
# Code 5, General error, returned with format [5, Exception]


def is_commented(comment_look):
    """
    :param comment_look: praw Comment
    :return: Boolean
    """
    comment_look.refresh()
    for reply in comment_look.replies:
        # If username on one of the replies is equal to bot username
        if reply.author.name.lower() == "TemplateFinderBott".lower():
            logging.info(f"Already replied to {comment_look.id}, ignoring reply")
            return True
        return False


def get_img_from_url(img_url):
    """
    Saves image to disk from url
    :param img_url: String, url
    :return: 0 if all ok, 1 if not image
    """
    # If it is an image, save it to the disk
    meme = ""

    image_formats = (".png", ".jpeg", ".jpg")

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
        return 1
    return meme


def get_class(comment_look, debug=False):
    """
    Gets the class of a comment
    :param comment_look: praw Comment
    :param debug: Boolean, True for debug output
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
            logging.info(f"{comment_look.id} not top level comment, ignoring reply")
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
                logging.warning(
                    "Reddit server error, waiting 5 seconds to try again")
                time.sleep(5)
                bad_gateway = True
                continue
            # If there is a normal http error
            elif f.status_code != 200 and f.status_code < 500:
                logging.error(f"http error - status code: {f.status_code}, message: {f.json()['message']}")
                return [4, f.status_code, f.json()["message"]]
            # If everything is ok
            else:
                parsed_json = f.json()
                logging.debug("parsed json: " + parsed_json)

                # Figure out if it is an image post by looking at its headers
                img_url = parsed_json["data"]["children"][0]["data"]["url"]

                logging.debug("img url:  " + img_url)

                # If image, save to disk
                if meme := get_img_from_url(img_url) != 1:
                    bad_gateway = False
                else:
                    logging.debug(f"{img_url} not a photo")
                    return [2]

                # TODO make this a google search instead
                search_url = 'http://www.google.hr/searchbyimage/upload'
                multipart = {'encoded_image': (meme, open(meme, 'rb')), 'image_content': ''}
                response = requests.post(search_url, files=multipart, allow_redirects=False)
                fetch_url = response.headers['Location']
                webbrowser.open(fetch_url)
    except Exception as e:
        logging.error(e)
        return [5, e]


# Old method
"""                # Loop through every template until a greater than 50 percent confidence
                for filename in os.listdir(directory):
                    if not filename.endswith(".csv"):

                        template = os.path.join(directory, filename)
                        confidence = ai_related_scripts.image_ai.check_match(template, meme)
                        logging.debug(f"Confidence that {comment_look.id} is {template}: {confidence}")
                        # If there isn't an error
                        if confidence[0] == 0 and confidence[1] >= 50.0:
                            logging.info(f"{comment_look.id} is probably of template {template}")
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
                            logging.error(confidence[1])
                            return [5, confidence[1]]

                    # Class not found
                    logging.info(f"{comment_look.id} did not have a template")
                    return [1]

                # Delete the image
                os.remove(meme)
    except Exception as e:
        logging.error(e)
        return [5, e]"""


approved_subs = ["2wnr3g"]
# Initialize replied_to from a csv file

# print(lines)
# print(replied_to)

# Loop through mentions
# print(reddit.inbox.mentions(limit=10))


def main():
    config()
    load_config("config.json")

    global todays_day
    counter = 0

    template_suggestions = []
    incorrect_templates = []

    while True:
        # Authorization check, it's crap I know
        try:
            for comment in reddit.inbox.mentions(limit=1):
                pass
        except ResponseException:
            logging.critical(
                "Reddit object likely not authenticated, received 401 error from authentication test")
            break

        counter += 1

        for comment in reddit.inbox.mentions(limit=50):
            # If its name is commented and it hasn't replied to the comment, reply to it and append the list to replied_to and a csv file
            if not is_commented(comment) and comment.subreddit_id in approved_subs:

                reply = ""
                if do_debug:
                    match_result = get_class(comment, True)
                else:
                    match_result = get_class(comment)

                # Set reply variable
                # If the function says to proceed
                if match_result[0] == 0:
                    # If there isn't any extra info
                    if len(match_result) == 3:
                        reply = f"""
                                I am {"nearly 100" if match_result[1] > 100.0 else round(match_result[1])}% sure that this uses the {match_result[2]} template.
                                It can be found [here]({match_result[2]}).

                                [^Incorrect?](https://www.reddit.com/message/compose/?to=TemplateFinderBot&subject=INCORRECT&message={{/"post_id/": /"{comment.parent_id}/", /"correct_template/": /"PUT THE LINK TO THE CORRECT TEMPLATE HERE/"}}) [^Github](https://github.com/ThatGuyDavid09/MemeTemplateBot/)
                                """
                    # If there is
                    else:
                        reply = f"""
                                I am {"nearly 100" if match_result[1] > 100.0 else round(match_result[1])}% sure that this uses the {match_result[2]} template.
                                It can be found [here]({match_result[2]}).
                                Some extra info: {match_result[3]}

                                [^Incorrect?](https://www.reddit.com/message/compose/?to=TemplateFinderBot&subject=INCORRECT&message={{/"post_id/": /"{comment.parent_id}/", /"correct_template/": /"PUT THE LINK TO THE CORRECT TEMPLATE HERE/"}}) [^Github](https://github.com/ThatGuyDavid09/MemeTemplateBot/)
                                """
                # If the class cannot be identified
                elif match_result[0] == 1:
                    reply = f"""
                            Sadly, I don't know what template this meme is using.

                            [^Want to include this in future searches?](https://www.reddit.com/message/compose/?to=TemplateFinderBot&subject=REQUEST&message={{/"post_id/": /"{comment.parent_id}/", /"template_link/": /"PUT LINK TO TEMPLATE HERE/", /"template_name/": /"PUT NAME OF TEMPLATE HERE/", /"extra_info/": /"PUT EXTRA INFO HERE, IF THERE IS ANY}}) [^Github](https://github.com/ThatGuyDavid09/MemeTemplateBot/)
                            """
                else:
                    pass

                # Replay to the comment and print some debug
                comment.reply(reply)
                logging.info(f"Replied to {comment.id} in {comment.subreddit}")

        # time.sleep(10)
        # Do daily
        if todays_day != date.today().strftime("%d/%m/%Y")[:2]:

            approved_subjects = ["INCORRECT", "REQUEST"]

            for message in reddit.inbox.unread(limit=None):
                if isinstance(message, Message) and message.was_comment is False and message.subject in approved_subjects:
                    validate = URLValidator()

                    # Check type of message
                    if message.subject == "INCORRECT":
                        try:
                            # Validate Message
                            message_json = json.loads(message.body)
                            temp = message_json["correct_template"]

                            validate(temp)

                            # Append to correct list
                            incorrect_templates.append(message_json)
                        # Check if Json
                        except JSONDecodeError:
                            message.reply("We did not understand the format of your request. Please check your formatting and try again.")
                        # Check if good url
                        except ValidationError:
                            message.reply("That does not seem to have a valid url!")
                        # Check if correct formatting
                        except KeyError:
                            message.reply("We did not understand the format of your request. Please check your formatting and try again.")
                        finally:
                            message.mark_read()

                    if message.subject == "REQUEST":
                        try:
                            # Validate Message
                            message_json = json.loads(message.body)
                            temp = message_json["template_link"]

                            validate(temp)

                            # Append to correct list
                            template_suggestions.append(message_json)
                        # Check if Json
                        except JSONDecodeError:
                            message.reply(
                                "We did not understand the format of your request. Please check your formatting and try again.")
                        # Check if good url
                        except ValidationError:
                            message.reply("That does not seem to have a valid url!")
                        # Check if correct formatting
                        except KeyError:
                            message.reply("We did not understand the format of your request. Please check your formatting and try again.")
                        finally:
                            message.mark_read()
            todays_day = date.today().strftime("%d/%m/%Y")[:2]

            # Email the stuff to me
            if template_suggestions is not None and incorrect_templates is not None and send_email:

                msg = MIMEMultipart()
                msg["From"] = email_address
                msg["To"] = email_address
                msg["Subject"] = "Stuff from reddit bot"

                # Message of email
                if template_suggestions is None:
                    message = f"""
HEY! These are today's template suggestions:
{template_suggestions}

-The reddit bot"""
                elif incorrect_templates is None:
                    message = f"""
HEY! These are today's incorrect templates:
{incorrect_templates}

-The reddit bot"""
                else:
                    message = f"""
HEY! These are today's incorrect templates and template suggestions:
Incorrect templates: {incorrect_templates}
Template suggestions: {template_suggestions}

-The reddit bot"""
                # Send email
                msg.attach(MIMEText(message, "plain"))

                s.send_message(msg)
                del msg
                # Clear the 2 lists
                template_suggestions.clear()
                incorrect_templates.clear()


if __name__ == '__main__':
    main()
