# Matrix-bot
A python3 bot for use with matrix.org clients

Requires matrix-python-sdk which can be found at https://github.com/matrix-org/matrix-python-sdk

Main features:

- Send random lines from a textfile
- Send random images from specific folders, including the ability to specify multiple folders and selecting an image common to them all.
- Weightings applied to send images and text to reduce number of repeats




Setup:

File structure:
The bot is designed with the following file structure in mind:

    |Root
        | - Image directory 
            | - People 
            | - Subfolders of images 
        | - Text directory

With the image directory containing several subfolders of folders of images. At the moment the bot is written with .jpg files in mind.

Initialisation:
Run Initialisation.py with directory names changed in the file. This will generate a .pickle file containing a list of images, the names of the subfolders they are in and an initialised weighting. It will also initialise the weightings of the textfiles.

Setting up the bot:
Edit the python file to change directory names, token, bot name and client details at the top of the file.
At the bottom of the file add your hostname, username, password and roomfor the bot.

Running the bot:
Run Matrix_bot.py

