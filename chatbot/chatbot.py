import random
import json
import requests 
import pickle
import numpy as np
import tensorflow as tf

import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

import paralleldots 
paralleldots.set_api_key("BfAaULYjwzc4srLvUYVWvmtIVf9KIrfUWbz0s54lVlo")
url = 'http://ws.audioscrobbler.com/2.0/'
#api for lastfm = c598cd224db2938e2efcf42b3e492b72


lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbot_model.h5')

def clean_up_Sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]

    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_Sentence(sentence)
    bag = [0] * len(words)

    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1

    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse = True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})

    return return_list



def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']

    for i in list_of_intents:
        if i['intent'] == tag:
            result = random.choice(i['responses'])
            break
    
    return result
print("Chatbot is now running ")

def emotion_analysis(analyze):
    max_val = 0
    emotion = ""
    for i,j in analyze.items():
        for key,value in j.items():
            if value > max_val:
                max_val = value
                emotion = key
    
    return emotion

artists = {
    "Fear" : ["Burzum", "Swans", "Nine Inch Nails", "Tool", "Chelsea Wolfe", "Marilyn Manson", "Neurosis", "Ministry", "Skinny Puppy", "KMFDM", "Front Line Assembly", "Rammstein", "Rob Zombie", "Gary Numan"  ],
    "Happy": ["Bruno Mars", "Meghan Trainor", "BTS", "Pharrell Williams", "Katy Perry", "Taylor Swift", "Maroon 5", "Dua Lipa", "Carly Rae Jepsen", "Camila Cabello", "Selena Gomez","Halsey", "NCT", "GOT7" ,"Drake"],
    "Angry": ["Kendrick Lamar", "Billie Eilish", "Denzel Curry", "The Weeknd", "Eminem", "Ariana Grande", "Jhene Aiko", "Khalid", "Post Malone","PartyNextDoor", "Bryson Tiller","H.E.R.",  ], 
    "Sad": ["Billie Eilish", "Lana Del Rey", "Adele", "Frank Ocean", "Kacey Musgraves", "Blood Orange", "Childish Gambino", "SZA", "Khalid", "Anderson .Paak"],
    "Excited": ["Lizzo", "Kendrick Lamar", "Drake", "Arctic Monkeys", "Grimes", "Coldplay"],
    "Bored": ["Mac DeMarco", "Frank Ocean", "Ariel Pink", "King Krule"]
}




def get_top_tracks(url, artist):
    params = {
    'method': 'artist.gettoptracks',
    'artist': artist,
    'api_key': 'c598cd224db2938e2efcf42b3e492b72',
    'format': 'json'
    }
    # send GET request to API endpoint with parameters
    response = requests.get(url, params=params)

    # parse JSON response
    data = json.loads(response.text)

    track_names = []
    for i,track in enumerate(data['toptracks']['track']):
        if i >= 6:
            break
        track_names.append(track['name'])


    return track_names
    
def get_similar_artists(url, artist):
    params2 = {
    'method': 'artist.getSimilar',
    'artist': artist,
    'api_key': 'c598cd224db2938e2efcf42b3e492b72',
    'format': 'json'
    }

     # send GET request to API endpoint with parameters
    response2 = requests.get(url, params=params2)

    # parse JSON response
    data2 = json.loads(response2.text)

    similar_artists = []
    for i,artist in enumerate(data2['similarartists']['artist']):
        if i >= 6:
            break
        similar_artists.append(artist['name'])

    return similar_artists


def get_user_response(message):
    #message = input("")
    #if message == "quit":
    #    break
    analyze = paralleldots.emotion(message)
    emotion = emotion_analysis(analyze)
                
    
    for i,j in artists.items():
        if i == emotion:
            random_artist = random.choice(j)

    track_names = get_top_tracks(url, random_artist)
    similar_artists = get_similar_artists(url, random_artist)



    ints = predict_class(message)
    res = get_response(ints, intents)

    return [res, emotion, random_artist, track_names, similar_artists]
    #print(res)
    #print("an artists is: ", random_artist, "and your emotion is: ", emotion)
    #print("some of you tracks are: ", track_names)
    #print("Similar arsists are: ", similar_artists)
