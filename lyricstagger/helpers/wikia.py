"""
Helper to download lyrics from lyrics.wikia.com
"""
from __future__ import unicode_literals
import re
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import lyricstagger.log as log


class Wikia:
    """Lyrics Downloader for lyrics.wikia.com"""
    url = "http://lyrics.wikia.com/api.php"

    def __init__(self):
        pass

    @staticmethod
    def parse(text, gracenote):
        """Parse lyrics from html"""
        # parse the result
        soup = BeautifulSoup(text)
        lyricbox = soup.find('div', "lyricbox")
        if lyricbox is None:
            log.debug("BeautifulSoup doesn't find content")
            return None

        if gracenote:
            # gracenote lyrics are in a separate paragraph
            lyricbox = lyricbox.find('p')

        lyrics = ''
        for content in lyricbox.contents:
            if type(content) == NavigableString:
                lyrics += content.strip()
            elif type(content) == Tag:
                if (content.string and content.name == "b" and
                        content.string.startswith("Instrumental")):
                    return '{{Instrumental}}'
                elif content.name == "br":
                    lyrics += '\n'
                if content.name not in ['script'] and content.string:
                    lyrics += content.string.strip()
        return lyrics.strip()

    @staticmethod
    def get_raw_data(artist, song):
        """Download html with lyrics, return None or tuple (text, gracenote)"""
        if not artist or not song:
            return None  # wikia needs both informations
        payload = {'artist': artist, 'song': song, 'fmt': "json"}
        result = requests.get(Wikia.url, params=payload)
        if result.status_code != 200:
            return None

        # The api returns a pseudo json object, that contains a url.
        match = re.search("'url':'([^']+)'", result.text)
        if match is None:
            return None

        html_url = match.group(1)
        log.debug('fetch url %s', html_url)
        if 'action=edit' in html_url:
            log.debug("no lyrics found")
            return None

        result = requests.get(html_url)
        gracenote = False

        if result.status_code != 200:
            # try it also with Gracenote: (e.g. Glen Hansard - High Hope)
            html_url = html_url[:9] + \
                html_url[9:].replace('/', '/Gracenote:', 1)
            log.debug('fetch url %s', html_url)
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
