#!/usr/bin/env python3

import os
import sys
import logging
import random
import math
import configparser
import sqlite3

import googlephotos
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.discovery import build
import wget

from matrix_client.client import MatrixClient
from matrix_client.api import MatrixRequestError
from requests.exceptions import MissingSchema
from matrix_bot_api.matrix_bot_api import MatrixBotAPI
from matrix_bot_api.mregex_handler import MRegexHandler
from matrix_bot_api.mcommand_handler import MCommandHandler


##Bot setup - edit Matrix_Bot.ini
config_file = '/mnt/Matrix_Bot.ini'
config = configparser.ConfigParser()
config.read(config_file)

# Global variables
USERNAME = config["BOTINFO"]["username"]  # Bot's username
PASSWORD = config["BOTINFO"]["password"]  # Bot's password
SERVER = config["BOTINFO"]["host"]  # Matrix server URL



#SQL custom functions
def log(number):
    return math.log(number)

def rand():
    return random.random()


##Posts selected image
def post_image(image_file, text, room):
    service.getGooglePhoto(image_file,"temp")
    print(image_file)
    try:
        with open("temp", "rb") as image:
            f = image.read()
            b = bytearray(f)
            a = client.upload(b,"image/jpeg")
            room.send_image(a, text)
    except:
        print("Could not post image")


##Select an image based on the choice of people you want in it and with a weighting

def weighted_image(names_given,text,room):
    names_given.sort()
    people_string = " % ".join(names_given)
    people_string = "% "+people_string+" %"
    db_in = "images.db"
    con = sqlite3.connect(db_in)
    print("Checking database...")
    c = con.cursor()
    con.create_function("log",1,log)
    con.create_function("rand",0,rand)
    try:
        c.execute("SELECT image_name, names FROM images where names like ? ORDER BY -log(1.0 - rand()) / weights LIMIT 1",(people_string,))
        to_send = c.fetchall()[0]
        image_to_send = to_send[0]
        people_in_image = "Image containing: "+to_send[1]
        print(people_in_image)
        c.execute("update images set weights = weights*0.05 where image_name = ?", (image_to_send,))
        print("database updated")
        post_image(image_to_send, people_in_image, room)
    except:
        print("No relevant image could be found")
        room.send_text("No image matches your criteria")
    
    con.commit()
    con.close()

def photo_callback(room,event):
    print("!photo detected")
    selected = [i for i in name_array if i in event['content']['body'].lower()]
    try:
        if "!photo help" in event['content']['body']:
            #Show help mesage with list of commands
            room.send_text(photo_help)
            print("Photo help message sent")
            
        elif "!photo any" in event['content']['body']:
            #Send random picture
            directory = config["DIRECTORY"]["people"]
            post_random_image_dir(directory, "Random image", room)     
            
            
        else:
            input_text = event['content']['body']
            input_text = input_text.split(" ")
            del(input_text[0])
            if selected != []:
                text = "Image of " + " ".join(selected)
                selected_names = [name_array[i] for i in selected]
                weighted_image(selected_names,text,room)
            else:
                print("Please add valid command after !photo")
                room.send_text("Please add valid command after !photo")
    except:
        print("Unable to send image")

def main():
    # Create an instance of the MatrixBotAPI
    bot = MatrixBotAPI(USERNAME, PASSWORD, SERVER)

    photo_handler = MCommandHandler("photo", photo_callback)
    bot.add_handler(photo_handler)

    # Start polling
    bot.start_polling()
    print("Polling started")

    while True:
        input()



if __name__ == "__main__":
    SCOPES = 'https://www.googleapis.com/auth/photoslibrary.readonly'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('photoslibrary', 'v1', http=creds.authorize(Http()))
    service = googlephotos.gphotos(service)

    name_array = dict(config.items("GOOGLE_ALBUMS"))

    host = config["BOTINFO"]["host"]
    username = config["BOTINFO"]["username"]
    password = config["BOTINFO"]["password"]
    bot_sender = config["BOTINFO"]["bot_sender"]
    token = config["BOTINFO"]["token"]
    print("Credentials read")
    client = MatrixClient(host,token,bot_sender)
    main() 