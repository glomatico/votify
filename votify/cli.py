from __future__ import annotations

import inspect
import json
import logging
import time
from enum import Enum
from pathlib import Path

import click
import colorama

from . import __version__
from .constants import (
    AAC_AUDIO_QUALITIES,
    EXCLUDED_CONFIG_FILE_PARAMS,
    PREMIUM_AUDIO_QUALITIES,
    VORBIS_AUDIO_QUALITIES,
    X_NOT_FOUND_STRING,
)
from .custom_formatter import CustomFormatter
from .downloader import Downloader
from .downloader_audio import DownloaderAudio
from .downloader_episode import DownloaderEpisode
from .downloader_episode_video import DownloaderEpisodeVideo
from .downloader_music_video import DownloaderMusicVideo
from .downloader_song import DownloaderSong
from .downloader_video import DownloaderVideo
from .enums import (
    AudioQuality,
    CoverSize,
    DownloadMode,
    RemuxModeAudio,
    RemuxModeVideo,
    VideoFormat,
)
from .spotify_api import SpotifyApi
from .utils import color_text

logger = logging.getLogger("votify")

spotify_api_sig = inspect.signature(SpotifyApi.__init__)
downloader_sig = inspect.signature(Downloader.__init__)
downloader_audio_sig = inspect.signature(DownloaderAudio.__init__)
downloader_song_sig = inspect.signature(DownloaderSong.__init__)
downloader_video_sig = inspect.signature(DownloaderVideo.__init__)


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
    default=5,
    help="Wait interval between downloads in seconds.",
)
@click.option(
    "--enable-videos",
    is_flag=True,
    help="Enable video downloads when available.",
)
@click.option(
    "--download-music-videos",
    is_flag=True,
    help="List and select a related music video to download from songs.",
)
@click.option(
    "--download-podcast-videos",
    is_flag=True,
    help="Attempt to download the video version of podcasts.",
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
    "--no-exceptions",
    is_flag=True,
    help="Don't print exceptions.",
)
@click.option(
    "--cookies-path",
    type=Path,
    default=Path("./cookies.txt"),
    help="Path to cookies file.",
)
# Downloader specific options
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
    "--wvd-path",
    type=Path,
    default=downloader_sig.parameters["wvd_path"].default,
    help="Path to .wvd file.",
)
@click.option(
    "--aria2c-path",
    type=str,
    default=downloader_sig.parameters["aria2c_path"].default,
    help="Path to aria2c binary.",
)
@click.option(
    "--ffmpeg-path",
    type=str,
    default=downloader_sig.parameters["ffmpeg_path"].default,
    help="Path to ffmpeg binary.",
)
@click.option(
    "--mp4box-path",
    type=str,
    default=downloader_sig.parameters["mp4box_path"].default,
    help="Path to MP4Box binary.",
)
@click.option(
    "--mp4decrypt-path",
    type=str,
    default=downloader_sig.parameters["mp4decrypt_path"].default,
    help="Path to mp4decrypt binary.",
)
@click.option(
    "--packager-path",
    type=str,
    default=downloader_sig.parameters["packager_path"].default,
    help="Path to Shaka Packager binary.",
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
    help="Template file for music videos.",
)
@click.option(
    "--template-folder-music-video",
    type=str,
    default=downloader_sig.parameters["template_folder_music_video"].default,
    help="Template folder for music videos",
)
@click.option(
    "--template-file-music-video",
    type=str,
    default=downloader_sig.parameters["template_file_music_video"].default,
    help="Template file for the tracks that are not part of an album.",
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
    "--cover-size",
    type=CoverSize,
    default=downloader_sig.parameters["cover_size"].default,
    help="Cover size.",
)
@click.option(
    "--save-cover",
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
# DownloaderAudio specific options
@click.option(
    "--audio-quality",
    "-a",
    type=AudioQuality,
    default=downloader_audio_sig.parameters["audio_quality"].default,
    help="Audio quality for songs and podcasts.",
)
@click.option(
    "--download-mode",
    "-d",
    type=DownloadMode,
    default=downloader_audio_sig.parameters["download_mode"].default,
    help="Download mode for songs and podcasts.",
)
@click.option(
    "--remux-mode-audio",
    type=RemuxModeAudio,
    default=downloader_audio_sig.parameters["remux_mode"].default,
    help="Remux mode for songs and podcasts.",
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
# DownloaderVideo specific options
@click.option(
    "--video-format",
    type=VideoFormat,
    default=downloader_video_sig.parameters["video_format"].default,
    help="Video format.",
)
@click.option(
    "--remux-mode-video",
    type=RemuxModeVideo,
    default=downloader_video_sig.parameters["remux_mode"].default,
    help="Remux mode for videos.",
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
    enable_videos: bool,
    download_music_videos: bool,
    download_podcast_videos: bool,
    force_premium: bool,
    read_urls_as_txt: bool,
    config_path: Path,
    log_level: str,
    no_exceptions: bool,
    cookies_path: Path,
    output_path: Path,
    temp_path: Path,
    wvd_path: Path,
    download_mode: DownloadMode,
    aria2c_path: str,
    ffmpeg_path: str,
    mp4box_path: str,
    mp4decrypt_path: str,
    packager_path: str,
    template_folder_album: str,
    template_folder_compilation: str,
    template_file_single_disc: str,
    template_file_multi_disc: str,
    template_folder_episode: str,
    template_file_episode: str,
    template_folder_music_video: str,
    template_file_music_video: str,
    template_file_playlist: str,
    date_tag_template: str,
    cover_size: CoverSize,
    save_cover: bool,
    save_playlist: bool,
    overwrite: bool,
    exclude_tags: str,
    truncate: int,
    audio_quality: AudioQuality,
    remux_mode_audio: RemuxModeAudio,
    lrc_only: bool,
    no_lrc: bool,
    video_format: VideoFormat,
    remux_mode_video: RemuxModeVideo,
    no_config_file: bool,
) -> None:
    colorama.just_fix_windows_console()
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(CustomFormatter())
    logger.addHandler(stream_handler)
    if not cookies_path.exists():
        logger.critical(X_NOT_FOUND_STRING.format("Cookies file", cookies_path))
        return
    logger.info("Starting Votify")
    spotify_api = SpotifyApi.from_cookies_file(cookies_path)
    if spotify_api.session_info["isAnonymous"]:
        logger.critical(
            "Failed to get a valid session. Try logging in and exporting your cookies again"
        )
        return
    downloader = Downloader(
        spotify_api,
        output_path,
        temp_path,
        wvd_path,
        aria2c_path,
        ffmpeg_path,
        mp4box_path,
        mp4decrypt_path,
        packager_path,
        template_folder_album,
        template_folder_compilation,
        template_file_single_disc,
        template_file_multi_disc,
        template_folder_episode,
        template_file_episode,
        template_folder_music_video,
        template_file_music_video,
        template_file_playlist,
        date_tag_template,
        cover_size,
        save_cover,
        save_playlist,
        overwrite,
        exclude_tags,
        truncate,
    )
    downloader_audio = DownloaderAudio(
        downloader,
        audio_quality,
        download_mode,
        remux_mode_audio,
    )
    downloader_song = DownloaderSong(
        downloader_audio,
        lrc_only,
        no_lrc,
    )
    downloader_episode = DownloaderEpisode(
        downloader_audio,
    )
    downloader_video = DownloaderVideo(
        downloader,
        video_format,
        remux_mode_video,
    )
    downloader_episode_video = DownloaderEpisodeVideo(
        downloader_video,
        downloader_episode,
    )
    downloader_music_video = DownloaderMusicVideo(
        downloader_video,
    )
    is_premium = (
        True if force_premium else spotify_api.user_profile["product"] == "premium"
    )
    if not lrc_only:
        if audio_quality in AAC_AUDIO_QUALITIES:
            if (
                remux_mode_audio == RemuxModeAudio.FFMPEG
                and not downloader.ffmpeg_path_full
            ):
                logger.critical(X_NOT_FOUND_STRING.format("FFmpeg", ffmpeg_path))
            if (
                remux_mode_audio == RemuxModeAudio.MP4BOX
                and not downloader.mp4box_path_full
            ):
                logger.critical(X_NOT_FOUND_STRING.format("MP4Box", mp4box_path))
                return
            if (
                remux_mode_audio
                in (
                    RemuxModeAudio.MP4DECRYPT,
                    RemuxModeAudio.MP4BOX,
                )
                and not downloader.mp4decrypt_path_full
            ):
                logger.critical(
                    X_NOT_FOUND_STRING.format("mp4decrypt", mp4decrypt_path)
                )
                return
            if not wvd_path.exists():
                logger.critical(
                    X_NOT_FOUND_STRING.format(".wvd", wvd_path)
                    + ", a .wvd file is required for downloading in AAC quality"
                )
                return
            downloader.set_cdm()
        if download_mode == DownloadMode.ARIA2C and not downloader.aria2c_path_full:
            logger.critical(X_NOT_FOUND_STRING.format("aria2c", aria2c_path))
            return
        if not is_premium and audio_quality in PREMIUM_AUDIO_QUALITIES:
            logger.critical("Cannot download at chosen quality with a free account")
            return
    can_download_music_videos = True
    if enable_videos:
        if (
            downloader_music_video.remux_mode == RemuxModeVideo.FFMPEG
            and not downloader.ffmpeg_path_full
        ):
            logger.critical(X_NOT_FOUND_STRING.format("FFmpeg", ffmpeg_path))
            return
        if (
            downloader_music_video.remux_mode == RemuxModeVideo.MP4BOX
            and not downloader.mp4box_path_full
        ):
            logger.critical(X_NOT_FOUND_STRING.format("MP4Box", mp4box_path))
            return
        music_video_warning_message = []
        if not downloader.mp4decrypt_path_full and video_format == VideoFormat.MP4:
            music_video_warning_message.append(
                X_NOT_FOUND_STRING.format("mp4decrypt", mp4decrypt_path)
            )
        elif not downloader.packager_path_full and video_format == VideoFormat.WEBM:
            music_video_warning_message.append(
                X_NOT_FOUND_STRING.format("Shaka Packager", packager_path)
            )
        if not wvd_path.exists():
            music_video_warning_message.append(
                X_NOT_FOUND_STRING.format(".wvd file", wvd_path)
            )
        else:
            downloader.set_cdm()
        if is_premium:
            music_video_warning_message.append(
                "Cannot download music videos with a non-premium account"
            )
        if music_video_warning_message:
            logger.warning(
                "Music videos will not be downloaded due to the following reasons:\n"
                + "\n".join(music_video_warning_message)
            )
            can_download_music_videos = False
    error_count = 0
    if read_urls_as_txt:
        _urls = []
        for url in urls:
            if Path(url).exists():
                _urls.extend(Path(url).read_text(encoding="utf-8").splitlines())
        urls = _urls
    for url_index, url in enumerate(urls, start=1):
        url_progress = color_text(f"URL {url_index}/{len(urls)}", colorama.Style.DIM)
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
                exc_info=no_exceptions,
            )
            continue
        for index, download_queue_item in enumerate(download_queue, start=1):
            queue_progress = color_text(
                f"Track {index}/{len(download_queue)} from URL {url_index}/{len(urls)}",
                colorama.Style.DIM,
            )
            media_metadata = download_queue_item.media_metadata
            try:
                logger.info(
                    f'({queue_progress}) Downloading "{media_metadata["name"]}"'
                )
                media_id = downloader.get_media_id(media_metadata)
                media_type = media_metadata["type"]
                gid_metadata = downloader.get_gid_metadata(media_id, media_type)
                if gid_metadata.get("original_video") or (
                    media_type == "track" and download_music_videos
                ):
                    if not enable_videos or not can_download_music_videos:
                        logger.warning(
                            "Music videos are not downloadable with current "
                            "configuration, skipping"
                        )
                        continue
                    downloader_music_video.download(
                        music_video_id=media_id,
                        music_video_metadata=media_metadata,
                        album_metadata=download_queue_item.album_metadata,
                        gid_metadata=gid_metadata,
                        playlist_metadata=download_queue_item.playlist_metadata,
                        playlist_track=index,
                    )
                elif media_type == "track":
                    if audio_quality in VORBIS_AUDIO_QUALITIES:
                        logger.warning(
                            "Vorbis audio quality is only supported for podcasts, "
                            "skipping"
                        )
                        continue
                    downloader_song.download(
                        track_id=media_id,
                        track_metadata=media_metadata,
                        album_metadata=download_queue_item.album_metadata,
                        gid_metadata=gid_metadata,
                        playlist_metadata=download_queue_item.playlist_metadata,
                        playlist_track=index,
                    )
                elif media_type == "episode":
                    if enable_videos and download_podcast_videos:
                        downloader_episode_video.download(
                            episode_id=media_id,
                            episode_metadata=media_metadata,
                            show_metadata=download_queue_item.show_metadata,
                            gid_metadata=gid_metadata,
                            playlist_metadata=download_queue_item.playlist_metadata,
                            playlist_track=index,
                        )
                    else:
                        downloader_episode.download(
                            episode_id=media_id,
                            episode_metadata=media_metadata,
                            show_metadata=download_queue_item.show_metadata,
                            gid_metadata=gid_metadata,
                            playlist_metadata=download_queue_item.playlist_metadata,
                            playlist_track=index,
                        )
            except Exception as e:
                error_count += 1
                logger.error(
                    f'({queue_progress}) Failed to download "{media_metadata["name"]}"',
                    exc_info=not no_exceptions,
                )
            finally:
                if wait_interval > 0 and index != len(download_queue):
                    logger.debug(
                        f"Waiting for {wait_interval} second(s) before continuing"
                    )
                    time.sleep(wait_interval)
        logger.info(f"Done ({error_count} error(s))")
