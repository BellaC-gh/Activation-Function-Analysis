# -*- coding: utf-8 -*-
"""Final Project Official.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PDI1bmxi5VrxWtxn1hqbouqWHiZZJ__b
"""

from google.colab import drive
drive.mount('/content/drive')

"""---CNN Neural Network for Image Classification (Created in Google Colab)---"""

# Importing the required libraries
import cv2
import os
import numpy as np
from random import shuffle

# We need to install specific compatible versions of tflean and tensorflow
!pip install tensorflow==2.8.0
!pip install tflearn==0.5.0

import tensorflow as tf
import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.normalization import local_response_normalization
from tflearn.layers.estimator import regression
import tflearn.datasets.mnist as mnist


#Retreiving the directories for our training and testing images which we've uploaded to google colab
TRAIN_DIR = '/content/drive/MyDrive/Cats_vs_Dogs/train'
TEST_DIR = '/content/drive/MyDrive/Cats_vs_Dogs/test'

#creating a variable for the size we want the images to be resized to
IMG_SIZE = 100
#variable for our learning rate
LR = 0.0005

'''Function which will classify each image based on what it named'''
def label_img(img):
	#remove whitespaces
	img = img.strip()
	#retrieves just the letters before the _
	word_label = img.split('_')
	#classifies each image into a binary based on word_label
	if word_label == 'cat': return [1, 0]
	elif word_label == 'dog': return [0, 1]
	#throwaway return label in case any file names don't match the expected form
	else: return [2,2]

'''Function which will create an array containing the data that will train our network'''
def create_train_data():
	# Creating an empty array where we should store the training data
	training_data = []

	#Loop that runs through every image contained the the directory we stored in the variable TRAIN_DIR
	for img in os.listdir(TRAIN_DIR):

		#using the label image function we created earlier to label each image
		label = label_img(img)

		#creating the full path to the image
		path = os.path.join(TRAIN_DIR, img)

		#using cv2 to convert the image to grayscale
		img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

		#using cv2 to change the size of the image into something reasonable to process by a standard cpu
		img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))

		#adding the image and it's label to the end of the array we created at the begining of this funtion
		training_data.append([np.array(img), np.array(label)])

	#shuffling the array of training data we just created in order to randomize the order that the network trains on the images
	shuffle(training_data)

	return training_data

'''Funtion similar to create_train_data'''
def process_test_data():
	testing_data = []
	for img in os.listdir(TEST_DIR):
		#creating the full path to the image
		path = os.path.join(TEST_DIR, img)

		#retrieving the number at the end of each
		img_item,img_num = img.split('_')
		#using cv2 to convert the image to grayscale
		img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

		#again using cv2 to resize the image
		img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))

		#adding the image and it's number to the end of the testing data array, bearing in mind that the image number tells us nothing as to whether it is a cat or a dog
		testing_data.append([np.array(img), img_num])

	shuffle(testing_data)
	return testing_data

'''Calling the above to funtions to create the training and the testing data for our network'''
train_data = create_train_data()
test_data = process_test_data()

'''Creating the neural network using tensorflow'''
#ensuring we have a cleared graph to work with
tf.compat.v1.reset_default_graph()

#Input Layer
#creating the imput layer of our neural network, which expects images of the size (IMG_SIZE x IMG_SIZE) that are grayscale (1)
convnet = input_data(shape =[None, IMG_SIZE, IMG_SIZE, 1], name ='input')

#--First Layer--
"""creating a 2D convolutional layer with 32 filters, each using a 5x5 filter size
and leaky_relu activation function. Then processing the previously generated
layer through it. The input is a 50x50 matrix representing each image, the
filters are a smaller matrix (5x5 in this case) that contains weights to extract
the patterns of each image. The 5x5 filter is passed over the 50x50 image one
pixel at a time to create a smaller output called a feature map. The goal here
being to create a more simplified image that still contains the important
details. Finally the relu activation funtion is applied, which just reviews the
output one element (pixel) at a time and changes any negative values to zero and
leaves the positive values unchanged."""
convnet = conv_2d(convnet, 32, 5, activation ='leaky_relu')
#creating a 2D max pooling layer with a 5x5 window size and applies it to the input convnet
convnet = max_pool_2d(convnet, 5)

#--Second Layer--
convnet = conv_2d(convnet, 32, 5, activation ='leaky_relu')
convnet = max_pool_2d(convnet, 5)

#--Third Layer--
convnet = conv_2d(convnet, 32, 5, activation ='leaky_relu')
convnet = max_pool_2d(convnet, 5)

#--Output Layer--
#defines the output layer of the neural network with two output classes (cats vs dogs in this case), using softmax activation for classification
convnet = fully_connected(convnet, 2, activation ='softmax')
#regression model for training using the Adam optimizer with categorical cross-entropy loss.
convnet = regression(convnet, optimizer ='adam', learning_rate = LR,
	loss ='categorical_crossentropy', name ='targets')

model = tflearn.DNN(convnet, tensorboard_dir ='log')

# Splitting the testing data and training data
train = train_data[:-50]
validate = train_data[-50:]

'''Setting up the features and labels'''
# X-Features & Y-Labels
X = np.array([i[0] for i in train]).reshape(-1, IMG_SIZE, IMG_SIZE, 1)
Y = np.array([i[1] for i in train])
validate_x = np.array([i[0] for i in validate]).reshape(-1, IMG_SIZE, IMG_SIZE, 1)
validate_y = np.array([i[1] for i in validate])


#Creating a title for our model which also lists the learning rate currently being used
MODEL_NAME = '\nCats vs Dogs \n -Learning Rate:{} \n -Model Type:{}'.format(LR, 'Basic Convolutional with 6 Layers')

# Lists to store training and validation losses
training_loss = []
validation_loss = []

# Fit the model and manually collect loss values
for epoch in range(10):
    model.fit({'input': X}, {'targets': Y}, n_epoch=1, validation_set=({'input': validate_x}, {'targets': validate_y}),
              snapshot_step=64, show_metric=True, run_id=MODEL_NAME)

    # Evaluate training and validation loss after each epoch
    train_metrics = model.evaluate(X, Y)
    val_metrics = model.evaluate(validate_x, validate_y)

    training_loss.append(train_metrics[0])
    validation_loss.append(val_metrics[0])

model.save(MODEL_NAME)

# Plotting the loss graph
import matplotlib.pyplot as plt

epochs = range(1, len(training_loss) + 1)
plt.plot(epochs, training_loss, label='Training Loss')
plt.plot(epochs, validation_loss, label='Validation Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()


print('\n')


'''Testing the data'''
import matplotlib.pyplot as plt
test_data = process_test_data()


fig = plt.figure(figsize=(10, 10))

for num, data in enumerate(test_data[:20]):
	img_num = data[1]
	img_data = data[0]

	y = fig.add_subplot(4, 5, num + 1)
	orig = img_data
	data = img_data.reshape(IMG_SIZE, IMG_SIZE, 1)

	model_out = model.predict([data])[0]

	if np.argmax(model_out) == 1: str_label ='Dog'
	else: str_label ='Cat'

	y.imshow(orig, cmap ='gray')
	plt.title(str_label)
	y.axes.get_xaxis().set_visible(False)
	y.axes.get_yaxis().set_visible(False)
	plt.subplots_adjust(hspace=0.5)
plt.show()