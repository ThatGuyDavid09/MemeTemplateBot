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

meme_folder = "2 anime ppl shaking hands"

directory = r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Sorted memes\{folder}".format(folder = meme_folder)

print("Searching directory " + directory + "...")

# If the file has img_ in it, rename it
for file in listdir(directory):
    print(file)
    if "img_" in file:
        os.rename(r'{file_path}\{old_name}'.format(file_path = directory, old_name = file),r'{file_path}\{new_name}'.format(file_path = directory, new_name = get_random_string(30)))
        print("Renamed " + str(file))
