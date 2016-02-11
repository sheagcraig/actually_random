# Actually Random

## Introduction
I like to rip mountain bike trails to my giant Spotify playlist,
"Bottomless Happiness". Unfortunately, Spotify's "shuffle" play feature
is not really random. The algorithm is not public information, but some
tracks get played more frequently than others. If you play the playlist
during a ride one day, then ride the next day, chances are extremely
high that you'll hear a lot of the same songs again.

This is annoying to me.

I want all of my jams, and I want them to not repeat until I have had
the auditory satisfaction of enjoying each and every one.

This script allows you to copy an existing playlist after randomizing
the tracks. You can then play with shuffle _turned off_ and get the
equivalent of what you actually wanted.

![Playlists](https://github.com/sheagcraig/actually_random/blob/master/screenshots/playlists.png)
Playlist selection view.
![Playlist](https://github.com/sheagcraig/actually_random/blob/master/screenshots/playlist.png)
Playlist shuffle view.

## Setting it Up
Git clone the project and get into that beautiful new directory.

This project is in Python 3, so you'll need that.

1. From the Actually Random directory, you can do `pyvenv venv` to create a
virtual environment.
2. Next, `source venv/bin/activate` to make the virtual env active.
3. `pip install -r requirements.txt` to grab all of the dependencies.
4. Register your application with Spotify. You'll need to visit
   developer.spotify.com to register your app. After writing an Application
   Name and Description, you will be provided with a `ClientID` and
   `ClientSecret` which you will need to configure the app in a couple steps.
5. Add a Redirect URI to `http://127.0.0.1:8080/playlists`, and make sure you
   `ADD` and then `SAVE`!
6. `cp config_example.json config.json` to copy the example config file.
7. Edit the config.json file and add your `ClientSecret` and `ClientID` values.
8. `python actually_random.py` to run the application.
9. Open a web browser to http://127.0.0.1:8080 and you should be redirected to
   Spotify's login page, listing the access you are providing.

## What _Is_ This?
This project is a quick Flask app. It uses the flask-bootstrap and
flask-wtforms plugins, as well as the Spotipy API wrapper for Spotify.

Bootstrap provides styling, and WTForms handles form validation.
