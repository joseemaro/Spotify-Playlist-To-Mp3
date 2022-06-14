# Spotify-Playlist-To-Mp3
This is a python project that convert Spotify playlist into mp3 files in your pc. This project has a simple interface make with tkinter. Enjoy!

# Configuration

## Download the Project

```bash
git clone https://github.com/joseemaro/Spotify-Playlist-To-Mp3.git
```

## Set Dependencies

```bash
pip install spotipy 
pip install youtube_dl 
pip install youtube_search
pip install ffmpeg
```

## FFmpeg configuration

You need to copy the files inside the folder "ffmpegData" to the directory where 'youtube-dl.exe' is installed, for example in windows is '$path:"Python\Python38-32\Scripts"'

## Set up Spotify Account

You need to go to Spotify [dashboard](https://developer.spotify.com/dashboard/). Here you must Log in and click the button "Create App", with any name it doesn't matter.
Here you will see your Client ID and your Client Secret, you must copy this codes for later.
Then you will need your Spotify Username, this is in your profile of spotify [profile](https://www.spotify.com/ar/account/overview/)

Finally you will need the playlist that you want to download, this has an Url like this: 'https://open.spotify.com/playlist/586Li8UF7LrIstfaEhvGpU'
You will need only the code at the final of this, so the code will be: 586Li8UF7LrIstfaEhvGpU

## (Optional) Set txt file

You can complete the fields when you run the project or you can complete the fields through a txt file.
You can copy the client id, client secret, username and playlist id into the 'data.txt' file, so every time that you use this project this fields will automatically be loaded in the interface.
You must copy the codes before the = of each field(without spaces). You have to see something like this:
Playlist ID=586Li8UF7LrIstfaEhvGpU

# Running

In your terminal you must run this code, then the interface will be open
```bash
python spotify-to-mp3.py  
```
