import os
import sys
import requests
from types import NoneType
from pprint import pprint
import time
from datetime import datetime
from PIL import Image
from io import BytesIO
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import spotipy
from pixoo import Channel, ImageResampleMode, Pixoo
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import threading
from dotenv import load_dotenv

load_dotenv()

ipAdd = os.getenv('PIXOO64_IP_ADDRESS')
clID = os.getenv('SPOTIFY_CLIENT_ID')
rURI = os.getenv('SPOTIFY_CLIENT_URI')
clSEC = os.getenv('SPOTIFY_CLIENT_SECRET')

scope = "user-read-playback-state"

pixoo = Pixoo(ipAdd, 64, False)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

# Flag to indicate whether the clock should be displayed
show_clock = False


def get_spotify_client():
    """Create and return a Spotify client."""
    return spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=clID, client_secret=clSEC, redirect_uri=rURI, scope=scope))


def get_current_track_image(sp):
    """Get the current track's image from Spotify."""
    try:
        play_tr = sp.current_playback()
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 401:
            logging.error("Access token expired. Re-authenticating...")
            sp = get_spotify_client()
            play_tr = sp.current_playback()
        else:
            raise

    if play_tr is None:
        return None, None

    track_id = play_tr["item"]["id"]
    img_url = play_tr["item"]["album"]["images"][2]["url"]
    response = http.get(img_url, timeout=10)  # Set timeout to 10 seconds
    img = Image.open(BytesIO(response.content))

    return track_id, img


def is_playing(sp):
    """Check if a track is currently playing."""
    try:
        play_tr = sp.current_playback()
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 401:
            logging.error("Access token expired. Re-authenticating...")
            sp = get_spotify_client()
            play_tr = sp.current_playback()
        else:
            raise

    if play_tr is None or not play_tr['is_playing']:
        return False

    return True


def is_podcast(sp):
    """Check if the current playback is a podcast episode."""
    try:
        play_tr = sp.current_playback()
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 401:
            logging.error("Access token expired. Re-authenticating...")
            sp = get_spotify_client()
            play_tr = sp.current_playback()
        else:
            raise

    if play_tr is None:
        return False

    return play_tr["currently_playing_type"] == "episode"


def add_clock_to_artwork():
    """Add a clock to the artwork displayed on the Pixoo."""
    while True:
        if show_clock:
            pixoo.draw_filled_rectangle((44, 56), (62, 62), (51, 51, 51))
            pixoo.draw_pixel((53, 58), (255, 255, 255))
            pixoo.draw_pixel((53, 60), (255, 255, 255))

            now = time.localtime()
            # Adjust for local timezone (UTC-5 or UTC-4 during daylight saving time)
            local_time = time.localtime(time.mktime(now) - 5 * 3600)  # Adjust as needed for daylight saving time
            currtimeh = time.strftime("%I", local_time)  # 12-hour format
            currtimem = time.strftime("%M", local_time)
            am_pm = time.strftime("%p", local_time)  # AM/PM indicator
            pixoo.draw_text(currtimeh, (45, 57), (255, 255, 255))
            pixoo.draw_text(currtimem, (55, 57), (255, 255, 255))
            pixoo.draw_text(am_pm, (65, 57), (255, 255, 255))

            pixoo.push()
        time.sleep(10)


def clear_pixoo():
    """Clear the Pixoo display."""
    pixoo.set_channel(Channel.FACES)
    pixoo.set_clock(0)


def main():
    """Main function to run the Pixoo Spotify integration."""
    global show_clock
    podcast_img = "Podcast.png"

    sp = get_spotify_client()
    current_track_id = None

    # Start the time update thread
    time_thread = threading.Thread(target=add_clock_to_artwork)
    time_thread.daemon = True
    time_thread.start()

    while True:
        if not is_playing(sp):
            show_clock = False
            clear_pixoo()
            time.sleep(10)  # Sleep to avoid rapid re-calling of clear_pixoo
        else:
            show_clock = True
            if is_podcast(sp):
                pixoo.draw_image(podcast_img)
            else:
                track_id, img = get_current_track_image(sp)
                if track_id is None:
                    clear_pixoo()
                elif track_id != current_track_id:
                    current_track_id = track_id
                    pixoo.draw_image(img)

        time.sleep(2)


if __name__ == "__main__":
    main()