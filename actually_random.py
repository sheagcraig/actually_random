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

"""Spotify's "shuffle" play feature is not really random. The algorithm
is not public information, but some tracks get played more frequently
than others. This script allows you to copy an existing playlist after
randomizing the tracks. You can then play without shuffle and get the
equivalent of what you actually want.
"""

import base64
import json
import os
import urllib

from flask import Flask, request, redirect, g, render_template
import requests
import spotipy
from spotipy import util


app = Flask(__name__)

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()


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
    prefs = get_prefs()
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        prefs["ClientID"], prefs["ClientSecret"], REDIRECT_URI,
        scope="user-library-read")
    return redirect(sp_oauth.get_authorize_url())


@app.route("/callback/q")
def callback():
    prefs = get_prefs()
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }
    base64encoded = base64.b64encode("{}:{}".format(prefs["ClientID"],
                                                    prefs["ClientSecret"]))
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload,
                                 headers=headers)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    sp = spotipy.Spotify(access_token)
    user_id = sp.current_user()["id"]
    # TODO: Grab a playlist id...
    results = sp.user_playlist(user_id, "5lKq6aIb91EFzmzmrfeVV3")

    tracks = results["tracks"]
    track_names = [track["track"]["name"] for track in tracks["items"]]
    while tracks["next"]:
        tracks = sp.next(tracks)
        track_names.extend([track["track"]["name"] for track in
                            tracks["items"]])

    return render_template("index.html", sorted_array=track_names)


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
