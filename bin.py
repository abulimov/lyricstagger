#!/usr/bin/env python3
"""
Walks over filesystem and downloads lyrics for each found
music file without lyrics tag. Then adds this lyrics as a tag to this file.
"""
import sys
import lyrics_tagger.debug as debug
import lyrics_tagger.misc as misc


def main():
    """Main function"""
    path = sys.argv[1]

    for file_path in misc.get_file_list(path):
        debug.debug("processing file %s", file_path)
        audio = misc.get_audio(file_path)
        data = misc.get_tags(audio)
        if data and not 'lyrics' in audio:
            lyrics = misc.fetch(data['artist'], data['title'], data['album'])
            if lyrics:
                debug.debug("writing LYRICS tag to file '%s'", file_path)
                audio["LYRICS"] = lyrics
                audio.save()
            else:
                debug.debug("no lyrics found for file '%s'", file_path)

if __name__ == '__main__':
    main()
