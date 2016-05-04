# Lyrics Tagger

Made to automagically fill **LYRICS** tag in musical files.

Scan music files, download missing lyrics and save it into tag.

As for now, this project supports downloading lyrics from
http://lyrics.wikia.com or http://darklyrics.com and writing it into
*'.flac'*, *'.ogg'* and *'.mp3'* files.

Written in Python3 (3.3+), with heavy usage of [Type Annotations](https://www.python.org/dev/peps/pep-0484/).

Uses:
 * [mutagen](https://pypi.python.org/pypi/mutagen) to deal with tags,
 * [requests](https://pypi.python.org/pypi/requests) and
 * [beautifulsoup4](https://pypi.python.org/pypi/beautifulsoup4) to obtain lyrics,
 * [click](https://pypi.python.org/pypi/click) for cli,
 * [mock](https://pypi.python.org/pypi/mock) for test.

## Setup

Using pip

        pip install 'git+https://github.com/abulimov/lyricstagger#egg=lyricstagger'

## Usage

Show music files without lyrics

        user@machine:~$ lyricstagger report ~/Music
        No lyrics in file '/home/user/Music/Some Artist/01 - Some Track.ogg'
        No lyrics in file '/home/user/Music/Some Artist/02 - Other Track.ogg'

Download lyrics and tag music files

        user@machine:~$ lyricstagger tag ~/Music

Remove all lyrics from music files

        user@machine:~$ lyricstagger remove ~/Music

Edit lyrics in file with EDITOR

        user@machine:~$ lyricstagger edit "~/Music/Some Artist/01 - Some Track.ogg"

Print lyrics from file to stdout

        user@machine:~$ lyricstagger show "~/Music/Some Artist/01 - Some Track.ogg"
        Artist: Some Artist, Title: Some Track

        There goes lyrics

## Debug

Setting environment variable DEBUG enabled debugging

## Running tests

Just run

        user@machine:~$ cd lyricstagger
        user@machine:~/lyricstagger$ python -m unittest discover test -v

## Contributing

Please read [CONTRIBUTING.md](https://github.com/abulimov/lyricstagger/blob/master/CONTRIBUTING.md) if you wish to contribute.

## License

Licensed under the [MIT License](http://opensource.org/licenses/MIT).
