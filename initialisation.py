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
        for root, dirnames, filenames in os.walk(os.path.join(directory,i)):
            subdirectory = os.path.join(directory,i)
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
    try:
        c.execute('drop table images')
    except:
        print("no existing table to drop")
    c.execute('CREATE TABLE images (image_name VARCHAR, image_location VARCHAR, names VARCHAR, weights NUM, UNIQUE(image_name))')
    for i in range(len(image_name_list)):
        name_list[i].sort()
        c.execute('INSERT OR IGNORE INTO images (image_name, image_location, names, weights) values (?,?,?,?)', (image_list[i],image_name_list[i]," ".join(name_list[i]),100))
    conn.commit()
    conn.close()
    print("Image database created")

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
                try:
                    c.execute('drop table table_text')
                except:
                    print("no existing table to drop")
                c.execute('CREATE TABLE table_text (text VARCHAR, weights NUM,UNIQUE(text))')
                for i in range(number_of_lines):
                    line_to_write = in_file_list[i].rstrip()
                    c.execute('INSERT OR IGNORE INTO table_text (text, weights) values (?,?)', (line_to_write,100))
                conn.commit()
                conn.close()

                in_file.close()
    print("Text databases created")


if __name__ == "__main__":
    
    config = configparser.ConfigParser()
    config.read('/mnt/Matrix_Bot.ini')

    Image_directory = config["DIRECTORY"]["people"]
    Text_directory = config["DIRECTORY"]["text"]
    
    SQLImageList(Image_directory)
    SQLTextList(Text_directory)
