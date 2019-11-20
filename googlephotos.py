import os
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.discovery import build
import wget
import sqlite3


##Create list of albums

def albumList(albums_to_search):
    album_list = []
    results = service.albums().list().execute()
    for i in results["albums"]:
        if i["title"] in albums_to_search:
            album_list.append([i["title"],i["id"]])
    return(album_list)



#Gets photo info from albums
def mediaFromAlbum(album_id):
    photo = service.mediaItems().search(body={'albumId':album_id,'pageSize':'50'}).execute()
    media = photo['mediaItems']
    while 'nextPageToken' in photo:
        nextPageToken = photo['nextPageToken']
        photo = service.mediaItems().search(body={'albumId':album_id,'pageSize':'50','pageToken':nextPageToken}).execute()
        media_temp = photo['mediaItems']
        media = media+media_temp
    return(media)

    ##Generate local database
def SQLImageList(directory,media,person_name):
    conn = sqlite3.connect(os.path.join(directory,"images.db"))
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS images (image_name VARCHAR, names VARCHAR, weights NUM, UNIQUE(image_name))')
    for image in media:
        people_string = "% "+person_name+" %"
        #Check if image id already exists and add name to list of it does
        c.execute('select image_name from images where image_name = ? and names not like ?', (image["id"],people_string))
        image_to_update = c.fetchall()
        if image_to_update:
            c.execute('SELECT names FROM images WHERE image_name = ?',(image["id"],))
            #Generate ordered list of names
            names_to_update = c.fetchall()[0][0]
            names_to_update = names_to_update.split(",")
            names_to_update = [x for x in names_to_update if x]
            names_to_update.append(" "+person_name+" ")
            names_to_update.sort()
            names_to_update = ",".join(names_to_update)
            names_to_update = names_to_update
            c.execute("update images set names = ? where image_name = ?", (names_to_update,image["id"]))
        else:
            c.execute("insert or ignore into images (image_name, names, weights) values (?,?,?)",(image["id"]," "+person_name+" ",100))
    conn.commit()
    conn.close()



##Gets photo url from id
def getGooglePhoto(photo_id):
    photo_get = service.mediaItems().get(mediaItemId=photo_id).execute()
    max_width = 1920
    max_height = 1080
    base_url = photo_get['baseUrl']+"=w"+str(max_width)+"-h"+str(max_height)
    print(base_url)
    local_file = wget.download(base_url, out="local_file.jpg")
    local_file


if __name__ == "__main__":
    SCOPES = 'https://www.googleapis.com/auth/photoslibrary.readonly'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('photoslibrary', 'v1', http=creds.authorize(Http()))


