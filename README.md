# HEAVY BREAKDOWNS FINDER

A simple webapp that creates a spotify playlist with the hardest hitting breakdowns.
This is my first attempt at web programming, and it is shit.
If someone ever sees this and has tips for improvement, please, send me an email

## How it works
The apps crawls Spotify using it's web API to find public playlists of songs with breakdowns, and than creates a new playlist for the user with the most common songs found.
 * The Depth parameter determines how many playlists will be indexed. (More depth = higher runtime)
 * The Length parameter determines how many songs will be in the final playlist.

## How to run this

Python package dependencies:
 * flask
 * flask_session
 * spotipy

You need to create a Spotify app in https://developer.spotify.com/dashboard and replace the CLIENT_ID and CLIENT_SECRET in app.py with ID and SECRET of your app.

Also, the SPOTIPY_REDIRECT_URI needs to be updated if you want to run it on a remote server.

Example:
```
  CLIENT_ID = "ce42fe948f4e49a380028f15c79b5cda"
  CLIENT_SECRET = "0a98d19de9944d43b4f6bb78732ea861"
  ...
  os.environ['SPOTIPY_REDIRECT_URI'] = 'http://domain.com'
```

run with:

    $ python3 app.py
