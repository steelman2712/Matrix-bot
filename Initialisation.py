import os
import pickle
import numpy as np
from numpy.random import choice

root_dir = "Your directory"

Image_directory = os.path.join(root_dir,"Images/People")
Text_directory = os.path.join(root_dir,"Textfiles")

##Initialise people naming and weighting

image_list = []
image_name_list = []
name_list = []
weight = []

folder_list = [x[0] for x in os.walk(Image_directory)]
del folder_list[0]
for i in folder_list:
    name = os.path.split(i)[1]
    for root, dirnames, filenames in os.walk(os.path.join(Image_directory,i)):
        subdirectory = os.path.join(Image_directory,i)
        for image in filenames:
            if image.endswith(".jpg"):
                #print(image)
                if image not in image_list:
                    #print("new")
                    image_list.append(image)
                    image_name_list.append(os.path.join(subdirectory, image))
                    name_list.append([name])
                    weight.append(100)
                else:
                    #print("old")
                    index = image_list.index(image)
                    #print(name_list[index])
                    name_list[index].append(name)
 
data_out = [image_name_list, name_list, weight]

with open(os.path.join(Image_directory,"output.txt"),"wb") as outfile:
    pickle.dump(data_out,outfile)


##Initialise text file weightings


for root, dirnames, filenames in os.walk(Text_directory):
    for text in filenames:
        print(text)
        if text.endswith(".txt"):
            number_of_lines = len(list(open(os.path.join(Text_directory,text))))
            weight = np.tile(100,number_of_lines)
            print(weight)
            out_name = text.split(".")
            out_name = out_name[0]+".pickle"
            out_name = os.path.join(Text_directory,out_name)
            with open(os.path.join(Text_directory,out_name),"wb") as outfile:
                pickle.dump(weight,outfile)
        
