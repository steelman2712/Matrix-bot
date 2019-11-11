import os
import sqlite3
import configparser

def SQLImageList(directory):
    image_list = []     #NAME OF IMAGE FILE
    image_name_list = []    #LOCATION + FILENAME OF IMAGE FILE
    name_list = []      #NAMES OF PEOPLE IN IMAGE
    folder_list = [x[0] for x in os.walk(directory)]
    del folder_list[0]
    for i in folder_list:
        name = os.path.split(i)[1]
        for root, dirnames, filenames in os.walk(os.path.join(Image_directory,i)):
            subdirectory = os.path.join(Image_directory,i)
            for image in filenames:
                if image.endswith(".jpg" or ".jpeg"):
                    if image not in image_list:
                        image_list.append(image)
                        image_name_list.append(os.path.join(subdirectory, image))
                        name_list.append([" "+name+" "])
                    else:
                        index = image_list.index(image)
                        name_list[index].append(" "+name+" ")
    
    conn = sqlite3.connect(os.path.join(directory,"images.db"))
    c = conn.cursor()
    for i in range(len(image_name_list)):
        name_list[i].sort()
        people_string = "%".join(name_list[i])
        people_string = "%"+people_string+"%"
        c.execute('select image_name from images where image_name = ? and names not like ?', (image_list[i],people_string))
        image_to_update = c.fetchall()
        if image_to_update:
            c.execute("update images set names = ? where image_name = ?", (" ".join(name_list[i]),image_list[i]))
        
        c.execute("insert or ignore into images (image_name, image_location, names, weights) values (?,?,?,?)",(image_list[i],image_name_list[i]," ".join(name_list[i]),100))
        
    conn.commit()
    conn.close()

def SQLTextList(directory):
    for root, dirnames, filenames in os.walk(directory):
        for text in filenames:
            if text.endswith(".txt"):
                in_file = open(os.path.join(directory,text))
                in_file_list = list(in_file)
                number_of_lines = len(in_file_list)
                out_name = text.split(".")
                file_name = out_name[0]
                out_name = file_name+".db"
                out_name = os.path.join(directory,out_name)
                
                conn = sqlite3.connect(out_name)
                c = conn.cursor()
                print(file_name)
                for i in range(number_of_lines):
                    line_to_write = in_file_list[i].rstrip()
                    c.execute('INSERT OR IGNORE INTO table_text (text, weights) values (?,?)', (line_to_write,100))
                conn.commit()
                conn.close()

                in_file.close()


if __name__ == "__main__":
    
    config = configparser.ConfigParser()
    config.read('/home/***REMOVED***/code/matrix-python-sdk/test_zone/Matrix_Bot.ini')

    Image_directory = config["DIRECTORY"]["people"]
    Text_directory = config["DIRECTORY"]["text"]
    
    
    SQLImageList(Image_directory)
    SQLTextList(Text_directory)
