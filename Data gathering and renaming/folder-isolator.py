# This looks through all folders in "directory" and if any of them have less than 15 files it adds (Do not use) to their name.
# It copies a list of all usable folders to the clipboard.
import pyperclip
import os

from os import listdir

# Get folders in directory
# directory = r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Sorted memes"
directory = r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Sorted memes"
folder_paths = [os.path.join(directory, o) for o in os.listdir(directory) if os.path.isdir(os.path.join(directory,o))]

folders = []

min_files = 15
unuse_suffix = "(Do not use)"

# Loop thorugh them all
for folder_path in folder_paths:
    folder_split = folder_path.split("\\")
    #If the folder isn't marked for unuse, look for it and see if it should. if it should, rename it
    if "Do not use" not in folder_split[-1]:
        num_files = 0
        folder_look_path = directory + r"\{}".format(folder_split[-1])

        print("Looking at folder " + folder_split[-1])

        for file in listdir(folder_look_path):
            num_files += 1
        print("Found {} files".format(str(num_files)))
        if num_files < min_files:
            print("Min files not met, renaming "+ folder_split[-1])
            os.rename(folder_look_path, directory + r"\{folder} {suffix}".format(folder = folder_split[-1], suffix = unuse_suffix))

# Reassign folder paths
folder_paths = [os.path.join(directory, o) for o in os.listdir(directory) if os.path.isdir(os.path.join(directory,o))]

# If it is usable, append it to a list and copy to clipbaord
for folder_path in folder_paths:
    folder_split = folder_path.split("\\")
    if "Do not use" not in folder_split[-1]:
        usable_folders.append(folder_split[-1])

pyperclip.copy(str(usable_folders))
print("Usable folders copied to clipboard!")
