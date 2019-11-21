import googlephotos
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.discovery import build
import googlephotos

import configparser
import os
import sqlite3
import math
import random

##Bot setup - edit Matrix_Bot.ini
config_file = '/mnt/Matrix_Bot.ini'
config = configparser.ConfigParser()
config.read(config_file)




SCOPES = 'https://www.googleapis.com/auth/photoslibrary.readonly'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('photoslibrary', 'v1', http=creds.authorize(Http()))
service = googlephotos.gphotos(service)
name_array = dict(config.items("GOOGLE_ALBUMS"))

directory = "/mnt/"
albums_to_search = [name_array[x] for x in name_array]
album_list = service.albumList(albums_to_search)


for albums in album_list:
   print(albums)
   media_list = service.mediaFromAlbum(albums[1])
   googlephotos.SQLImageList(directory,media_list,albums[0])