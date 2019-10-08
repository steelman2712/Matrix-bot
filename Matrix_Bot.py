#!/usr/bin/env python3

# A simple chat client for matrix.
# This sample will allow you to connect to a room, and send/recieve messages.
# Args: host:port username password room
# Error Codes:
# 1 - Unknown problem has occured
# 2 - Could not find the server.
# 3 - Bad URL Format.
# 4 - Bad username/password.
# 11 - Wrong room format.
# 12 - Couldn't find room.

import os
import sys
import samples_common  # Common bits used between samples
import logging
import random
import numpy as np
import pickle
import time
import configparser
from numpy.random import choice


from matrix_client.client import MatrixClient
from matrix_client.api import MatrixRequestError
from requests.exceptions import MissingSchema

config = configparser.ConfigParser()
config.read('Matrix_Bot.ini')


##Bot setup - edit Matrix_Bot.ini

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
    name_array = np.column_stack((name_list,folder_list,keywords))
    return(name_array)

##Generate !photo helpfile
def help_file_gen(name_list):
    photo_help = "The !photo command currently supports the following arguments: any" 
    for i in range(len(name_list)):
        photo_help = photo_help+", "+name_list[i][2]
    return(photo_help)





# Called when a message is recieved.
def on_message(room, event):
    #print("message received")
    if event['type'] == "m.room.message":
        if event['content']['msgtype'] == "m.text":
            
            ##
            ##Posts image on command "!photo"
            if "!photo " in event['content']['body'] and not event['sender']==config["BOTINFO"]["bot_sender"]:
                print("!photo detected")
                selected = [i for i in name_array[:,2] if i in event['content']['body']]
                
                if "!photo help" in event['content']['body']:
                    #Show help mesage with list of commands
                    room.send_text(photo_help)
                    
                    
                elif "!photo any" in event['content']['body']:
                    #Send random picture
                    directory = config["DIRECTORY"]["people"]
                    post_random_image_dir(directory, "Random image", room)     
                    
                    
                else:
                    input_text = event['content']['body']
                    input_text = input_text.split(" ")
                    del(input_text[0])
                    print(input_text)
                    names_given = input_text
                    names_text = ", ".join(names_given[:-1])
                    text = str.join(" ", ("Image of", names_text))
                    text = str.join(" and ", (text,names_given[-1]))
                    print(text)
                    weighted_image(names_given,text,room)
                    #room.send_text("Name not currently in database")
            
            
            ##Samples line from textfile
            for key in config["TEXT_COMMANDS"]:
                if key in event['content']['body']:
                    print(key)
                    line_select(config["TEXT_COMMANDS"][key],room)
                

            
            
            
        #Stores mxc url for all images sent to group by other users
        elif event['content']['msgtype'] == "m.image":
            print("{0}: {1}".format(event['sender'], event['content']['url']))
            image_list = open(config["FILE"]["image_list"], "a")
            image_list.write(event['content']['url']+"\n")
            image_list.close()



##Posts selected image
def post_image(image_file, text, room):
    with open(image_file, "rb") as image:
        f = image.read()
        b = bytearray(f)
        a = client.upload(b,"image/jpeg")
        room.send_image(a, text)

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

##Select an image based on the people you want in it and with a weighting
def weighted_image(names_given,text,room):
    directory = config["DIRECTORY"]["people"]
    with open(os.path.join(directory,"output.txt"),"rb") as infile:
        data_in = pickle.load(infile)

    image_name_list = data_in[0]
    name_list = data_in[1]
    weight = data_in[2]
    
    index=0
    indices = []
    image_index = []
    weight_index = []
    for i in name_list:
        if all(names in i for names in names_given):
            indices.append(index)
            image_index.append(image_name_list[index])
            weight_index.append(weight[index])
        index = index + 1
        
        
    if len(weight_index) != 0:
        total = sum(weight_index)
        weight_index = [weight/total for weight in weight_index]

        draw = choice(image_index, p=weight_index)
        image_to_send = draw
        choice_index = image_name_list.index(draw)
        weight[choice_index] = weight[choice_index]*0.3
        print(name_list[choice_index])
        post_image(image_to_send, text, room)

    else:
        print("No image matches your criteria")
        room.send_text("No image matches your criteria")
    data_out = [image_name_list, name_list, weight]

    with open(os.path.join(directory,"output.txt"),"wb") as outfile:
        pickle.dump(data_out,outfile)



def line_select(file,room):
    Text_directory = config["DIRECTORY"]["text"]
    pickle_file = os.path.join(Text_directory,file+".pickle")
    text_file = os.path.join(Text_directory,file+".txt")
    with open(pickle_file,"rb") as infile:
        weight = pickle.load(infile)
    total = sum(weight)   
    weight_sample = [w/total for w in weight]
    draw = choice(list(open(text_file)), p=weight_sample)
    choice_index = list(open(text_file)).index(draw)
    weight[choice_index] = weight[choice_index]*0.05
    
    print(weight)
    with open(pickle_file,"wb") as outfile:
        pickle.dump(weight,outfile)
    print(draw)
    room.send_text(draw)












def main(host, username, password, room_id_alias):
    client = MatrixClient(host)

    try:
        client.login_with_password(username, password)
    except MatrixRequestError as e:
        print(e)
        if e.code == 403:
            print("Bad username or password.")
            sys.exit(4)
        else:
            print("Check your sever details are correct.")
            sys.exit(2)
    except MissingSchema as e:
        print("Bad URL format.")
        print(e)
        sys.exit(3)

    try:
        room = client.join_room(room_id_alias)
    except MatrixRequestError as e:
        print(e)
        if e.code == 400:
            print("Room ID/Alias in the wrong format")
            sys.exit(11)
        else:
            print("Couldn't find room.")
            sys.exit(12)

    room.add_listener(on_message)
    client.start_listener_thread()

    while True:
        msg = samples_common.get_input()
        if msg == "/quit":
            break
        else:
            room.send_text(msg)
        #try:
        #    client.start_listener_thread()
        #except:
        #    time.wait(30)
            
            
if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    print("Started")
    #host, username, password = samples_common.get_user_details(sys.argv)

    #if len(sys.argv) > 4:
        #room_id_alias = sys.argv[4]
    #else:
        #room_id_alias = samples_common.get_input("Room ID/Alias: ")
    
    host = config["BOTINFO"]["host"]
    username = config["BOTINFO"]["username"]
    password = config["BOTINFO"]["password"]
    room_id_alias = config["BOTINFO"]["room_id_alias"]
    bot_sender = config["BOTINFO"]["bot_sender"]
    token = config["BOTINFO"]["token"]
    
    client = MatrixClient(host,token,bot_sender)
    
    name_array = name_array_gen(config)
    photo_help = help_file_gen(name_array)
    
    
    
    
    main(host, username, password,room_id_alias) 
