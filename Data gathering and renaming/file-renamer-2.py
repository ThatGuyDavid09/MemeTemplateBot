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

meme_folder = "dj khaled suffering from success"

directory = r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Sorted memes\{folder}".format(folder = meme_folder)

print("Searching directory " + directory + "...")

while True:
    for file in listdir(directory):
        # This try just catches an error when it tries to rename the file while downloading
        try:
            # print(file)
            if "download" in file or "images" in file:
                os.rename(r'{file_path}\{old_name}'.format(file_path = directory, old_name = file),r'{file_path}\{new_name}.'.format(file_path = directory, new_name = get_random_string(30)) + str(file[-3:]))
                print("Renamed " + str(file))
        except:
            pass
