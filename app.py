import os
from flask import Flask, session, request, redirect, render_template
from flask_session import Session
import spotipy
import uuid
import collections

# Constants
CLIENT_ID = "ce42fe948f4e49a380028f15c79b5cda"
CLIENT_SECRET = "c602ae563d904059a9addd7ef07e9372"
MAX_QUERY_SIZE = 50
CACHES_FOLDER = './.spotify_caches/'

os.environ['SPOTIPY_CLIENT_ID'] = CLIENT_ID
os.environ['SPOTIPY_CLIENT_SECRET'] = CLIENT_SECRET
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://127.0.0.1:8080'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

if not os.path.exists(CACHES_FOLDER):
    os.makedirs(CACHES_FOLDER)

def session_cache_path():
    return CACHES_FOLDER + session.get('uuid')

@app.route('/')
def index():

    # Set session uuid
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    # Authenticate to spotify
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='playlist-modify-public',
                                                cache_handler=cache_handler,
                                                show_dialog=True,
                                                open_browser=True)

    if request.args.get("code"):
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)

    return render_template('index.html')

@app.route('/result')
def result():
    depth = int(request.args.get("depth"))
    length = int(request.args.get("length"))

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)

    # Search for breakdowns playlists
    playlists = []
    songs = []
    for index in range(0, depth, MAX_QUERY_SIZE):
        result = spotify.search(q='breakdowns', type='playlist', limit=MAX_QUERY_SIZE, offset=index)
        for playlist in result['playlists']['items']:
            playlist_id = playlist['id']
            if playlist_id in playlists:
                continue

            # Gather songs
            for track in spotify.playlist_tracks(playlist_id)['items']:

                # False positive?
                if not track['track']:
                    continue

                songs.append(track['track']['id'])
            playlists.append(playlist['id'])

    # Create a playlist
    current_user = spotify.current_user()['id']
    playlist = spotify.user_playlist_create(current_user, "HEAVY BREAKS")

    # Add popular songs to playlist
    songs_left = length
    for song, _ in collections.Counter(songs).most_common():
        try:
            if songs_left:
                spotify.playlist_add_items(playlist['id'], [song])
            else:
                break
        except:
            pass
        songs_left -= 1

    # Sign Out
    try:
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    return redirect(playlist['external_urls']['spotify'])

if __name__ == '__main__':
    app.run(threaded=True, port=80)
