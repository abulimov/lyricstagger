#!/usr/bin/env python3
"""
Find tracks without lyrics
"""
from lyrics_tagger.misc import get_file_list, get_audio
import sys


def main():
    """Main function"""
    path = sys.argv[1]

    for filepath in get_file_list(path):
        audio = get_audio(filepath)
        if audio and not 'lyrics' in audio:
            print("No lyrics in file '%s'" % filepath)

if __name__ == '__main__':
    main()
