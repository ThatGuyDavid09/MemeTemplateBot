# This is (or will be) an implementation of a transfer ai that
# Matches similar memes together and returns some useful info about them
# This will allow for more obscure memes to be recognized

import cv2

"""
To use:
Put your 2 images you want to compare in the folder this is in
Put their file names in the variables below
"""

template_use = "test1.jpg"
meme_use = "test2.jpg"


def main(template, meme):
    """
    Main function
    :param template: File path
    :param meme: File path
    :return: None
    """
    print(check_match(template, meme))


def check_match(template, meme, debug=False):
    """
    This calculates how similar template is to meme
    :param template: File path
    :param meme: File path
    :param debug: Debug
    :return: [-1, Exception] if error, [0, confidence] if all ok
    """
    original = cv2.imread(template)
    image_to_compare = cv2.imread(meme)
    try:
        # Check for similarities between the 2 images
        sift = cv2.xfeatures2d.SIFT_create()
        kp_1, desc_1 = sift.detectAndCompute(original, None)
        kp_2, desc_2 = sift.detectAndCompute(image_to_compare, None)

        index_params = dict(algorithm=0, trees=5)
        search_params = dict()
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches = flann.knnMatch(desc_1, desc_2, k=2)

        good_points = []
        for m, n in matches:
            if m.distance < 0.6 * n.distance:
                good_points.append(m)

        # Define how similar they are
        if len(kp_1) <= len(kp_2):
            number_keypoints = len(kp_1)
        else:
            number_keypoints = len(kp_2)

        if debug:
            print("[DEBUG] Keypoints 1ST Image: " + str(len(kp_1)))
            print("[DEBUG] Keypoints 2ND Image: " + str(len(kp_2)))
            print("[DEBUG] GOOD Matches:", len(good_points))
            # Multiplied by 1000 to exaggerate any differences
            print("[DEBUG] How good it's the match: ", len(good_points) / number_keypoints * 1000)

            # Show images
            result = cv2.drawMatches(original, kp_1, image_to_compare, kp_2, good_points, None)

            cv2.imshow("result", cv2.resize(result, None, fx=0.4, fy=0.4))
            cv2.imwrite("feature_matching.jpg", result)

            cv2.imshow("Original", cv2.resize(original, None, fx=0.4, fy=0.4))
            cv2.imshow("Duplicate", cv2.resize(image_to_compare, None, fx=0.4, fy=0.4))
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return [0, len(good_points) / number_keypoints * 1000]
    except Exception as e:
        return [-1, e]


if __name__ == '__main__':
    main(template_use, meme_use)

# Another attempt, may use later
"""
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt
import numpy as np
import cv2

def mse(imageA, imageB):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err
def compare_images(imageA, imageB, title):
    # compute the mean squared error and structural similarity
    # index for the images
    m = mse(imageA, imageB)
    s = ssim(imageA, imageB)
    # setup the figure
    fig = plt.figure(title)
    plt.suptitle("MSE: %.2f, SSIM: %.2f" % (m, s))
    # show first image
    ax = fig.add_subplot(1, 2, 1)
    plt.imshow(imageA, cmap = plt.cm.gray)
    plt.axis("off")
    # show the second image
    ax = fig.add_subplot(1, 2, 2)
    plt.imshow(imageB, cmap = plt.cm.gray)
    plt.axis("off")
    # show the images
    plt.show()

meme = cv2.imread("test1.jpg")
template = cv2.imread("test2.jpg")
meme_shape = meme.shape[:2]
template = cv2.resize(template, meme_shape)
# convert the images to grayscale
meme = cv2.cvtColor(meme, cv2.COLOR_BGR2GRAY)
template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

# TODO: Make the images the same size

# initialize the figure
fig = plt.figure("Images")
images = ("Meme", meme), ("Template", template)
# loop over the images
for (i, (name, image)) in enumerate(images):
    # show the image
    ax = fig.add_subplot(1, 2, i + 1)
    ax.set_title(name)
    plt.imshow(image, cmap = plt.cm.gray)
    plt.axis("off")
# show the figure
plt.show()
# compare the images
compare_images(meme, template, "Meme vs. Template")
"""
