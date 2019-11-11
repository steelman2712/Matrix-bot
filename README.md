# Matrix-bot
A python3 bot for use with matrix.org clients


# Main features:

- Send random lines from a textfile
- Send random images from specific folders, including the ability to specify multiple folders and selecting an image common to them all.
- Weightings applied to send images and text to reduce number of repeats


# Quick setup
Pull from Docker via:
```bash
sudo docker pull steelman2712/matrix_bot:latest
sudo docker run -v [Location of data on host]:/mnt/ matrix_bot
```
This should pull the docker platform relevant to your platform and run it. The config file and folder structure should be generated, as well as a sample function.

# Building from git 

# Prerequisites
Matrix-client-api and Configparser
```bash 
pip3 install matrix_client configparser
```
# Setup:

Clone from github
```bash
git clone https://github.com/steelman2712/Matrix-bot/
```
Place the config file "Matrix_bot.ini" somewhere.

Edit all instances of '/mnt/Matrix_Bot.ini' in matrix_bot.py to point to where you've placed the config file. Run matrix_bot.py, it should create some databases before starting.

File structure:
The bot is designed with the following file structure in mind:

    |Root
     Matrix_Bot.ini
        | - Image directory 
            | - People 
                | - Subfolders of images 
        | - Text directory
    


With the image directory containing several subfolders of folders of images. At the moment the bot is written with .jpg files in mind.


