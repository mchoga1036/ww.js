import sys
from bs4 import BeautifulSoup
from ytmusicapi import YTMusic
import os
import json
import requests

oauth = f"{os.getcwd()}/oauth.json"
# yt = YTMusic(oauth)
yt = YTMusic()
import urllib
import os
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, TCOM, TCON, TDRC, TRCK, APIC
from mutagen.easyid3 import EasyID3

from pytubefix import Search


def get_songs_metadata(song):
    results = []

    try:

        count = 0
        song_results = yt.search(song, filter="songs")
        video_results = yt.search(song, filter="videos")
        for song in song_results:
            if count < 2:
                artist = "".join([c for c in song['artists'][0]['name'] if c not in ['[', ']']])
                title = "".join([c for c in song['title'] if c not in ['[', ']']])
                results.append(
                    {"artist": artist, "title": title, "video_id": song['videoId'], "album_id": song["album"]["id"]})

                count += 1
            else:
                break

        if len(video_results) > 0:
            results.append({"artist": video_results[0]['artists'][0]['name'], "title": video_results[0]['title'],
                            "video_id": video_results[0]['videoId']})

        return results

    except Exception as e:
        print(f"An error occurred: {e}")
        # return None
        return []


def get_song_metadata(song):
    # yt.title = "".join([c for c in yt.title if c not in ['/', '\\', '|', '?', '*', ':', '>', '<', '"']])

    try:
        results = yt.search(song, filter="songs")
        title = results[0]['title']
        album_name = results[0]['album']['name']
        artist = results[0]['artists'][0]['name']

        video_id = results[0]['videoId']
        album = yt.get_album(results[0]["album"]["id"])
        year = album["year"]
        url = album['thumbnails'][-1]['url']

        return {"title": title, "album_name": album_name, "artist": artist, "year": year, "video_id": video_id,
                "url": url}

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_albums_metadata(album):
    albums = []

    results = yt.search(album, filter="albums")

    count = 0

    # for x in results:
    for x in results:
        # print(x)

        if count < 3:
            albums.append(
                # {"artist": x['artists'][1]['name'], "title": x['title'], "album_id": x['browseId'], "year": x['year']})
                {"artist": x['artists'][0]['name'], "title": x['title'], "album_id": x['browseId'], "year": x['year']})

            count += 1

    return albums


def get_videos_metadata(video):
    videos = []
    count = 0



    results = Search(video).fetch_and_parse()




    for index, vid in enumerate(results[0]["videos"]):

        if count < 3:



            author = "".join([c for c in vid.author if c not in ['[', ']']])
            title = "".join([c for c in vid.title if c not in ['[', ']']])
            videos.append(
                {"author": author, "title": title, "video_id": vid.video_id})

            count += 1
        else:
            break

    return videos



def lyrics(song):
    try:
        results = yt.search(song, filter="songs")

        title = results[0]['title']
        artist = results[0]['artists'][0]['name']


        album = yt.get_album(results[0]["album"]["id"])
        album_art = album['thumbnails'][-1]['url']

        video_id = results[0]['videoId']
        data = yt.get_watch_playlist(video_id)
        lyrics_id = data["lyrics"]

        lyrics = yt.get_lyrics(lyrics_id)
        result = f"*{artist} - {title}*\n\n{lyrics['lyrics']}"
        return {"album_art": album_art, "lyrics": result}

    except Exception as e:
        print(f"An error occurred: {e}")
        return None



def tagger(location, video_id, album_id=None, track_num=1):
    title = None
    artist = None
    album = None
    thumbnail = None
    year = "2024"

    if album_id is not None:

        try:

            title = yt.get_song(video_id)["videoDetails"]["title"]

            album_details = yt.get_album(album_id)
            album = album_details["title"]
            artist = album_details['artists'][0]['name']
            year = album_details["year"]
            thumbnail = album_details['thumbnails'][-1]['url']

        except Exception as e:
            print(f"An error occurred getting metadata song {title}: {e}")

    else:
        try:

            title = yt.get_song(video_id)["videoDetails"]["title"]
            album = "mchoga"
            artist = "morris"
            year = "2024"
            thumbnail = yt.get_song(video_id)["videoDetails"]["thumbnail"]["thumbnails"][-1]["url"]

        except Exception as e:
            print(f"An error occurred while getting metadata video {title}: {e}")

    try:

        mp3file = EasyID3(location)

        mp3file["albumartist"] = album
        mp3file["artist"] = artist
        mp3file["album"] = album
        mp3file["title"] = title
        mp3file["website"] = 'https://morrischoga.vercel.app'
        mp3file["tracknumber"] = str(track_num)
        mp3file.save()

        audio = ID3(location)
        audio.save(v2_version=3)

        audio = ID3(location)
        with urllib.request.urlopen(thumbnail) as albumart:
            audio["APIC"] = APIC(
                encoding=3, mime="image/jpeg", type=3, desc="Cover", data=albumart.read()
            )
        audio.save(v2_version=3)

    except Exception as e:
        print(f"An error occurred while tagging {title}: {e}")


def get_playList_and_song_metadata(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    script = soup.script.string
    json_result = json.loads(script)

    return json_result


def get_playlist(url):
    playlist = {}
    playlist_json = get_playList_and_song_metadata(url)
    playlist["playlist"] = playlist_json["name"]

    for song in range(len(playlist_json["track"])):
        song_url = playlist_json["track"][song]["url"]
        song_json = get_playList_and_song_metadata(song_url)
        artist_name = song_json["audio"]["byArtist"][0]["name"]
        song_name = song_json["audio"]["name"]

        playlist[song_name] = artist_name
        # print(f'{song} {artist_name} {song_name}')
    # return playlist_name, playlist
    return playlist
