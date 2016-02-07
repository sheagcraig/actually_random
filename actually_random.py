#!/usr/bin/env python
# Copyright (C) 2016 Shea G Craig
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""I like to rip mountain bike trails to my giant Spotify playlist,
"Bottomless Happiness". Unfortunately, Spotify's "shuffle" play feature
is not really random. The algorithm is not public information, but some
tracks get played more frequently than others. If you play the playlist
during a ride one day, then ride the next day, chances are extremely
high that you'll hear a lot of the same songs again.

This is annoying to me.

I want all of my jams, and I want them to not repeat until I have had
the auditory satisfaction of enjoying each and every one.

This script allows you to copy an existing playlist after randomizing
the tracks. You can then play without shuffle and get the equivalent of
what you actually wanted.
"""

import base64
import copy
import json
import random
import urllib

from flask import (Flask, request, redirect, g, render_template, url_for,
                   session, flash)
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required, NoneOf

import requests
import spotipy
from spotipy import util


app = Flask(__name__)
bootstrap = Bootstrap(app)

# Flask Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
REDIRECT_URI = "{}:{}/playlists".format(CLIENT_SIDE_URL, PORT)
SCOPE = ("playlist-modify-public playlist-modify-private "
         "playlist-read-collaborative playlist-read-private")


def get_oauth():
    prefs = get_prefs()
    return spotipy.oauth2.SpotifyOAuth(
        prefs["ClientID"], prefs["ClientSecret"], REDIRECT_URI, scope=SCOPE,
        cache_path=".tokens")


def get_spotify():
    oauth = get_oauth()
    token_info = oauth.get_cached_token()
    return spotipy.Spotify(token_info["access_token"])


def get_prefs():
    """Get application prefs plist and set secret key.

    Args:
        path: String path to a plist file.
    """
    with open("config.json") as prefs_file:
        prefs = json.load(prefs_file)
    app.secret_key = prefs["SecretKey"]

    return prefs


def finish_auth(auth_token):
    sp_oauth = get_oauth()
    response_data = sp_oauth.get_access_token(auth_token)


@app.route("/")
def index():
    # TODO: Probably should add a Login page?
    sp_oauth = get_oauth()
    return redirect(sp_oauth.get_authorize_url())


@app.route("/playlists")
def playlists():
    finish_auth(request.args["code"])
    spotify = get_spotify()
    user_id = spotify.current_user()["id"]
    results = spotify.user_playlists(user_id)

    playlists = results["items"]
    playlist_names = get_user_playlists()
    session["playlist_names"] = [item["name"] for item in playlist_names]

    return render_template("playlists.html", sorted_array=playlist_names)


@app.route("/playlist/<playlist_id>", methods=["GET", "POST"])
def view_playlist(playlist_id):
    """Shuffle a playlist and allow user to save to a new playlist."""

    class PlaylistNameForm(Form):
        """Form for getting new playlist name.

        Will not accept existing playlist names.
        """
        name = StringField("Playlist Name", validators=[
            Required(), NoneOf(session["playlist_names"],
                               message="That name is already in use!")])
        submit = SubmitField("Save")

    form = PlaylistNameForm()

    spotify = get_spotify()
    user_id = spotify.current_user()["id"]
    results = spotify.user_playlist(user_id, playlist_id)

    tracks = results["tracks"]
    track_info = tracks["items"]
    # Spotify returns results in a pager; get next results if more than
    # 100 returned.
    while tracks["next"]:
        tracks = spotify.next(tracks)
        track_info.extend(tracks["items"])

    track_names = [(track["track"]["name"], track["track"]["id"]) for track
                    in track_info]

    if "Shuffle" in request.form:
        return redirect(url_for("view_playlist", playlist_id=playlist_id))
    elif form.validate_on_submit():
        # If the playlist form is valid, save the new playlist and
        # redirect to playlists page.
        new_playlist_name = form.name.data
        # TODO: We need to get the private/public status of the playlist
        # to copy to the new one.
        spotify.user_playlist_create(user_id, new_playlist_name, public=results["public"])
        new_playlist_id = get_playlist_id_by_name(new_playlist_name)
        # You can add up to 100 tracks per request.
        all_tracks = [track_names[item][1] for item in session["shuffled"]]
        for tracks in get_tracks_for_add(all_tracks):
            spotify.user_playlist_add_tracks(user_id, new_playlist_id, tracks)
        flash("Playlist '{}' saved.".format(new_playlist_name))
        return redirect(url_for("index"))

    name = session["name"] = results["name"]
    images = results["images"]
    session["shuffled"] = get_shuffle(track_names)
    shuffled_names = [track_names[index] for index in session["shuffled"]]

    return render_template(
        "playlist.html", name=name, track_names=get_names(track_names),
        shuffled_names=get_names(shuffled_names), images=images, form=form)


def get_tracks_for_add(tracks):
    index = 0
    output = []
    while index < len(tracks):
        output.append(tracks[index])
        if len(output) == 100 or index == len(tracks) - 1:
            yield output
            output = []
        index += 1


def get_shuffle(tracks):
    """Return a shuffling sequence.

    Because we can't fit large playlists into the session cookie, we
    only store a shuffling pattern, i.e. a sequence of indices.

    Args:
        tracks: An iterable.

    Returns:
        A tuple of shuffled indexes.
    """
    sequence = list(range(len(tracks)))
    random.shuffle(sequence)
    return sequence


def get_names(tracks):
    return [track[0] for track in tracks]


def get_user_playlists():
    spotify = get_spotify()
    user_id = spotify.current_user()["id"]
    results = spotify.user_playlists(user_id)

    playlists = results["items"]
    playlist_names = [{"id": playlist["id"], "name": playlist["name"],
                       "images": playlist["images"]} for playlist in playlists]
    while results["next"]:
        results = sp.next(playlists)
        playlist_names.extend([{"id": playlist["id"], "name": playlist["name"]}
                               for playlist in results])
    return playlist_names


def get_playlist_id_by_name(name):
    return [playlist["id"] for playlist in get_user_playlists() if
            playlist["name"] == name][0]


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
