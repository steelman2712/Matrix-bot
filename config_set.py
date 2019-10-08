import configparser
import numpy as np
config = configparser.ConfigParser()
import os

config["BOTINFO"]={"host":"https://matrix.org",
                    "username":"yorkshire_bot1",
                    "password":"DependenceInfect",
                    "room_id_alias":"!yZspvMlFzSmvYZDNoE:matrix.org",
                    "bot_sender":"@yorkshire_bot1:matrix.org",
                    "token":"MDAxOGxvY2F0aW9uIG1hdHJpeC5vcmcKMDAxM2lkZW50aWZpZXIga2V5CjAwMTBjaWQgZ2VuID0gMQowMDJkY2lkIHVzZXJfaWQgPSBAeW9ya3NoaXJlX2JvdDE6bWF0cml4Lm9yZwowMDE2Y2lkIHR5cGUgPSBhY2Nlc3MKMDAyMWNpZCBub25jZSA9IHNZUHhUaWVkRTFPemp2MUMKMDAyZnNpZ25hdHVyZSAGvqy6gCGgQqv-PIovqsaG2sJoD3IC4tKd8Yk2WDFu6Ao"
    }

config["DIRECTORY"]={"global":"/home/reynolds/code/matrix-python-sdk/",
                     "image":"/home/reynolds/code/matrix-python-sdk/Erasmus/",
                     "text":"/home/reynolds/code/matrix-python-sdk/Resources/Textfiles/",    
                    "people":"/home/reynolds/code/matrix-python-sdk/Erasmus/People"
                     }

config["FILE"]={"image_list":"/home/reynolds/code/matrix-python-sdk/Erasmus/images.txt",}
                     
config["TEXT_COMMANDS"]={
        "!converse":"conversation_starters",
        "!flirt":"flirt",
        "!truth":"truth"
        }
    
    

with open('Matrix_Bot.ini', 'w') as configfile:
  config.write(configfile)
