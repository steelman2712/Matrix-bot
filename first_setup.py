import os
import shutil


def setup():
    print("Running first time setup script")
    directory = "./mnt/"
    old_dir = "./samples/"

    config_old_location = os.path.join(old_dir,"Matrix_Bot.ini")
    config_new_location = os.path.join(directory,"Matrix_Bot.ini")

    image_folder_location = os.path.join(directory,"Images")
    resource_folder_location = os.path.join(directory,"Resources")
    people_folder_location = os.path.join(image_folder_location,"People")
    text_folder_location = os.path.join(resource_folder_location,"Textfiles")

    people_sample_location = os.path.join(old_dir,"People")
    text_sample_location = os.path.join(old_dir,"Textfiles")

    config_file_gen = False
    image_folder_gen = False
    resource_folder_gen = False


    ##Copy config file
    try:
        if not os.path.exists(config_new_location):
            print("Generating config file")
            shutil.copyfile(config_old_location,config_new_location)
            config_file_gen = True
        else:
            print("Config file already exists, not overwriting")
    except:
        print("Copying of config file failed")
        

    ##Create folders##

    #Images
    try:
        if not os.path.exists(image_folder_location) and config_file_gen:
            print("Creating Image folders")
            os.mkdir(image_folder_location)
            shutil.copytree(people_sample_location,people_folder_location)
            image_folder_gen = True
        else:
            print("Image folder or config file already exists, not overwriting")

    except:
        print("Could not create Image folder")
                                

    #Resources
    try:
        if not os.path.exists(resource_folder_location) and config_file_gen:
            print("Creating Resource folders")
            os.mkdir(resource_folder_location)
            shutil.copytree(text_sample_location,text_folder_location)
            resource_folder_gen = True
        else:
            print("Resource folder or config file already exists, not overwriting")

    except:
        print("Could not create Resource folder")
                            


    
