"""
Actions with musical files
"""

import click
import lyricstagger.log as log
import lyricstagger.misc as misc


def tag(logger: log.CliLogger, filepath: str, overwrite: bool = False) -> None:
    """Try to tag lyrics for given file"""
    audio = misc.get_audio(filepath)
    data = misc.get_tags(audio)
    # we cannot find lyrics if we don't have tags
    if data:
        if overwrite or "lyrics" not in data:
            lyrics = misc.fetch(data["artist"],
                                data["title"],
                                data["album"])
            if lyrics:
                logger.log_writing(filepath)
                audio = misc.write_lyrics(audio, lyrics)
                audio.save()
            else:
                logger.log_not_found(filepath)


def tag_force(logger: log.CliLogger, filepath: str) -> None:
    """Wrapper for tag action setting overwrite to true"""
    tag(logger, filepath, overwrite=True)


def remove(logger: log.CliLogger, filepath: str) -> None:
    """Remove given file"""
    audio = misc.get_audio(filepath)
    logger.log_removing(filepath)
    misc.remove_lyrics(audio)
    audio.save()


def edit(logger, filepath):
    """Edit given file's lyrics with EDITOR"""
    audio = misc.get_audio(filepath)
    lyrics = misc.edit_lyrics(audio)
    if lyrics:
        logger.log_writing(filepath)
        audio = misc.write_lyrics(audio, lyrics)
        audio.save()
    else:
        logger.log_no_lyrics_saved(filepath)


def show(logger, filepath):
    """Pretty print lyrics from given file"""
    audio = misc.get_audio(filepath)
    data = misc.get_tags(audio)
    if data and "lyrics" in data:
        click.secho("%s" % click.format_filename(filepath), fg="blue")
        click.secho("Artist: %s, Title: %s" % (data["artist"],
                                               data["title"]),
                    fg="blue")
        click.echo()
        click.echo(data["lyrics"])
        click.echo()
    else:
        logger.log_not_found(filepath)
        click.secho("No lyrics in file '%s'" % filepath, fg="red")


def report(logger, filepath):
    """Show lyrics presence in given file"""
    audio = misc.get_audio(filepath)
    data = misc.get_tags(audio)
    if data and 'lyrics' not in data:
        logger.log_not_found(filepath)
        click.secho("no lyrics:    ", nl=False, fg="red")
    else:
        click.secho("lyrics found: ", nl=False, fg="green")
    click.echo("%s" % click.format_filename(filepath))
