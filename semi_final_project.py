# -*- coding: utf-8 -*-
"""Semi_Final_Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LKYnBQdUsy9po1afFF5oevTWvazvUF46
"""

!pip install underthesea

!pip install Flask

from google.colab import drive
drive.mount('/content/drive')

# Libraries
import nltk
from underthesea import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from keras.utils.np_utils import to_categorical
import numpy as np
import tensorflow as tf
import keras
from tensorflow import keras
from tensorflow.keras import layers
import random
import pickle
import json
import re

patterns = {
	'[àáảãạăắằẵặẳâầấậẫẩ]': 'a',
	'[đ]': 'd',
	'[èéẻẽẹêềếểễệ]': 'e',
	'[ìíỉĩị]': 'i',
	'[òóỏõọôồốổỗộơờớởỡợ]': 'o',
	'[ùúủũụưừứửữự]': 'u',
	'[ỳýỷỹỵ]': 'y'
}

stop_words = ['bạn', 'ban', 'anh', 'chị', 'chi', 'em', 'shop', 'bot', 'ad']

def convert_to_no_accents(text):
	output = text
	for regex, replace in patterns.items():
		output = re.sub(regex, replace, output)
		output = re.sub(regex.upper(), replace.upper(), output)
	return output

trains = {}
with open('/content/drive/MyDrive/UIT/NĂM 4/E-commerce/PROJECT/data/intents.json', 'r', encoding='utf-8') as json_data:
	intents = json.load(json_data)
	for one_intent in intents['intents']:
		sentences = one_intent['patterns']
		trains[one_intent['tag']] = sentences
# print(trains)
classes = {}
X_train = []
y_train = []
for i, (key, value) in enumerate(trains.items()):
	X_train += [word_tokenize(v, format="text") for v in value] + [convert_to_no_accents(v) for v in value]
	y_train += [i]*len(value)*2
	classes[i] = key

pickle.dump(classes, open("/content/drive/MyDrive/UIT/NĂM 4/E-commerce/PROJECT/pkl/classes.pkl", "wb"))

y_train = to_categorical(y_train)

# print(X_train)
# print(y_train)
vectorizer = TfidfVectorizer(lowercase=True, stop_words=stop_words)
X_train = vectorizer.fit_transform(X_train).toarray()

pickle.dump(vectorizer, open("/content/drive/MyDrive/UIT/NĂM 4/E-commerce/PROJECT/pkl/tfidf_vectorizer.pkl", "wb"))
model = tf.keras.Sequential()
model.add(tf.keras.layers.Dense(8, input_dim = X_train.shape[1] ))
model.add(tf.keras.layers.Dense(8))
model.add(tf.keras.layers.Dense(len(y_train[0]), activation='softmax'))
callbacks = [
	keras.callbacks.ModelCheckpoint('/content/drive/MyDrive/UIT/NĂM 4/E-commerce/PROJECT/pkl/model.h5', save_best_only=True),
]
model.compile(loss='mean_squared_error', optimizer='adam')
model.fit(X_train, y_train, epochs=2000, batch_size=8, callbacks=callbacks)
model.save('/content/drive/MyDrive/UIT/NĂM 4/E-commerce/PROJECT/pkl/model.h5')

def classify(sentence):
  sentence = word_tokenize(sentence, format="text")
  #print("test:", sentence, vectorizer)
  results = model.predict(vectorizer.transform([sentence]).toarray())[0]
  results = np.array(results)
  #print("kq", results)
  idx = np.argsort(-results)[0]
  return classes[idx], results[idx]

def response(tag):
	for i in intents['intents']:
		if i['tag'] == tag:
			return random.choice(i['responses'])

!pip freeze > requirements.txt

print('Customer: ', end=''),
x = input()
tag, _ = classify(x)
print('Bot: ', response(tag))

model.variables