import asyncio
import logging
from functools import wraps
from pathlib import Path

import click
import colorama
from dataclass_click import dataclass_click

from .. import __version__
from ..api.api import Librespot, SpotifyApi
from ..downloader.audio import SpotifyAudioDownloader
from ..downloader.base import SpotifyBaseDownloader
from ..downloader.downloader import SpotifyDownloader
from ..downloader.exceptions import VotifyDownloaderException, VotifyMediaFileExists
from ..downloader.video import SpotifyVideoDownloader
from ..interface.audio import SpotifyAudioInterface
from ..interface.base import SpotifyBaseInterface
from ..interface.enums import AutoMediaOption
from ..interface.episode import SpotifyEpisodeInterface
from ..interface.episode_video import SpotifyEpisodeVideoInterface
from ..interface.exceptions import (
    VotifyMediaException,
    VotifyMediaFlatFilterException,
    VotifyUrlParseException,
)
from ..interface.interface import SpotifyInterface
from ..interface.music_video import SpotifyMusicVideoInterface
from ..interface.song import SpotifySongInterface
from ..interface.video import SpotifyVideoInterface
from .cli_config import CliConfig
from .config_file import ConfigFile
from .database import Database
from .utils import CustomLoggerFormatter, prompt_path

logger = logging.getLogger(__name__)


def make_sync(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


@click.command()
@click.help_option("-h", "--help")
@click.version_option(__version__, "-v", "--version")
@dataclass_click(CliConfig)
@ConfigFile.loader
@make_sync
async def main(config: CliConfig):
    colorama.just_fix_windows_console()

    root_logger = logging.getLogger(__name__.split(".")[0])
    root_logger.setLevel(config.log_level)
    root_logger.propagate = False

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(CustomLoggerFormatter())
    root_logger.addHandler(stream_handler)

    if config.log_file:
        file_handler = logging.FileHandler(config.log_file, encoding="utf-8")
        file_handler.setFormatter(CustomLoggerFormatter(use_colors=False))
        root_logger.addHandler(file_handler)

    if config.auto_media_option == AutoMediaOption.LIKED_TRACKS:
        config.urls = ["Liked Tracks"]
    elif not config.urls:
        raise (
            click.exceptions.MissingParameter(
                param_type="argument",
                param_hint="'URLS...'",
            )
        )

    logger.info(f"Starting Votify {__version__}")

    cookies_path = prompt_path(config.cookies_path)

    if config.wvd_path:
        wvd_path = prompt_path(config.wvd_path)
    else:
        wvd_path = None

    if config.database_path:
        database = Database(config.database_path)
        flat_filter = database.flat_filter
    else:
        database = None
        flat_filter = None

    if not Librespot and not any(
        audio_quality.mp4 for audio_quality in config.audio_quality
    ):
        logger.warning(
            "Librespot is not available, "
            "Vorbis audio quality for songs will not be available"
        )

    api = await SpotifyApi.create_from_netscape_cookies(
        cookies_path,
        skip_librespot=not Librespot,
    )
    if api.anonymous_session:
        logger.critical(
            "Could not authenticate with the provided cookies, "
            "please check your cookies file and try again"
        )
        return

    base_interface = SpotifyBaseInterface(
        api=api,
        cover_size=config.cover_size,
        skip_stream_info=config.synced_lyrics_only,
        wvd_path=wvd_path,
    )
    video_interface = SpotifyVideoInterface(
        base=base_interface,
        video_format=config.video_format,
        resolution=config.video_resolution,
    )
    audio_interface = SpotifyAudioInterface(
        base=base_interface,
        audio_quality_priority=config.audio_quality,
    )
    song_interface = SpotifySongInterface(audio_interface)
    episode_interface = SpotifyEpisodeInterface(audio_interface)
    music_video_interface = SpotifyMusicVideoInterface(video_interface)
    episode_video_interface = SpotifyEpisodeVideoInterface(video_interface)
    interface = SpotifyInterface(
        base=audio_interface,
        song=song_interface,
        episode=episode_interface,
        music_video=music_video_interface,
        episode_video=episode_video_interface,
        prefer_video=config.prefer_video,
        flat_filter=flat_filter if not config.overwrite else None,
    )

    base_downloader = SpotifyBaseDownloader(
        interface=interface,
        output_path=config.output,
        temp_path=config.temp,
        aria2c_path=config.aria2c_path,
        curl_path=config.curl_path,
        ffmpeg_path=config.ffmpeg_path,
        mp4box_path=config.mp4box_path,
        mp4decrypt_path=config.mp4decrypt_path,
        shaka_packager_path=config.shaka_packager_path,
        album_folder_template=config.album_folder_template,
        compilation_folder_template=config.compilation_folder_template,
        podcast_folder_template=config.podcast_folder_template,
        no_album_folder_template=config.no_album_folder_template,
        single_disc_file_template=config.single_disc_file_template,
        multi_disc_file_template=config.multi_disc_file_template,
        podcast_file_template=config.podcast_file_template,
        no_album_file_template=config.no_album_file_template,
        playlist_file_template=config.playlist_file_template,
        date_tag_template=config.date_tag_template,
        exclude_tags=config.exclude_tags,
        truncate=config.truncate,
    )
    audio_downloader = SpotifyAudioDownloader(
        base=base_downloader,
        download_mode=config.audio_download_mode,
        remux_mode=config.audio_remux_mode,
    )
    video_downloader = SpotifyVideoDownloader(
        base=base_downloader,
        remux_mode=config.video_remux_mode,
    )
    downloader = SpotifyDownloader(
        base=base_downloader,
        audio=audio_downloader,
        video=video_downloader,
        no_synced_lyrics_file=config.no_synced_lyrics_file,
        save_playlist_file=config.save_playlist_file,
        save_cover_file=config.save_cover_file,
        overwrite=config.overwrite,
        synced_lyrics_only=config.synced_lyrics_only,
    )

    if config.read_urls_as_txt:
        urls_from_file = []
        for url in config.urls:
            if Path(url).is_file() and Path(url).exists():
                urls_from_file.extend(
                    [
                        line.strip()
                        for line in Path(url).read_text(encoding="utf-8").splitlines()
                        if line.strip()
                    ]
                )
        urls = urls_from_file
    else:
        urls = config.urls

    error_count = 0
    for url_index, url in enumerate(urls, 1):
        url_progress = click.style(f"[URL {url_index}/{len(urls)}]", dim=True)
        logger.info(url_progress + f' Processing "{url}"')
        download_queue = downloader.get_download_item(url, config.auto_media_option)
        download_index = 1
        while True:
            item = None
            download_queue_progress = click.style(
                f"[Track {download_index}]",
                dim=True,
            )
            try:
                item = await download_queue.__anext__()
                if isinstance(item, BaseException):
                    raise item
            except StopAsyncIteration:
                break
            except VotifyUrlParseException as e:
                logger.error(url_progress + f" {str(e)}")
                break
            except VotifyMediaException as e:
                media_title = "Unknown Title"
                if e.media_metadata and e.media_metadata.get("name"):
                    media_title = e.media_metadata["name"]

                if isinstance(e, VotifyMediaFlatFilterException):
                    e = VotifyMediaFileExists(media_path=e.result)

                logger.warning(
                    download_queue_progress + f' Skipping "{media_title}": {str(e)}'
                )
                download_index += 1
                continue
            except Exception as e:
                error_count += 1
                logger.error(
                    download_queue_progress + f" Error fetching media: {str(e)}",
                    exc_info=not config.no_exceptions,
                )
                download_index += 1
                continue

            media_title = item.media.media_metadata["name"] if item else "Unknown Title"

            try:
                logger.info(download_queue_progress + f' Downloading "{media_title}"')

                await downloader.download(item)
            except Exception as e:
                if isinstance(e, VotifyDownloaderException):
                    logger.warning(
                        download_queue_progress + f' Skipping "{media_title}": {str(e)}'
                    )
                else:
                    error_count += 1
                    logger.error(
                        download_queue_progress + f' Error downloading "{media_title}"',
                        exc_info=not config.no_exceptions,
                    )
            finally:
                download_index += 1
                if (
                    database
                    and item
                    and item.media
                    and item.media.media_metadata
                    and item.staged_path
                ):
                    media_id = item.media.media_metadata["uri"].split(":")[-1]
                    database.add(media_id, item.final_path)
                await asyncio.sleep(config.wait_interval)

    logger.info(f"Finished with {error_count} error(s)")
