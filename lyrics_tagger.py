#!/usr/bin/env python3
"""
Walks over filesystem and downloads lyrics for each found
music file without lyrics tag. Then adds this lyrics as a tag to this file.
"""
from mutagen.oggvorbis import OggVorbis
import re
import sys
import requests
import urllib
import os
import logging
from bs4 import BeautifulSoup, NavigableString

#set up logging
if 'DEBUG' in os.environ:
    LOGGING_LEVEL = logging.DEBUG
else:
    LOGGING_LEVEL = logging.WARNING

logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]#\
        %(levelname)-8s [%(asctime)s]  %(message)s', level=LOGGING_LEVEL)


def fetch(artist, song, album):
    """Fetch lyrics with different helpers"""
    helpers = [Wikia()]
    for helper in helpers:
        try:
            lyrics = helper.fetch(artist, song, album)
        except ConnectionError as error:
            lyrics = None
            logging.warning('Connection error: %s', error)
        if lyrics:
            break
    return lyrics


class Wikia:
    """Lyrics Downloader for lyrics.wikia.com"""
    url = "http://lyrics.wikia.com/api.php?artist=%s&song=%s&fmt=json"

    def __init__(self):
        pass

    @staticmethod
    def parse(text, gracenote):
        """Parse lyrics from html"""
        # parse the result
        soup = BeautifulSoup(text)
        lyricbox = soup.find('div', "lyricbox")
        if lyricbox is None:
            logging.debug("BeautifulSoup doesn't find content")
            return None

        if gracenote:
            # gracenote lyrics are in a separate paragraph
            lyricbox = lyricbox.find('p')

        lyrics = ''
        for content in lyricbox.contents:
            text = str(content).strip()
            if type(content) == NavigableString:
                lyrics += text.strip()
            elif text.startswith('<b>Instrumental</b>'):
                return '{{Instrumental}}'
            elif text.startswith('<br'):
                lyrics += '\n'
        return lyrics.strip()

    @staticmethod
    def get_raw_data(artist, song):
        """Download html with lyrics, return None or tuple (text, gracenote)"""
        if not artist or not song:
            return None  # wikia needs both informations
        artist_encoded = urllib.parse.quote_plus(artist)
        song_encoded = urllib.parse.quote_plus(song)
        result = requests.get(Wikia.url % (artist_encoded, song_encoded))
        if result.status_code != 200:
            return None

        # The api returns a pseudo json object, that contains a url.
        match = re.search("'url':'([^']+)'", result.text)
        if match is None:
            return None

        html_url = match.group(1)
        logging.debug('fetch url %s', html_url)
        if 'action=edit' in html_url:
            logging.debug("no lyrics found")
            return None

        result = requests.get(html_url)
        gracenote = False

        if result.status_code != 200:
            # try it also with Gracenote: (e.g. Glen Hansard - High Hope)
            html_url = html_url[:9] + \
                html_url[9:].replace('/', '/Gracenote:', 1)
            logging.debug('fetch url %s', html_url)
            result = requests.get(html_url)
            gracenote = True
            if result.status_code != 200:
                return None
        return (result.text, gracenote)

    def fetch(self, artist, song, _):
        """Fetch lyrics from remote url"""
        data = self.get_raw_data(artist, song)
        if data:
            return self.parse(data(0), data(1))
        return None


def get_file_list(path):
    """Generator of file pathes in directory"""
    for root, _, files in os.walk(path):
        for each in files:
            _, ext = os.path.splitext(each)
            if ext.lower() == ".ogg":
                filepath = os.path.join(root, each)
                yield filepath


def get_tags(audio):
    """Get tags from audio class"""
    data = dict()
    for tag in ['artist', 'album', 'title']:
        if tag in audio:
            if isinstance(audio[tag], list):
                data[tag] = audio[tag][0]
            else:
                data[tag] = audio[tag]
        else:
            logging.info("Failed to find tag %s", tag)
            return None
    return data


def main():
    """Main function"""
    path = sys.argv[1]

    for file_path in get_file_list(path):
        logging.debug("processing file %s", file_path)
        audio = OggVorbis(file_path)
        data = get_tags(audio)
        if data and not 'lyrics' in audio:
            lyrics = fetch(data['artist'], data['title'], data['album'])
            if lyrics:
                logging.debug("writing LYRICS tag to file '%s'", file_path)
                audio["LYRICS"] = lyrics
                audio.save()
            else:
                logging.debug("no lyrics found for file '%s'", file_path)

if __name__ == '__main__':
    main()
