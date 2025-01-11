from flask import Flask, render_template, redirect, request, url_for
from dotenv import load_dotenv
import flask_login
import requests
import urllib
import os


app = Flask(__name__)
app.secret_key = "gdauhaj"  # random temporary password

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(flask_login.UserMixin):
    def __init__(self, token, id):
        self.token = token
        self.id = id


@login_manager.user_loader
def user_loader(id):
    return users.get(id)
users = {}

@app.route("/user-profile")
@flask_login.login_required
def user_profile():
    user = flask_login.current_user
    print(user)
    print(user.token)
    display_name = get_user_profile(user)
    return f"Your display name is {display_name}" # Fill in later

@app.route("/logout")
def logout():
    flask_login.logout_user()
    return "Logged out"

def get_user_profile(user):
    response = requests.get(
        url = "https://api.spotify.com/v1/me",
        headers = {f"Authorization: Bearer {user.token}"}
    )
    response.raise_for_status()

    return response.json()["display_name"]


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

@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/brat")
def brat():
    token = get_spotify_access_token()
    response = requests.get(
        url='https://api.spotify.com/v1/albums/2lIZef4lzdvZkiiCzvPKj7',
        headers={"Authorization": f"Bearer {token}"},
    )
    album_json = response.json()

    return album_json

@app.route("/club-classics")
def clubclassics():
    token = get_spotify_access_token()
    response = requests.get(
        url='https://api.spotify.com/v1/tracks/7BoOmRrtNCbIT9yQ4xidk5',
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
    token = request.args.get('code')
    user = User(token, "person")
    users["person"] = user
    flask_login.login_user(user)
    return redirect(url_for("user_profile"))

if __name__ == "__main__":
    load_dotenv(override=True)
    
    app.run(host="127.0.0.1", port=8080, debug=True)