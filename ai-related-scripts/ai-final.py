"""
Title: Image classification from scratch
Author: [fchollet](https://twitter.com/fchollet)
Date created: 2020/04/27
Last modified: 2020/04/28
Description: Training an image classifier from scratch on the Kaggle Cats vs Dogs dataset.
"""
"""
## Introduction
This example shows how to do image classification from scratch, starting from JPEG
image files on disk, without leveraging pre-trained weights or a pre-made Keras
Application model. We demonstrate the workflow on the Kaggle Cats vs Dogs binary
 classification dataset.
We use the `image_dataset_from_directory` utility to generate the datasets, and
we use Keras image preprocessing layers for image standardization and data augmentation.
"""

"""
## Setup
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

import os
import numpy as np
import pandas as pd

classes_num = 0
colnames = ["file_name", "classes"]
data = pd.read_csv('train.csv', names=colnames)

classes_lst = data.classes.tolist()

last = ""
for now in classes_lst:
    if now != last:
        classes_num += 1
    last = now

classes_num -= 1
print(f"Classes calculated, there are {classes_num} classes")

directory = r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Sets\Sorted memes"
folder_paths = [os.path.join(directory, o) for o in os.listdir(directory) if os.path.isdir(os.path.join(directory,o))]

folders = []

for folder_path in folder_paths:
    folder_split = folder_path.split("\\")
    if "Do not use" not in folder_split[-1]:
        folders.append(folder_split[-1])

num_skipped = 0
for folder_name in folders:
    folder_path = os.path.join(directory, folder_name)
    for fname in os.listdir(folder_path):
        fpath = os.path.join(folder_path, fname)
        try:
            fobj = open(fpath, "rb")
            is_jfif = tf.compat.as_bytes("JFIF") in fobj.peek(10)
        finally:
            fobj.close()

        if not is_jfif:
            num_skipped += 1
            # Delete corrupted image
            os.remove(fpath)

print("Deleted %d images" % num_skipped)

"""
## Generate a `Dataset`
"""

image_size = (256, 256)
batch_size = 16

train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    directory,
    validation_split=0.2,
    subset="training",
    seed=1337,
    image_size=image_size,
    batch_size=batch_size,
)
val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    directory,
    validation_split=0.2,
    subset="validation",
    seed=1337,
    image_size=image_size,
    batch_size=batch_size,
)

"""
## Visualize the data
Here are the first 9 images in the training dataset. As you can see, label 1 is "dog"
 and label 0 is "cat".
"""

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 10))
for images, labels in train_ds.take(1):
    for i in range(9):
        ax = plt.subplot(3, 3, i + 1)
        plt.imshow(images[i].numpy().astype("uint8"))
        plt.title(int(labels[i]))
        plt.axis("off")

"""
## Using image data augmentation
When you don't have a large image dataset, it's a good practice to artificially
introduce sample diversity by applying random yet realistic transformations to the
training images, such as random horizontal flipping or small random rotations. This
helps expose the model to different aspects of the training data while slowing down
 overfitting.
"""

data_augmentation = keras.Sequential(
    [
        layers.experimental.preprocessing.RandomFlip("horizontal"),
        layers.experimental.preprocessing.RandomRotation(0.1),
    ]
)

"""
Let's visualize what the augmented samples look like, by applying `data_augmentation`
 repeatedly to the first image in the dataset:
"""

plt.figure(figsize=(10, 10))
for images, _ in train_ds.take(1):
    for i in range(9):
        augmented_images = data_augmentation(images)
        ax = plt.subplot(3, 3, i + 1)
        plt.imshow(augmented_images[0].numpy().astype("uint8"))
        plt.axis("off")

"""
## Standardizing the data
Our image are already in a standard size (180x180), as they are being yielded as
contiguous `float32` batches by our dataset. However, their RGB channel values are in
 the `[0, 255]` range. This is not ideal for a neural network;
in general you should seek to make your input values small. Here, we will
standardize values to be in the `[0, 1]` by using a `Rescaling` layer at the start of
 our model.
"""

"""
## Two options to preprocess the data
There are two ways you could be using the `data_augmentation` preprocessor:
**Option 1: Make it part of the model**, like this:
```python
inputs = keras.Input(shape=input_shape)
x = data_augmentation(inputs)
x = layers.experimental.preprocessing.Rescaling(1./255)(x)
...  # Rest of the model
```
With this option, your data augmentation will happen *on device*, synchronously
with the rest of the model execution, meaning that it will benefit from GPU
 acceleration.
Note that data augmentation is inactive at test time, so the input samples will only be
 augmented during `fit()`, not when calling `evaluate()` or `predict()`.
If you're training on GPU, this is the better option.
**Option 2: apply it to the dataset**, so as to obtain a dataset that yields batches of
 augmented images, like this:
```python
augmented_train_ds = train_ds.map(
  lambda x, y: (data_augmentation(x, training=True), y))
```
With this option, your data augmentation will happen **on CPU**, asynchronously, and will
 be buffered before going into the model.
If you're training on CPU, this is the better option, since it makes data augmentation
 asynchronous and non-blocking.
In our case, we'll go with the first option.
"""

"""
## Configure the dataset for performance
Let's make sure to use buffered prefetching so we can yield data from disk without
 having I/O becoming blocking:
"""

train_ds = train_ds.prefetch(buffer_size=32)
val_ds = val_ds.prefetch(buffer_size=32)

"""
## Build a model
We'll build a small version of the Xception network. We haven't particularly tried to
optimize the architecture; if you want to do a systematic search for the best model
 configuration, consider using
[Keras Tuner](https://github.com/keras-team/keras-tuner).
Note that:
- We start the model with the `data_augmentation` preprocessor, followed by a
 `Rescaling` layer.
- We include a `Dropout` layer before the final classification layer.
"""


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


model = make_model(input_shape=image_size + (3,), num_classes=classes_num)

"""
## Train the model
"""

epochs = 50

callbacks = [
    keras.callbacks.ModelCheckpoint(r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Sets\Model weights\{}".format("save_at_{epoch}.h5")),
]
model.compile(
    optimizer=keras.optimizers.Adam(1e-3),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

input("Press enter to train the ai...")
model.fit(
    train_ds, epochs=epochs, callbacks=callbacks, validation_data=val_ds,
)

"""
We get to ~96% validation accuracy after training for 50 epochs on the full dataset.
"""

"""
## Run inference on new data
Note that data augmentation and dropout are inactive at inference time.
"""

img = keras.preprocessing.image.load_img(
    r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Sets\test.jpg", target_size=image_size
)
img_array = keras.preprocessing.image.img_to_array(img)
img_array = tf.expand_dims(img_array, 0)  # Create batch axis

predictions = model.predict(img_array)
score = predictions[0]
print(score)