# This takes all files and folders in source_directory and splits them between test and train directory, unless the folder has
# (Do not use) in its name

import os

from os import listdir

source_directory = r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Sorted memes"
train_directory = r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Test set"
test_directory = r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Training set"

unuse_suffix = "Do not use"

# Make appropriate directories
folder_paths = [os.path.join(source_directory, o) for o in os.listdir(source_directory) if os.path.isdir(os.path.join(source_directory,o))]

# If it is usable, append it to a list
for folder_path in folder_paths:
    folder_split = folder_path.split("\\")
    if unuse_suffix not in folder_split[-1]:
        folder = folder_split[-1]
        print("Making folder " + folder)
        os.mkdir(train_directory + r"\{}".format(folder))
        os.mkdir(test_directory + r"\{}".format(folder))
