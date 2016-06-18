## v1.1.0 [unreleased]

- Moved to asyncio for concurrency
- Dropped python<3.5 support
- Added new version check
- Removed mock dependency
- Simplified engine logic

## v1.0.2 [2016-05-04]

- Fixed DarkLyrics stripping for last song text

## v1.0.1 [2016-05-04]

- Fixed DarkLyrics search (made it case-insensitive)

## v1.0.0 [2016-05-04]

- Dropped python2 and pypy support
- Rewritten with python3 type annotations
- Simplified DarkLyrics helper caching logic

## v0.9.1 [2016-04-29]

- Added caching in DarkLyrics helper

## v0.9.0 [2016-04-28]

- Added DarkLyrics helper
- Added multithreaded tagging
- Added ability to overwrite existing lyrics

## v0.8.4 [2015-11-22]

- Fixed click and BeautifulSoup4 warnings
- Updated wikia helper to support small change in lyrics.wikia.com API
- removed python 3.2 support, added python3.5 support

## v0.8.3 [2015-07-22]

- Fixed debug logging with python2

## v0.8.2 [2015-07-05]

- Fixed operations statistics with python2

## v0.8.1 [2015-06-26]

- Improved output for all operations and summary
- Simplified console module

## v0.8.0 [2015-06-21]

- Added changelog
- Switched to click library for opt parsing and output
- Improved output for report
- Added operation progress
