# Moves files from source_directory to train or test directory based on test_chance
import os
import random

from os import listdir

source_directory = r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Sorted memes"
train_directory = r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Test set"
test_directory = r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Training set"

unuse_suffix = "Do not use"
test_chance = 2

# Get folders
folder_paths = [os.path.join(source_directory, o) for o in os.listdir(source_directory) if os.path.isdir(os.path.join(source_directory,o))]

for folder_path in folder_paths:
    folder_split = folder_path.split("\\")
    if unuse_suffix not in folder_split[-1]:
        search_directory = source_directory + r"\{}".format(folder_split[-1])
        for file in listdir(search_directory):
            # Move the files
            if random.randint(1, 10) <= test_chance:
                os.rename(search_directory + r"\{file}".format(file = file), test_directory + r"\{folder}\{file}".format(folder = folder_split[-1], file = file))
            else:
                os.rename(search_directory + r"\{file}".format(file = file), train_directory + r"\{folder}\{file}".format(folder = folder_split[-1], file = file))
