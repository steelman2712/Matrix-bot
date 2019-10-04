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
from numpy.random import choice


from matrix_client.client import MatrixClient
from matrix_client.api import MatrixRequestError
from requests.exceptions import MissingSchema

Global_directory = "Your root directory"
Image_directory = os.path.join(Global_directory,"Images")
Text_directory = os.path.join(Global_directory,"Textfiles/")

image_list_file = os.path.join(Image_directory,"images.txt")


##Bot setup - insert token here, and add host, username, password and chat room id to the bottome line of this code
token = "your matrix.org token here"

bot = "@username:matrix.org"

client = MatrixClient("Host server e.g. https://matrix.org",token, bot)



##Generate array of names of people in photos, directory and keywords
name_list = []
keywords = []
directory = os.path.join(Image_directory,"People/")
folder_list = [x[0] for x in os.walk(directory)]
del folder_list[0]
for i in folder_list:
    name = os.path.split(i)[1]
    name_list.append(name)
for i in name_list:
    keywords.append(str.join("",("!photo ", i)))
name_array = np.column_stack((name_list,folder_list,keywords))

##Generate !photo helpfile
photo_help = ["The !photo command currently supports the following arguments: any"] 
photo_help.extend(name_list)
photo_help = ", ".join(photo_help)
    
##Generate general helpfile


##Link text commands with files, format [command, text file name] 
text_command = np.array([
    #eg.["!converse","conversation_starters"] will pull a random line from the file named "conversation_starters.txt" in the Text directory,
    ])
    
##Generate help list of commands
text_command_help = []


print("Started")
# Called when a message is recieved.
def on_message(room, event):
    #print("message received")
    if event['type'] == "m.room.message":
        if event['content']['msgtype'] == "m.text":
            
            #Posts "Pub." in reply to "Pub?"
            #if "Pub? " or "pub? " in event['content']['body']:
            #    room.send_text("Pub.")
                
            ##
            ##Posts  image on command "!photo"
            if "!photo " in event['content']['body'] and not event['sender']==bot:
                print("!photo detected")
                selected = [i for i in keywords if i in event['content']['body']]
                
                if "!photo help" in event['content']['body']:
                    #Show help mesage with list of commands
                    room.send_text(photo_help)
                    

                elif "!photo any" in event['content']['body']:
                    #Send random picture
                    directory = os.path.join(Image_directory,"People/")
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
            if any(com in event['content']['body'] for com in text_command[:,0]):                           #Checks if command is in message
                for i in text_command[:,0]:                                                                 #Finds location of the text command and what it refers to
                    if i in event['content']['body']:
                        text_list = np.array(text_command[:,0]).tolist()
                        k = text_list.index(i)
                        text_in = text_command[k,1]
                        line_select(text_in,room)
                
           
            
            
         
        #Stores mxc url for all images sent to group by other users
        elif event['content']['msgtype'] == "m.image":
            print("{0}: {1}".format(event['sender'], event['content']['url']))
            image_list = open(image_list_file, "a")
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
    #host, username, password = samples_common.get_user_details(sys.argv)

    #if len(sys.argv) > 4:
        #room_id_alias = sys.argv[4]
    #else:
        #room_id_alias = samples_common.get_input("Room ID/Alias: ")

    main("Host eg. https://matrix.org", "username", "password","room_name:matrix.org") 
