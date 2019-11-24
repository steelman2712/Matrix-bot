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
root_dir = '/mnt/'
config_file = os.path.join(root_dir,'Matrix_Bot.ini')
config = configparser.ConfigParser()
config.read(config_file)

# Global variables
USERNAME = config["BOTINFO"]["username"]  # Bot's username
PASSWORD = config["BOTINFO"]["password"]  # Bot's password
SERVER = config["BOTINFO"]["host"]  # Matrix server URL

##Run initialisation check for databases
def image_init_check(root_folder):
    db_in = os.path.join(root_folder,"images.db")
    return os.path.exists(db_in)

def text_init_check():
    directory = config["DIRECTORY"]["text"]
    db_list = [x[1]+".db" for x in list(config.items('TEXT_COMMANDS'))]
    existence_list = []
    for db in db_list:
        db_file = os.path.join(directory,db)
        existence_list.append(os.path.exists(db_file))
    return all(existence_list)

def init_check():
    return image_init_check(root_dir) and text_init_check()

##Generate !photo helpfile
def photo_help_file_gen(name_list):
    photo_help = "The !photo command currently supports the following arguments: any" 
    for i in name_list:
        photo_help = photo_help+", "+i
    print("Photo help to be shown when called: "+photo_help)
    return(photo_help)


#Generate overall helpfile
def help_file_gen(photo_help):
    help_string = "The bot currently takes the following commands: \nCommand:  What the command does \n "
    help_dict = dict(config.items("HELP"))
    for key,value in help_dict.items():
        help_string = help_string + "!"+key+":  " +value+"\n "
    help_string = help_string + "\n" + photo_help
    print(help_string)
    return(help_string)


#SQL custom functions
def log(number):
    return math.log(number)

def rand():
    return random.random()


##Posts selected image
def post_image(image_file, text, room):
    if os.path.exists("temp"):
        os.remove("temp")
    service.getGooglePhoto(image_file,"temp")
    try:
        with open("temp", "rb") as image:
            f = image.read()
            b = bytearray(f)
            a = client.upload(b,"image/jpeg")
            room.send_image(a, text)
            os.remove("temp")
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

##Create line selection function
def line_select(file,room):
    directory = config["DIRECTORY"]["text"]
    file_name = file+".db"
    con = sqlite3.connect(os.path.join(directory,file_name))
    c = con.cursor()
    con.create_function("log",1,log)
    con.create_function("rand",0,rand)
    c.execute("SELECT text FROM table_text ORDER BY -log(1.0 - rand()) / weights LIMIT 1")
    draw =c.fetchall()[0][0]
    c.execute("update table_text set weights = weights*0.05 where text = ?", (draw,))
    con.commit()
    con.close()

    print(draw)
    room.send_text(draw)

#Create command functions to be called by the bot

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
            weighted_image(["%"], "Random image", room)     
            
            
        else:
            if selected != []:
                text = "Image of " + " ".join(selected)
                selected_names = [name_array[i] for i in selected]
                weighted_image(selected_names,text,room)
            else:
                print("Please add valid command after !photo")
                room.send_text("Please add valid command after !photo")
    except:
        print("Unable to send image")


    
def text_callback(room,event):
    try:
        for key in config["TEXT_COMMANDS"]:
            if key in event['content']['body']:
                print(key)
                line_select(config["TEXT_COMMANDS"][key],room)
    except:
        print("Text command could not be sent")


def helpfile_callback(room,event):
    print("Sending helpfile")
    room.send_text(help_file)

def reinit(room,event):
    albums_to_search = [name_array[x] for x in name_array]
    album_list = service.albumList(albums_to_search)
    for albums in album_list:
        print(albums)
        media_list = service.mediaFromAlbum(albums[1])
        googlephotos.SQLImageList(root_dir,media_list,albums[0])
    room.send_text("Reinitialisation complete")

def main():
    # Create an instance of the MatrixBotAPI
    bot = MatrixBotAPI(USERNAME, PASSWORD, SERVER)

    for x in dict(config.items("TEXT_COMMANDS")):
        text_handler = MCommandHandler(x,text_callback)
        bot.add_handler(text_handler)

    photo_handler = MCommandHandler("photo", photo_callback)
    bot.add_handler(photo_handler)

    helpfile_handler = MCommandHandler("help",helpfile_callback)
    bot.add_handler(helpfile_handler)

    reinit_handler = MCommandHandler("reinit", reinit)
    bot.add_handler(reinit_handler)

    # Start polling
    bot.start_polling()
    print("Polling started")

    while True:
        input()



if __name__ == "__main__":
    SCOPES = 'https://www.googleapis.com/auth/photoslibrary.readonly'
    cred_dir = config["BOTINFO"]["credentials_location"]
    store = file.Storage(os.path.join(cred_dir,'credentials.json'))
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(os.path.join(cred_dir,'client_secret.json'), SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('photoslibrary', 'v1', http=creds.authorize(Http()))
    service = googlephotos.gphotos(service)      

    try:
        try:
            name_array = dict(config.items("GOOGLE_ALBUMS"))
        except:
            service.albumConfigWrite()
            name_array = dict(config.items("GOOGLE_ALBUMS"))
    except:
        raise("Couldn't read or write GOOGLE_ALBUMS part of config file")

    if not os.path.exists("images.db"):
        reinit("foo","bar") #Since this is a room command it expects 2 (unused) variables 

    photo_help = photo_help_file_gen([x for x in name_array])
    help_file = help_file_gen(photo_help)

    host = config["BOTINFO"]["host"]
    username = config["BOTINFO"]["username"]
    password = config["BOTINFO"]["password"]
    bot_sender = config["BOTINFO"]["bot_sender"]
    token = config["BOTINFO"]["token"]
    print("Credentials read")
    client = MatrixClient(host,token,bot_sender)

    main() 