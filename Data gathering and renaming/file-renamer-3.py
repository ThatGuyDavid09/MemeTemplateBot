# Searches thorugh all directories in directory and executes file-renamer-2 on them
import random
import string
import os
import pathlib

from os import listdir
from os.path import isfile

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

directory = r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Sorted memes"
folder_paths = [os.path.join(directory, o) for o in os.listdir(directory) if os.path.isdir(os.path.join(directory,o))]

folders = []

for folder_path in folder_paths:
    folder_split = folder_path.split("\\")
    if "Do not use" not in folder_split[-1]:
        folders.append(folder_split[-1])

# print(folders)

while True:
    for folder in folders:
        search_directory = directory + r"\{}".format(folder)
        # print("Searching " + str(folder))
        # print(search_directory)
        for file in listdir(search_directory):
            # This try just catches an error when it tries to rename the file while downloading
            try:
                # print(file)
                if "download" in file or "images" in file:
                    os.rename(r'{file_path}\{old_name}'.format(file_path = search_directory, old_name = file),r'{file_path}\{new_name}.'.format(file_path = search_directory, new_name = get_random_string(30)) + str(file[-3:]))
                    print("Renamed " + str(file) + " in " + folder)
            except:
                pass
