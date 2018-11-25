import sys
import os
from tinytag import TinyTag, TinyTagException
from itertools import groupby
import time


def get_mp3_collection(dir):
    mp3_collection = []
    for path, dirs, filenames in os.walk(dir):
        for filename in filenames:
            fileext = os.path.splitext(filename)[1]
            if fileext == '.mp3':
                track_filepath = os.path.abspath(os.path.join(path, filename))
                try:
                    tags = TinyTag.get(track_filepath)
                except TinyTagException:
                    pass
                mp3_collection.append([track_filepath, tags])
    return mp3_collection


def get_artist_tracks(mp3_collection, artist):
    mp3_artist_collection = []
    for filepath, tags in mp3_collection:
        if tags and tags.artist and (artist in tags.artist.lower()):
            mp3_artist_collection.append([filepath, tags])
    return sorted(
        mp3_artist_collection,
        key=lambda x: '{}{}'.format(x[1].year, x[1].album)
    )


def get_artist_group_tracks(mp3_artist_collection):
    tracks_by_albums = []
    for key, group in groupby(
            mp3_artist_collection,
            key=lambda x: '{},{},{}'.format(x[1].album, x[1].year, x[1].artist)):
        tracks_of_the_album = []
        for filepath, tags in group:
            duration_min_sec = time.strftime('%M:%S', time.gmtime(tags.duration))
            filepath_abs = os.path.abspath(filepath)
            tracks_of_the_album.append({
                'title': tags.title,
                'duration': duration_min_sec,
                'filepath': filepath_abs
            })
        key = key.split(',')
        tracks_by_albums.append({
            'artist': key[2],
            'album': key[0],
            'year': key[1],
            'tracks': tracks_of_the_album
        })
    return tracks_by_albums


if __name__ == '__main__':
    try:
        artist_name = sys.argv[1]
    except IndexError:
        exit('Please enter an artist name')
    else:
        path = 'music'
        mp3_collection = get_mp3_collection(path)
        mp3_artist_collection = get_artist_tracks(mp3_collection, artist_name)
        tracks_by_albums = get_artist_group_tracks(mp3_artist_collection)
        print(tracks_by_albums)
        for album in tracks_by_albums:
            print('ARTIST: {artist}\nALBUM: {album} {year}'.format(**album))
            for num, track in enumerate(album['tracks'], 1):
                print('{}. "{title}" {duration} ({filepath})'.format(num, **track))
            print('\n')
