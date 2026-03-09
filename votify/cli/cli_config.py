import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import click
from dataclass_click import argument, option

from ..api.api import SpotifyApi
from ..downloader.audio import SpotifyAudioDownloader
from ..downloader.base import SpotifyBaseDownloader
from ..downloader.downloader import SpotifyDownloader
from ..downloader.enums import AudioDownloadMode, AudioRemuxMode, VideoRemuxMode
from ..downloader.video import SpotifyVideoDownloader
from ..interface.audio import SpotifyAudioInterface
from ..interface.base import SpotifyBaseInterface
from ..interface.enums import (
    AudioQuality,
    CoverSize,
    VideoFormat,
    VideoResolution,
    AutoMediaOption,
)
from ..interface.interface import SpotifyInterface
from ..interface.video import SpotifyVideoInterface
from .utils import Csv

api_from_cookies_sig = inspect.signature(SpotifyApi.create_from_netscape_cookies)

base_interface_sig = inspect.signature(SpotifyBaseInterface.__init__)
audio_interface_sig = inspect.signature(SpotifyAudioInterface.__init__)
video_interface_sig = inspect.signature(SpotifyVideoInterface.__init__)
interface_sig = inspect.signature(SpotifyInterface.__init__)

base_downloader_sig = inspect.signature(SpotifyBaseDownloader.__init__)
video_downloader_sig = inspect.signature(SpotifyVideoDownloader.__init__)
audio_downloader_sig = inspect.signature(SpotifyAudioDownloader.__init__)
downloader_sig = inspect.signature(SpotifyDownloader.__init__)


@dataclass
class CliConfig:
    # CLI specific options
    urls: Annotated[
        list[str],
        argument(
            nargs=-1,
            type=str,
        ),
    ]
    wait_interval: Annotated[
        int,
        option(
            "--wait-interval",
            help="Wait interval between downloads in seconds",
            default=10,
        ),
    ]
    read_urls_as_txt: Annotated[
        bool,
        option(
            "--read-urls-as-txt",
            "-r",
            help="Read URLs from text files",
            is_flag=True,
        ),
    ]
    config_path: Annotated[
        str,
        option(
            "--config-path",
            help="Config file path",
            default=str(Path.home() / ".votify" / "config.ini"),
            type=click.Path(
                file_okay=True,
                dir_okay=False,
                writable=True,
                resolve_path=True,
            ),
        ),
    ]
    log_level: Annotated[
        str,
        option(
            "--log-level",
            help="Logging level",
            default="INFO",
            type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
        ),
    ]
    log_file: Annotated[
        str,
        option(
            "--log-file",
            help="Log file path",
            default=None,
            type=click.Path(
                file_okay=True,
                dir_okay=False,
                writable=True,
                resolve_path=True,
            ),
        ),
    ]
    no_exceptions: Annotated[
        bool,
        option(
            "--no-exceptions",
            help="Don't print exceptions",
            is_flag=True,
        ),
    ]
    # API specific options
    cookies_path: Annotated[
        str,
        option(
            "--cookies-path",
            "-c",
            help="Cookies file path",
            default=api_from_cookies_sig.parameters["cookies_path"].default,
            type=click.Path(
                file_okay=True,
                dir_okay=False,
                readable=True,
                resolve_path=True,
            ),
        ),
    ]
    # Base Interface specific options
    cover_size: Annotated[
        CoverSize,
        option(
            "--cover-size",
            help="Cover size to use",
            default=base_interface_sig.parameters["cover_size"].default,
            type=CoverSize,
        ),
    ]
    no_drm: Annotated[
        bool,
        option(
            "--no-drm",
            help="Don't allow DRM-protected media",
            is_flag=True,
        ),
    ]
    wvd_path: Annotated[
        str,
        option(
            "--wvd-path",
            help=".wvd file path",
            default=base_interface_sig.parameters["wvd_path"].default,
            type=click.Path(
                file_okay=True,
                dir_okay=False,
                readable=True,
                resolve_path=True,
            ),
        ),
    ]
    # Audio Interface specific options
    audio_quality: Annotated[
        AudioQuality,
        option(
            "--audio-quality",
            help="Comma-separated audio quality priority",
            default=audio_interface_sig.parameters["audio_quality_priority"].default,
            type=Csv(AudioQuality),
        ),
    ]
    # Video Interface specific options
    video_format: Annotated[
        VideoFormat,
        option(
            "--video-format",
            help="Video format to use",
            default=video_interface_sig.parameters["video_format"].default,
            type=VideoFormat,
        ),
    ]
    video_resolution: Annotated[
        VideoResolution,
        option(
            "--video-resolution",
            help="Video resolution to use",
            default=video_interface_sig.parameters["resolution"].default,
            type=VideoResolution,
        ),
    ]
    # Interface specific options
    prefer_video: Annotated[
        bool,
        option(
            "--prefer-video",
            help="Prefer video streams when available",
            is_flag=True,
        ),
    ]
    auto_media_option: Annotated[
        AutoMediaOption,
        option(
            "--auto-media-option",
            help="Auto media option",
            default=None,
            type=AutoMediaOption,
        ),
    ]
    # Base Downloader specific options
    output: Annotated[
        str,
        option(
            "--output",
            "-o",
            help="Output directory path",
            default=base_downloader_sig.parameters["output_path"].default,
            type=click.Path(
                file_okay=True,
                dir_okay=True,
                writable=True,
                resolve_path=True,
            ),
        ),
    ]
    temp: Annotated[
        str,
        option(
            "--temp",
            help="Temporary directory path",
            default=base_downloader_sig.parameters["temp_path"].default,
            type=click.Path(
                file_okay=True,
                dir_okay=True,
                writable=True,
                resolve_path=True,
            ),
        ),
    ]
    aria2c_path: Annotated[
        str,
        option(
            "--aria2c-path",
            help="aria2c executable path",
            default=base_downloader_sig.parameters["aria2c_path"].default,
        ),
    ]
    curl_path: Annotated[
        str,
        option(
            "--curl-path",
            help="curl executable path",
            default=base_downloader_sig.parameters["curl_path"].default,
        ),
    ]
    ffmpeg_path: Annotated[
        str,
        option(
            "--ffmpeg-path",
            help="ffmpeg executable path",
            default=base_downloader_sig.parameters["ffmpeg_path"].default,
        ),
    ]
    mp4box_path: Annotated[
        str,
        option(
            "--mp4box-path",
            help="MP4Box executable path",
            default=base_downloader_sig.parameters["mp4box_path"].default,
        ),
    ]
    mp4decrypt_path: Annotated[
        str,
        option(
            "--mp4decrypt-path",
            help="mp4decrypt executable path",
            default=base_downloader_sig.parameters["mp4decrypt_path"].default,
        ),
    ]
    shaka_packager_path: Annotated[
        str,
        option(
            "--shaka-packager-path",
            help="Shaka Packager executable path",
            default=base_downloader_sig.parameters["shaka_packager_path"].default,
        ),
    ]
    album_folder_template: Annotated[
        str,
        option(
            "--album-folder-template",
            help="Album folder template",
            default=base_downloader_sig.parameters["album_folder_template"].default,
        ),
    ]
    compilation_folder_template: Annotated[
        str,
        option(
            "--compilation-folder-template",
            help="Compilation folder template",
            default=base_downloader_sig.parameters[
                "compilation_folder_template"
            ].default,
        ),
    ]
    podcast_folder_template: Annotated[
        str,
        option(
            "--podcast-folder-template",
            help="Podcast folder template",
            default=base_downloader_sig.parameters["podcast_folder_template"].default,
        ),
    ]
    no_album_folder_template: Annotated[
        str,
        option(
            "--no-album-folder-template",
            help="No album folder template",
            default=base_downloader_sig.parameters["no_album_folder_template"].default,
        ),
    ]
    single_disc_file_template: Annotated[
        str,
        option(
            "--single-disc-file-template",
            help="Single disc file template",
            default=base_downloader_sig.parameters["single_disc_file_template"].default,
        ),
    ]
    multi_disc_file_template: Annotated[
        str,
        option(
            "--multi-disc-file-template",
            help="Multi disc file template",
            default=base_downloader_sig.parameters["multi_disc_file_template"].default,
        ),
    ]
    podcast_file_template: Annotated[
        str,
        option(
            "--podcast-file-template",
            help="Podcast file template",
            default=base_downloader_sig.parameters["podcast_file_template"].default,
        ),
    ]
    no_album_file_template: Annotated[
        str,
        option(
            "--no-album-file-template",
            help="No album file template",
            default=base_downloader_sig.parameters["no_album_file_template"].default,
        ),
    ]
    playlist_file_template: Annotated[
        str,
        option(
            "--playlist-file-template",
            help="Playlist file template",
            default=base_downloader_sig.parameters["playlist_file_template"].default,
        ),
    ]
    date_tag_template: Annotated[
        str,
        option(
            "--date-tag-template",
            help="Date tag template",
            default=base_downloader_sig.parameters["date_tag_template"].default,
        ),
    ]
    exclude_tags: Annotated[
        list[str],
        option(
            "--exclude-tags",
            help="Comma-separated tags to exclude",
            default=base_downloader_sig.parameters["exclude_tags"].default,
            type=Csv(str),
        ),
    ]
    truncate: Annotated[
        int | None,
        option(
            "--truncate",
            help="Truncate file and folder names to the specified length",
            default=base_downloader_sig.parameters["truncate"].default,
        ),
    ]
    # Video Downloader specific options
    video_remux_mode: Annotated[
        VideoRemuxMode,
        option(
            "--video-remux-mode",
            help="Video remux mode to use",
            default=video_downloader_sig.parameters["remux_mode"].default,
            type=VideoRemuxMode,
        ),
    ]
    # Audio Downloader specific options
    audio_download_mode: Annotated[
        AudioDownloadMode,
        option(
            "--audio-download-mode",
            help="Audio download mode to use",
            default=audio_downloader_sig.parameters["download_mode"].default,
            type=AudioDownloadMode,
        ),
    ]
    audio_remux_mode: Annotated[
        AudioRemuxMode,
        option(
            "--audio-remux-mode",
            help="Audio remux mode to use",
            default=audio_downloader_sig.parameters["remux_mode"].default,
            type=AudioRemuxMode,
        ),
    ]
    # Downloader specific options
    no_synced_lyrics_file: Annotated[
        bool,
        option(
            "--no-synced-lyrics-file",
            help="Don't create synced lyrics file",
            is_flag=True,
        ),
    ]
    save_playlist_file: Annotated[
        bool,
        option(
            "--save-playlist-file",
            help="Save playlist file",
            is_flag=True,
        ),
    ]
    save_cover_file: Annotated[
        bool,
        option(
            "--save-cover-file",
            help="Save cover file",
            is_flag=True,
        ),
    ]
    overwrite: Annotated[
        bool,
        option(
            "--overwrite",
            help="Overwrite existing media files",
            is_flag=True,
        ),
    ]
    synced_lyrics_only: Annotated[
        bool,
        option(
            "--synced-lyrics-only",
            help="Only download synced lyrics file",
            is_flag=True,
        ),
    ]
    no_config_file: Annotated[
        bool,
        option(
            "--no-config-file",
            "-n",
            help="Don't use a config file",
            is_flag=True,
        ),
    ]
