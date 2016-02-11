# Actually Random

## Introduction
I like to rip mountain bike trails to my giant Spotify playlist, "Bottomless
Happiness". Unfortunately, Spotify's "shuffle" play feature is not really
random. The algorithm is not public information, but some tracks get played
more frequently than others, probably based on the popularity of a track. 

At times, you will even hear the same track twice during one extended ride. I
have about 500 songs on this playlist, with a length of 24 hours and 29
minutes, and yet I somehow manage to hear "Running With the Devil" every damn
time.

Further, the play queue is deleted after some session timeout or the app is
shutdown, so that if you ride two days in a row, you'll probably hear a lot of
the same songs that you heard the previous day.

This is annoying to me.

I want all of my jams, and I want them to not repeat until I have had
the auditory satisfaction of enjoying each and every one.

As a quick practice project in Flask, I wrote Actually Random to allow you to
select a playlist, shuffle it up, and then save it with a new name.  

Then, when you go out to ride or run or whatever, play the new playlist without
using the shuffle feature.

### Playlist selection view.
![Playlists](https://github.com/sheagcraig/actually_random/blob/master/screenshots/playlists.png)
### Playlist shuffle view.
![Playlist](https://github.com/sheagcraig/actually_random/blob/master/screenshots/playlist.png)

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

### Diamond Dave
![Diamond Dave](https://github.com/sheagcraig/actually_random/blob/master/screenshots/flying.gif)
