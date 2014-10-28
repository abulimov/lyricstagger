"""
Helper to download lyrics from lyrics.wikia.com
"""
import re
import requests
import urllib
from bs4 import BeautifulSoup, NavigableString
import logging


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

    @staticmethod
    def fetch(artist, song, _):
        """Fetch lyrics from remote url"""
        data = Wikia.get_raw_data(artist, song)
        if data:
            return Wikia.parse(data[0], data[1])
        return None
