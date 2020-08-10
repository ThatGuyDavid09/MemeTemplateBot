# This is a reddit bot that, when it is called by commenting its username, uses ai to figure out what template the meme above it is
import praw

import csv
import time
import os

import requests
import shutil

import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from bs4 import BeautifulSoup

# authenticate bot
reddit = praw.Reddit(client_id="XXXXXXXXXX",
                     client_secret="XXXXXXXXXXXXXX",
                     refresh_token="XXXXXXXXXXXXXXXXXXXXX",
                     user_agent="Meme finder by /u/TemplateFinderBot")

image_class = "_2_tDEnGMLxpM6uOa2kaDB3"

reddit.read_only = False

# Ai variales
image_size = (256, 256)
batch_size = 16

# This function takes the post from the comment it is passed, figures out if it's a photo or not, if it is, it runs the ai on it and returns
# Its confidence and class number.
# It also returns success codes:
# Code 0: All ok, proceed with comment formatting, returned in list with format [0, photo_class, confidence (scale 0-100)]

# TODO someone needs to redo the image classification

# Code 1: It cannot identify the class of the photo, returned in list with format[1]
# Code 2: The post is not a photo, returned in list with format [3]
# Code 3: The provided comment is not a top level comment
# Code 4: HTTP error, returned in list with format [4, status_code, message]
def get_class(comment):

    bad_gateway = True
    directory = r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Code\Reddit bot"
    image_formats = (".png", ".jpeg", ".jpg")

    api_url = "https://api.reddit.com/api/info/?id="

    while True:
        if comment.parent_id[:3] == "t3_":
            id_to_get = comment.parent_id
        else:
            return [3]

    # This literally just loops the code if reddit has a bad gateway error, yes it happens that often
    while bad_gateway:
        # Sending the api request
        url_to_send = api_url + id_to_get
        # If it starts spitting out random HTTP errors, try to update this
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
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
        img = keras.preprocessing.image.load_img(
            "img.png", target_size=image_size
        )

        img_array = keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)  # Create batch axis

        # Delete the image
        os.remove("img.png")

        # Get the ai's prediction
        predictions = model.predict(img_array)
        scores = predictions[0]
        scores_lst = scores.tolist()
        # Calculate ai's most likely prediction
        max_num = max(scores_lst)
        # If, somehow, the ai manages to give a photo the exact same score in 2 classes, the program will not return the correct result. This is such an edge case
        # that I really don't care if it happens
        max_num_class = scores_lst.index(max_num)

        if max_num < 0.75:
            return [1]
        else:
            return [0, max_num_class, max_num * 100]
# Make the ai
def make_model(input_shape, num_classes):
    inputs = keras.Input(shape=input_shape)
    # Image augmentation block
    x = data_augmentation(inputs)

    # Entry block
    x = layers.experimental.preprocessing.Rescaling(1.0 / 255)(x)
    x = layers.Conv2D(32, 3, strides=2, padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)

    x = layers.Conv2D(64, 3, padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)

    previous_block_activation = x  # Set aside residual

    for size in [128, 256, 512, 728]:
        x = layers.Activation("relu")(x)
        x = layers.SeparableConv2D(size, 3, padding="same")(x)
        x = layers.BatchNormalization()(x)

        x = layers.Activation("relu")(x)
        x = layers.SeparableConv2D(size, 3, padding="same")(x)
        x = layers.BatchNormalization()(x)

        x = layers.MaxPooling2D(3, strides=2, padding="same")(x)

        # Project residual
        residual = layers.Conv2D(size, 1, strides=2, padding="same")(
            previous_block_activation
        )
        x = layers.add([x, residual])  # Add back residual
        previous_block_activation = x  # Set aside next residual

    x = layers.SeparableConv2D(1024, 3, padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)

    x = layers.GlobalAveragePooling2D()(x)
    if num_classes == 2:
        activation = "sigmoid"
        units = 1
    else:
        activation = "softmax"
        units = num_classes

    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(units, activation=activation)(x)

    return keras.Model(inputs, outputs)

# Mostly for classes_num
directory = r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Sets\Sorted memes"
folder_paths = [os.path.join(directory, o) for o in os.listdir(directory) if os.path.isdir(os.path.join(directory,o))]

folders = []

for folder_path in folder_paths:
    folder_split = folder_path.split("\\")
    if "Do not use" not in folder_split[-1]:
        folders.append(folder_split[-1])

classes_num = len(folders)

# Stuff required for compiling the ai
data_augmentation = keras.Sequential(
    [
        layers.experimental.preprocessing.RandomFlip("horizontal"),
        layers.experimental.preprocessing.RandomRotation(0.1),
    ]
)

train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    directory,
    validation_split=0.2,
    subset="training",
    seed=1337,
    image_size=image_size,
    batch_size=batch_size,
)

model = make_model(input_shape=image_size + (3,), num_classes=classes_num)

model.compile(
    optimizer=keras.optimizers.Adam(1e-3),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"])

# Loading weights
model.load_weights(r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Sets\Model weights\save_at_50.h5")

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
        class_of_photo = get_class(1)
        print(class_of_photo)
        comment.reply(class_of_photo)

# print(get_class(1))
