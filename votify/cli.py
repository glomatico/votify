from __future__ import annotations

import inspect
import json
import logging
import time
from enum import Enum
from pathlib import Path

import click

from . import __version__
from .constants import EXCLUDED_CONFIG_FILE_PARAMS, X_NOT_FOUND_STRING
from .downloader import Downloader
from .downloader_episode import DownloaderEpisode
from .downloader_song import DownloaderSong
from .enums import DownloadMode, Quality
from .spotify_api import SpotifyApi

logger = logging.getLogger("votify")

spotify_api_sig = inspect.signature(SpotifyApi.__init__)
downloader_sig = inspect.signature(Downloader.__init__)
downloader_song_sig = inspect.signature(DownloaderSong.__init__)


def get_param_string(param: click.Parameter) -> str:
    if isinstance(param.default, Enum):
        return param.default.value
    elif isinstance(param.default, Path):
        return str(param.default)
    else:
        return param.default


def write_default_config_file(ctx: click.Context) -> None:
    ctx.params["config_path"].parent.mkdir(parents=True, exist_ok=True)
    config_file = {
        param.name: get_param_string(param)
        for param in ctx.command.params
        if param.name not in EXCLUDED_CONFIG_FILE_PARAMS
    }
    ctx.params["config_path"].write_text(json.dumps(config_file, indent=4))


def load_config_file(
    ctx: click.Context,
    param: click.Parameter,
    no_config_file: bool,
) -> click.Context:
    if no_config_file:
        return ctx
    if not ctx.params["config_path"].exists():
        write_default_config_file(ctx)
    config_file = dict(json.loads(ctx.params["config_path"].read_text()))
    for param in ctx.command.params:
        if (
            config_file.get(param.name) is not None
            and not ctx.get_parameter_source(param.name)
            == click.core.ParameterSource.COMMANDLINE
        ):
            ctx.params[param.name] = param.type_cast_value(ctx, config_file[param.name])
    return ctx


@click.command()
@click.help_option("-h", "--help")
@click.version_option(__version__, "-v", "--version")
# CLI specific options
@click.argument(
    "urls",
    nargs=-1,
    type=str,
    required=True,
)
@click.option(
    "--wait-interval",
    "-w",
    type=float,
    default=10,
    help="Wait interval between downloads in seconds.",
)
@click.option(
    "--force-premium",
    "-f",
    is_flag=True,
    help="Force to detect the account as premium.",
)
@click.option(
    "--read-urls-as-txt",
    "-r",
    is_flag=True,
    help="Interpret URLs as paths to text files containing URLs.",
)
@click.option(
    "--config-path",
    type=Path,
    default=Path.home() / ".votify" / "config.json",
    help="Path to config file.",
)
@click.option(
    "--log-level",
    type=str,
    default="INFO",
    help="Log level.",
)
@click.option(
    "--print-exceptions",
    is_flag=True,
    help="Print exceptions.",
)
# SpotifyApi specific options
@click.option(
    "--cookies-path",
    type=Path,
    default=spotify_api_sig.parameters["cookies_path"].default,
    help="Path to cookies file.",
)
# Downloader specific options
@click.option(
    "--quality",
    "-q",
    type=Quality,
    default=downloader_sig.parameters["quality"].default,
    help="Audio quality.",
)
@click.option(
    "--output-path",
    "-o",
    type=Path,
    default=downloader_sig.parameters["output_path"].default,
    help="Path to output directory.",
)
@click.option(
    "--temp-path",
    type=Path,
    default=downloader_sig.parameters["temp_path"].default,
    help="Path to temporary directory.",
)
@click.option(
    "--download-mode",
    "-d",
    type=DownloadMode,
    default=downloader_sig.parameters["download_mode"].default,
    help="Download mode.",
)
@click.option(
    "--aria2c-path",
    type=str,
    default=downloader_sig.parameters["aria2c_path"].default,
    help="Path to aria2c binary.",
)
@click.option(
    "--unplayplay-path",
    type=str,
    default=downloader_sig.parameters["unplayplay_path"].default,
    help="Path to unplayplay binary.",
)
@click.option(
    "--template-folder-album",
    type=str,
    default=downloader_sig.parameters["template_folder_album"].default,
    help="Template folder for tracks that are part of an album.",
)
@click.option(
    "--template-folder-compilation",
    type=str,
    default=downloader_sig.parameters["template_folder_compilation"].default,
    help="Template folder for tracks that are part of a compilation album.",
)
@click.option(
    "--template-file-single-disc",
    type=str,
    default=downloader_sig.parameters["template_file_single_disc"].default,
    help="Template file for the tracks that are part of a single-disc album.",
)
@click.option(
    "--template-file-multi-disc",
    type=str,
    default=downloader_sig.parameters["template_file_multi_disc"].default,
    help="Template file for the tracks that are part of a multi-disc album.",
)
@click.option(
    "--template-folder-episode",
    type=str,
    default=downloader_sig.parameters["template_folder_episode"].default,
    help="Template folder for episodes (podcasts).",
)
@click.option(
    "--template-file-episode",
    type=str,
    default=downloader_sig.parameters["template_file_episode"].default,
    help="Template file for episodes (podcasts).",
)
@click.option(
    "--template-file-playlist",
    type=str,
    default=downloader_sig.parameters["template_file_playlist"].default,
    help="Template file for the M3U8 playlist.",
)
@click.option(
    "--date-tag-template",
    type=str,
    default=downloader_sig.parameters["date_tag_template"].default,
    help="Date tag template.",
)
@click.option(
    "--save-cover",
    "-s",
    is_flag=True,
    help="Save cover as a separate file.",
)
@click.option(
    "--save-playlist",
    is_flag=True,
    help="Save a M3U8 playlist file when downloading a playlist.",
)
@click.option(
    "--overwrite",
    is_flag=True,
    help="Overwrite existing files.",
)
@click.option(
    "--exclude-tags",
    type=str,
    default=downloader_sig.parameters["exclude_tags"].default,
    help="Comma-separated tags to exclude.",
)
@click.option(
    "--truncate",
    type=int,
    default=downloader_sig.parameters["truncate"].default,
    help="Maximum length of the file/folder names.",
)
# DownloaderSong specific options
@click.option(
    "--lrc-only",
    "-l",
    is_flag=True,
    help="Download only the synced lyrics.",
)
@click.option(
    "--no-lrc",
    is_flag=True,
    help="Don't download the synced lyrics.",
)
# This option should always be last
@click.option(
    "--no-config-file",
    "-n",
    is_flag=True,
    callback=load_config_file,
    help="Do not use a config file.",
)
def main(
    urls: list[str],
    wait_interval: float,
    force_premium: bool,
    read_urls_as_txt: bool,
    config_path: Path,
    log_level: str,
    print_exceptions: bool,
    cookies_path: Path,
    quality: Quality,
    output_path: Path,
    temp_path: Path,
    download_mode: DownloadMode,
    aria2c_path: str,
    unplayplay_path: str,
    template_folder_album: str,
    template_folder_compilation: str,
    template_file_single_disc: str,
    template_file_multi_disc: str,
    template_folder_episode: str,
    template_file_episode: str,
    template_file_playlist: str,
    date_tag_template: str,
    save_cover: bool,
    save_playlist: bool,
    overwrite: bool,
    exclude_tags: str,
    truncate: int,
    lrc_only: bool,
    no_lrc: bool,
    no_config_file: bool,
) -> None:
    logging.basicConfig(
        format="[%(levelname)-8s %(asctime)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    logger.setLevel(log_level)
    logger.info("Starting Votify")
    spotify_api = SpotifyApi(cookies_path)
    downloader = Downloader(
        spotify_api,
        quality,
        output_path,
        temp_path,
        download_mode,
        aria2c_path,
        unplayplay_path,
        template_folder_album,
        template_folder_compilation,
        template_file_single_disc,
        template_file_multi_disc,
        template_folder_episode,
        template_file_episode,
        template_file_playlist,
        date_tag_template,
        save_cover,
        save_playlist,
        overwrite,
        exclude_tags,
        truncate,
    )
    downloader_song = DownloaderSong(
        downloader,
        lrc_only,
        no_lrc,
    )
    downloader_episode = DownloaderEpisode(
        downloader,
    )
    if not lrc_only:
        if not downloader.unplayplay_path_full:
            logger.critical(X_NOT_FOUND_STRING.format("Unplayplay", unplayplay_path))
            return
        if download_mode == DownloadMode.ARIA2C and not downloader.aria2c_path_full:
            logger.critical(X_NOT_FOUND_STRING.format("aria2c", aria2c_path))
            return
        spotify_api.config_info["isPremium"] = (
            True if force_premium else spotify_api.config_info["isPremium"]
        )
        if not spotify_api.config_info["isPremium"] and quality == Quality.HIGH:
            logger.critical("Cannot download at chosen quality with a free account")
            return
    error_count = 0
    if read_urls_as_txt:
        _urls = []
        for url in urls:
            if Path(url).exists():
                _urls.extend(Path(url).read_text(encoding="utf-8").splitlines())
        urls = _urls
    for url_index, url in enumerate(urls, start=1):
        url_progress = f"URL {url_index}/{len(urls)}"
        logger.info(f'({url_progress}) Checking "{url}"')
        try:
            url_info = downloader.get_url_info(url)
            if url_info.type == "artist":
                download_queue = downloader.get_download_queue_from_artist(url_info.id)
            else:
                download_queue = downloader.get_download_queue(
                    url_info.type,
                    url_info.id,
                )
        except Exception as e:
            error_count += 1
            logger.error(
                f'({url_progress}) Failed to check "{url}"',
                exc_info=print_exceptions,
            )
            continue
        for index, download_queue_item in enumerate(download_queue, start=1):
            queue_progress = (
                f"Track {index}/{len(download_queue)}" f" from URL {url}/{len(urls)}"
            )
            media_metadata = download_queue_item.media_metadata
            try:
                logger.info(
                    f'({queue_progress}) Downloading "{media_metadata["name"]}"'
                )
                media_id = downloader.get_media_id(media_metadata)
                media_type = media_metadata["type"]
                if media_type == "track":
                    downloader_song.download(
                        track_id=media_id,
                        track_metadata=media_metadata,
                        album_metadata=download_queue_item.album_metadata,
                        playlist_metadata=download_queue_item.playlist_metadata,
                        playlist_track=index,
                    )
                elif media_type == "episode" and not lrc_only:
                    downloader_episode.download(
                        episode_id=media_id,
                        episode_metadata=media_metadata,
                        show_metadata=download_queue_item.show_metadata,
                        playlist_metadata=download_queue_item.playlist_metadata,
                        playlist_track=index,
                    )
            except Exception as e:
                error_count += 1
                logger.error(
                    f'({queue_progress}) Failed to download "{media_metadata["name"]}"',
                    exc_info=print_exceptions,
                )
            finally:
                if wait_interval > 0 and index != len(download_queue):
                    logger.debug(
                        f"Waiting for {wait_interval} second(s) before continuing"
                    )
                    time.sleep(wait_interval)
        logger.info(f"Done ({error_count} error(s))")
