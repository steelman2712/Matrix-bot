#!/usr/bin/env python3

import os
import sys
import logging
import random
import math
import configparser
import sqlite3

import initialisation
import re_init
import first_setup

from matrix_client.client import MatrixClient
from matrix_client.api import MatrixRequestError
from requests.exceptions import MissingSchema
from matrix_bot_api.matrix_bot_api import MatrixBotAPI
from matrix_bot_api.mregex_handler import MRegexHandler
from matrix_bot_api.mcommand_handler import MCommandHandler

##Bot setup - edit Matrix_Bot.ini
if not os.path.exists('/mnt/Matrix_Bot.ini'):
    first_setup.setup()
    print("Initial setup complete. There should now be a .ini file in the root of the folder you mounted. Add the credentials of your bot account and any command setup you want to do in that file. Add you images into subfolders in the /Images/People folder (a pair of example subfolders have been added) and any textfiles to /Resources/Textfiles. Re-run the docker container once you've done that and it should hopefully work.")
    exit()
config_file = '/mnt/Matrix_Bot.ini'
config = configparser.ConfigParser()
config.read(config_file)

# Global variables
USERNAME = config["BOTINFO"]["username"]  # Bot's username
PASSWORD = config["BOTINFO"]["password"]  # Bot's password
SERVER = config["BOTINFO"]["host"]  # Matrix server URL

##Run initialisation check for databases
def image_init_check():
    directory = config["DIRECTORY"]["people"]
    db_in = os.path.join(directory,"images.db")
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
    return image_init_check() and text_init_check()



##Generate array of names of people in photos, directory and keywords
def name_array_gen(config):
    name_list = []
    keywords = []
    directory = config["DIRECTORY"]["people"]
    folder_list = [x[0] for x in os.walk(directory)]
    del folder_list[0]
    for i in folder_list:
        name = os.path.split(i)[1]
        name_list.append(name)
    for i in name_list:
        keywords.append(str.join("",("!photo ", i)))
    name_array = [name_list,folder_list,keywords]
    return(name_array)


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


##  MATRIX CLIENT FUNCTION SETUP ##


##Posts selected image
def post_image(image_file, text, room):
    try:
        with open(image_file, "rb") as image:
            f = image.read()
            b = bytearray(f)
            a = client.upload(b,"image/jpeg")
            room.send_image(a, text)
    except:
        print("Could not post image")
    
def post_random_image(input_directory, text, room):
    image_selected = random.choice(os.listdir(input_directory))
    image_to_send = os.path.join(input_directory,image_selected)
    print(image_to_send, text)
    post_image(image_to_send,text, room)

##Send random photo from directory containing directories containing images
def post_random_image_dir(input_directory, text, room):
    folder_selected = [x[0] for x in os.walk(input_directory)]
    del folder_selected[0]
    q = random.choice(folder_selected)
    image_selected = random.choice(os.listdir(q))
    image_to_send = os.path.join(q,image_selected)
    print(image_to_send, text)
    post_image(image_to_send, text, room)

##Select an image based on the choice of people you want in it and with a weighting

def weighted_image(names_given,text,room):
    directory = config["DIRECTORY"]["people"]
    names_given.sort()
    people_string = " % ".join(names_given)
    people_string = "% "+people_string+" %"
    db_in = os.path.join(directory,"images.db")
    con = sqlite3.connect(db_in)
    print("Checking database...")
    c = con.cursor()
    con.create_function("log",1,log)
    con.create_function("rand",0,rand)
    try:
        c.execute("SELECT image_location, names FROM images where names like ? ORDER BY -log(1.0 - rand()) / weights LIMIT 1",(people_string,))
        to_send = c.fetchall()[0]
        image_to_send = to_send[0]
        people_in_image = "Image containing: "+to_send[1]
        print(people_in_image)
        c.execute("update images set weights = weights*0.05 where image_location = ?", (image_to_send,))
        post_image(image_to_send, people_in_image, room)
    except:
        print("No relevant image could be found")
        room.send_text("No image matches your criteria")
    
    con.commit()
    con.close()




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
    



## COMMAND SETUP ##

def photo_callback(room,event):
    print("!photo detected")
    selected = [i for i in name_array[2] if i in event['content']['body']]
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
            if selected != []:
                text = str.join(" ", ("Image of", selected))
                text = str.join(" ", (text,selected))
                weighted_image(selected,text,room)
            else:
                print("Please add valid command after !photo")
            #room.send_text("Name not currently in database")
    except:
        print("Unable to send image")
        room.send("Unable to find or send relevant image")
    

    
def text_callback(room,event):
    try:
        for key in config["TEXT_COMMANDS"]:
            if key in event['content']['body']:
                print(key)
                line_select(config["TEXT_COMMANDS"][key],room)
    except:
        print("Text command could not be sent")
                
            
## Refresh databases from within chat
def reinit(room,event):
    try:
        Image_directory = config["DIRECTORY"]["people"]
        re_init.SQLImageList(Image_directory)
        print("Image database refreshed")
        room.send_text("Image database refreshed")
        
    except:
        print("Image Database refresh failed")
        room.send_text("Image Database refresh failed")
    try:
        Text_directory = config["DIRECTORY"]["text"] 
        re_init.SQLTextList(Text_directory)
        print("Text databases refreshed")
        room.send_text("Text databases refreshed")
    except:
        print("Text Database refresh failed")
        room.send_text("Text Database refresh failed")


def helpfile_callback(room,event):
    print("Sending helpfile")
    room.send_text(help_file)
                
def main():
    # Create an instance of the MatrixBotAPI
    bot = MatrixBotAPI(USERNAME, PASSWORD, SERVER)
    
    for x in dict(config.items("TEXT_COMMANDS")):
        text_handler = MCommandHandler(x,text_callback)
        bot.add_handler(text_handler)
        
    photo_handler = MCommandHandler("photo", photo_callback)
    bot.add_handler(photo_handler)
    
    reinit_handler = MCommandHandler("reinit", reinit)
    bot.add_handler(reinit_handler)
    
    helpfile_handler = MCommandHandler("help",helpfile_callback)
    bot.add_handler(helpfile_handler)
    
    # Start polling
    bot.start_polling()
    print("Polling started")

    while True:
        input()


if __name__ == "__main__":
    if config["AUTOCONFIG"]["first_run"] == "True":
        print("Starting Initialisation")
        Image_directory = config["DIRECTORY"]["people"]
        Text_directory = config["DIRECTORY"]["text"]
        initialisation.SQLImageList(Image_directory)
        initialisation.SQLTextList(Text_directory)
        config.set("AUTOCONFIG","first_run","False")
        with open(config_file,"w") as config_out:
            config.write(config_out)
        print("Initialisation complete")
    
    name_array = name_array_gen(config)
    photo_help = photo_help_file_gen(name_array[0])
    help_file = help_file_gen(photo_help)
    
    host = config["BOTINFO"]["host"]
    username = config["BOTINFO"]["username"]
    password = config["BOTINFO"]["password"]
    bot_sender = config["BOTINFO"]["bot_sender"]
    token = config["BOTINFO"]["token"]
    print("Credentials read")
    client = MatrixClient(host,token,bot_sender)
    main() 
    
    
    
    
    
    
    
    
    
    
    
    
