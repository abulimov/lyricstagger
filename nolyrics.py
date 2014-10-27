#!/usr/bin/env python3
"""
Find tracks without lyrics
"""
from mutagen.oggvorbis import OggVorbis
from lyrics_tagger import get_file_list
import sys


def main():
    """Main function"""
    path = sys.argv[1]

    for filepath in get_file_list(path):
        audio = OggVorbis(filepath)
        if not 'lyrics' in audio:
            print("No lyrics in file '%s'" % filepath)

if __name__ == '__main__':
    main()
