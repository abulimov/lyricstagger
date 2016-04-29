"""init helpers"""
from . wikia import Wikia
from . darklyrics import DarkLyrics
__all__ = ['wikia', 'darklyrics']
HELPERS = [Wikia(), DarkLyrics()]
