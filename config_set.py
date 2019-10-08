import configparser
import numpy as np
config = configparser.ConfigParser()
import os

config["BOTINFO"]={"host":"https://matrix.org",
                    "username":"***REMOVED***",
                    "password":"***REMOVED***",
                    "room_id_alias":"***REMOVED***:matrix.org",
                    "bot_sender":"@***REMOVED***:matrix.org",
                    "token":"***REMOVED***"
    }

config["DIRECTORY"]={"global":"/home/***REMOVED***/code/matrix-python-sdk/",
                     "image":"/home/***REMOVED***/code/matrix-python-sdk/***REMOVED***/",
                     "text":"/home/***REMOVED***/code/matrix-python-sdk/Resources/Textfiles/",    
                    "people":"/home/***REMOVED***/code/matrix-python-sdk/***REMOVED***/People"
                     }

config["FILE"]={"image_list":"/home/***REMOVED***/code/matrix-python-sdk/***REMOVED***/images.txt",}
                     
config["TEXT_COMMANDS"]={
        "!converse":"conversation_starters",
        "!flirt":"flirt",
        "!truth":"truth"
        }
    
    

with open('Matrix_Bot.ini', 'w') as configfile:
  config.write(configfile)
