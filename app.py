from flask import Flask, render_template, redirect, request
from dotenv import load_dotenv
import requests
import urllib
import os


app = Flask(__name__)


def get_spotify_access_token():
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    token_response = requests.post(
        url="https://accounts.spotify.com/api/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
    )
    token_response.raise_for_status()

    return token_response.json()["access_token"]


def get_spotify_artist(id):
    token = get_spotify_access_token()
    
    response = requests.get(
        url=f"https://api.spotify.com/v1/artists/{id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()
    
    return response.json()


@app.route("/")
def main():
    artist_json = get_spotify_artist(id="4Z8W4fKeB5YxbusRsdQVPb")
    print(f"{request.host}")
    return render_template('index.html', image_path=artist_json["images"][1]["url"])

@app.route("/brat")
def brat():
    token = get_spotify_access_token()
    response = requests.get(
        url='https://api.spotify.com/v1/albums/2lIZef4lzdvZkiiCzvPKj7',
        headers={"Authorization": f"Bearer {token}"},
    )
    album_json = response.json()

    return album_json

@app.route("/login")
def login():
    url = "https://accounts.spotify.com/authorize"
    params = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
        "scope": "user-read-private user-read-email",
        "redirect_uri": f"http://{request.host}/spotify-callback",
        # TODO: "state": This provides protection against attacks such as cross-site request forgery. See RFC-6749.
    })
    print(f"{request.host}/spotify-callback")
    return redirect(f"{url}?{params}")


@app.route('/spotify-callback')
def spotify_callback():
    return 'Welcome to Spotify API!'


if __name__ == "__main__":
    load_dotenv(override=True)
    
    app.run(host="127.0.0.1", port=8080, debug=True)