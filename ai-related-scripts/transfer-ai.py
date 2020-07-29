# This is (or will be) an implementation of a transfer ai that
# Matches similar memes together and returns some useful info about them
# This will allow for more obscure memes to be recognized

# After some googling, I figured out we might be able to use an image hash to figure out if the images are similar
# Run pip install imagehash
from PIL import Image
import imagehash
hash1 = imagehash.whash(Image.open('test1.jpg'))
print(hash1)
hash2 = imagehash.whash(Image.open('test2.jpg'))
print(hash2)
