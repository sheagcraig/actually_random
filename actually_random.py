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
import json
import urllib

from flask import Flask, request, redirect, g, render_template
import requests
import spotipy
from spotipy import util


app = Flask(__name__)

# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private"


class AccessToken(object):
    """Stores a Spotify access token."""
    _access_token = None

    @property
    @classmethod
    def access_token(cls):
        return cls._access_token

    @access_token.setter
    @classmethod
    def access_token(cls, access_token):
        cls._access_token = access_token


def get_oauth():
    prefs = get_prefs()
    return spotipy.oauth2.SpotifyOAuth(
        prefs["ClientID"], prefs["ClientSecret"], REDIRECT_URI, scope=SCOPE,
        cache_path=".tokens")


def get_prefs():
    """Get application prefs plist.

    Args:
        path: String path to a plist file.
    """
    with open("config.json") as prefs_file:
        prefs = json.load(prefs_file)

    return prefs


@app.route("/")
def index():
    sp_oauth = get_oauth()
    return redirect(sp_oauth.get_authorize_url())


@app.route("/playlist/<playlist_id>")
def tracks(playlist_id):
    # TODO: Probably need to use the refresh token here.
    sp = spotipy.Spotify(AccessToken.access_token)
    user_id = sp.current_user()["id"]
    # TODO: Grab a playlist id...
    results = sp.user_playlist(user_id, playlist_id)

    tracks = results["tracks"]
    track_names = [track["track"]["name"] for track in tracks["items"]]
    while tracks["next"]:
        tracks = sp.next(tracks)
        track_names.extend([track["track"]["name"] for track in
                            tracks["items"]])

    return render_template("playlist.html", name=results["name"],
                           sorted_array=track_names)


@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']

    # # Auth Step 5: Tokens are Returned to Application
    sp_oauth = get_oauth()
    response_data = sp_oauth.get_access_token(auth_token)

    AccessToken.access_token = response_data["access_token"]
    spotify = spotipy.Spotify(AccessToken.access_token)
    user_id = spotify.current_user()["id"]
    results = spotify.user_playlists(user_id)

    playlists = results["items"]
    playlist_names = [{"id": playlist["id"], "name": playlist["name"]} for
                      playlist in playlists]
    while results["next"]:
        results = sp.next(playlists)
        playlist_names.extend([{"id": playlist["id"], "name": playlist["name"]}
                               for playlist in results])

    return render_template("playlists.html", sorted_array=playlist_names)


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
