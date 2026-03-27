import asyncio
import base64
import logging
import re
import shutil
import subprocess
from io import BytesIO
from pathlib import Path

import httpx
from async_lru import alru_cache
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover
from mutagen.oggvorbis import OggVorbis, OggVorbisHeaderError
from PIL import Image

from ..interface.enums import MediaType
from ..interface.interface import SpotifyInterface
from ..interface.types import MediaTags, PlaylistTags
from ..utils import CustomStringFormatter
from .constants import ILLEGAL_CHAR_REPLACEMENT, ILLEGAL_CHARS_RE, TEMP_PATH_TEMPLATE

logger = logging.getLogger(__name__)


class SpotifyBaseDownloader:
    def __init__(
        self,
        interface: SpotifyInterface,
        output_path: str = "./Spotify",
        temp_path: str = ".",
        aria2c_path: str = "aria2c",
        curl_path: str = "curl",
        ffmpeg_path: str = "ffmpeg",
        mp4box_path: str = "mp4box",
        mp4decrypt_path: str = "mp4decrypt",
        shaka_packager_path: str = "packager",
        album_folder_template: str = "{album_artist}/{album}",
        compilation_folder_template: str = "Compilations/{album}",
        podcast_folder_template: str = "Podcasts/{album}",
        no_album_folder_template: str = "{artist}/Unknown Album",
        single_disc_file_template: str = "{track:02d} {title}",
        multi_disc_file_template: str = "{disc}-{track:02d} {title}",
        podcast_file_template: str = "{track:02d} {title}",
        no_album_file_template: str = "{title}",
        playlist_file_template: str = "Playlists/{playlist_artist}/{playlist_title}",
        date_tag_template: str = "%Y-%m-%dT%H:%M:%SZ",
        exclude_tags: list[str] | None = None,
        truncate: int | None = None,
        silent: bool = False,
        skip_cleanup: bool = False,
    ) -> None:
        self.interface = interface
        self.output_path = output_path
        self.temp_path = temp_path
        self.aria2c_path = aria2c_path
        self.curl_path = curl_path
        self.ffmpeg_path = ffmpeg_path
        self.mp4box_path = mp4box_path
        self.mp4decrypt_path = mp4decrypt_path
        self.shaka_packager_path = shaka_packager_path
        self.album_folder_template = album_folder_template
        self.compilation_folder_template = compilation_folder_template
        self.podcast_folder_template = podcast_folder_template
        self.no_album_folder_template = no_album_folder_template
        self.single_disc_file_template = single_disc_file_template
        self.multi_disc_file_template = multi_disc_file_template
        self.podcast_file_template = podcast_file_template
        self.no_album_file_template = no_album_file_template
        self.playlist_file_template = playlist_file_template
        self.date_tag_template = date_tag_template
        self.exclude_tags = exclude_tags
        self.truncate = truncate
        self.silent = silent
        self.skip_cleanup = skip_cleanup

        self._initialize()

    def _initialize(self) -> None:
        self._initialize_truncate()
        self._initialize_full_binaries_path()

    def _initialize_truncate(self) -> None:
        if isinstance(self.truncate, int):
            self.truncate = None if self.truncate < 4 else self.truncate

    def _initialize_full_binaries_path(self) -> None:
        self.aria2c_full_path = shutil.which(self.aria2c_path)
        self.curl_full_path = shutil.which(self.curl_path)
        self.ffmpeg_full_path = shutil.which(self.ffmpeg_path)
        self.mp4box_full_path = shutil.which(self.mp4box_path)
        self.mp4decrypt_full_path = shutil.which(self.mp4decrypt_path)
        self.shaka_packager_full_path = shutil.which(self.shaka_packager_path)

    def sanitize_string(
        self,
        dirty_string: str,
        file_ext: str = None,
    ) -> str:
        sanitized_string = re.sub(
            ILLEGAL_CHARS_RE,
            ILLEGAL_CHAR_REPLACEMENT,
            dirty_string,
        )

        if file_ext is None:
            sanitized_string = sanitized_string[: self.truncate]
            if sanitized_string.endswith("."):
                sanitized_string = sanitized_string[:-1] + ILLEGAL_CHAR_REPLACEMENT
        else:
            if self.truncate is not None:
                sanitized_string = sanitized_string[: self.truncate - len(file_ext)]
            sanitized_string += file_ext

        return sanitized_string.strip()

    def get_final_path(
        self,
        tags: MediaTags,
        file_extension: str,
        playlist_tags: PlaylistTags | None,
    ) -> str:
        if tags.media_type in {MediaType.PODCAST, MediaType.PODCAST_VIDEO}:
            template_folder_parts = self.podcast_folder_template.split("/")
            template_file_parts = self.podcast_file_template.split("/")
        else:
            if tags.album:
                template_folder_parts = (
                    self.compilation_folder_template.split("/")
                    if tags.compilation
                    else self.album_folder_template.split("/")
                )
                template_file_parts = (
                    self.multi_disc_file_template.split("/")
                    if isinstance(tags.disc_total, int) and tags.disc_total > 1
                    else self.single_disc_file_template.split("/")
                )
            else:
                template_folder_parts = self.no_album_folder_template.split("/")
                template_file_parts = self.no_album_file_template.split("/")

        template_parts = template_folder_parts + template_file_parts
        formatted_parts = []

        for i, part in enumerate(template_parts):
            is_folder = i < len(template_parts) - 1
            formatted_part = CustomStringFormatter().format(
                part,
                album=(tags.album, "Unknown Album"),
                album_artist=(tags.album_artist, "Unknown Artist"),
                artist=(tags.artist, "Unknown Artist"),
                composer=(tags.composer, "Unknown Composer"),
                date=(tags.date, "Unknown Date"),
                disc=(tags.disc, ""),
                disc_total=(tags.disc_total, ""),
                isrc=(tags.isrc, "Unknown ISRC"),
                label=(tags.label, "Unknown Label"),
                media_id=(tags.media_id, "Unknown Media ID"),
                media_type=(tags.media_type, "Unknown Media Type"),
                playlist_artist=(
                    (playlist_tags.artist if playlist_tags else None),
                    "Unknown Playlist Artist",
                ),
                playlist_id=(
                    (playlist_tags.id if playlist_tags else None),
                    "Unknown Playlist ID",
                ),
                playlist_title=(
                    (playlist_tags.title if playlist_tags else None),
                    "Unknown Playlist Title",
                ),
                playlist_track=(
                    (playlist_tags.track if playlist_tags else None),
                    "",
                ),
                producer=(tags.producer, "Unknown Producer"),
                publisher=(tags.publisher, "Unknown Publisher"),
                rating=(tags.rating, "Unknown Rating"),
                title=(tags.title, "Unknown Title"),
                track=(tags.track, ""),
                track_total=(tags.track_total, ""),
            )
            sanitized_formatted_part = self.sanitize_string(
                formatted_part,
                file_extension if not is_folder else None,
            )
            formatted_parts.append(sanitized_formatted_part)

        final_path = str(Path(self.output_path, *formatted_parts))

        logger.debug(f"Generated final path: {final_path}")

        return final_path

    def get_playlist_file_path(
        self,
        tags: PlaylistTags,
    ) -> str:
        template_parts = self.playlist_file_template.split("/")
        formatted_parts = []

        for i, part in enumerate(template_parts):
            is_folder = i < len(template_parts) - 1
            formatted_part = CustomStringFormatter().format(
                part,
                playlist_artist=(tags.artist, "Unknown Playlist Artist"),
                playlist_id=(tags.id, "Unknown Playlist ID"),
                playlist_title=(tags.title, "Unknown Playlist Title"),
                playlist_track=(tags.track, ""),
                playlist_track_total=(tags.track_total, ""),
            )
            sanitized_formatted_part = self.sanitize_string(
                formatted_part,
                ".m3u8" if not is_folder else None,
            )
            formatted_parts.append(sanitized_formatted_part)

        playlist_file_path = str(Path(self.output_path, *formatted_parts))

        logger.debug(f"Generated playlist file path: {playlist_file_path}")

        return playlist_file_path

    def update_playlist_file(
        self,
        playlist_file_path: str,
        final_path: str,
        playlist_track: int,
    ) -> None:
        playlist_file_path_obj = Path(playlist_file_path)
        final_path_obj = Path(final_path)
        output_dir_obj = Path(self.output_path)

        playlist_file_path_obj.parent.mkdir(parents=True, exist_ok=True)
        playlist_file_path_parent_parts_len = len(playlist_file_path_obj.parent.parts)
        output_path_parts_len = len(output_dir_obj.parts)

        final_path_relative = Path(
            ("../" * (playlist_file_path_parent_parts_len - output_path_parts_len)),
            *final_path_obj.parts[output_path_parts_len:],
        )
        playlist_file_lines = (
            playlist_file_path_obj.open("r", encoding="utf8").readlines()
            if playlist_file_path_obj.exists()
            else []
        )
        if len(playlist_file_lines) < playlist_track:
            playlist_file_lines.extend(
                "\n" for _ in range(playlist_track - len(playlist_file_lines))
            )

        playlist_file_lines[playlist_track - 1] = final_path_relative.as_posix() + "\n"
        with playlist_file_path_obj.open("w", encoding="utf8") as playlist_file:
            playlist_file.writelines(playlist_file_lines)

        logger.debug(
            f"Updated playlist file '{playlist_file_path}' with track {playlist_track}: {final_path_relative.as_posix()}"
        )

    def get_temp_path(
        self,
        media_id: str,
        folder_tag: str,
        file_tag: str,
        file_extension: str,
    ) -> str:
        return str(
            Path(self.temp_path)
            / TEMP_PATH_TEMPLATE.format(folder_tag)
            / (f"{media_id}_{file_tag}" + file_extension)
        )

    @alru_cache()
    async def get_cover_bytes(self, cover_url: str) -> bytes | None:
        async with httpx.AsyncClient() as client:
            response = await client.get(cover_url)

            if response.status_code == 200:
                return response.content

            if response.status_code == 404:
                return None

            response.raise_for_status()

    async def apply_tags(
        self,
        input_path: str,
        tags: MediaTags,
        cover_url: str | None,
    ) -> None:
        exclude_tags = self.exclude_tags or []
        filtered_tags = MediaTags(
            **{
                k: v
                for k, v in tags.__dict__.items()
                if v is not None and k not in exclude_tags
            }
        )

        cover_bytes = await self.get_cover_bytes(cover_url) if cover_url else None

        logger.debug(f"Applying tags to '{input_path}': {filtered_tags}")

        if input_path.lower().endswith(".ogg"):
            self._apply_ogg_tags(
                input_path,
                filtered_tags,
                cover_bytes,
                exclude_tags,
            )
        elif input_path.lower().endswith((".mp4", ".m4a")):
            self._apply_mp4_tags(
                input_path,
                filtered_tags,
                cover_bytes,
                exclude_tags,
            )
        elif input_path.lower().endswith(".flac"):
            self._apply_flac_tags(
                input_path,
                filtered_tags,
                cover_bytes,
                exclude_tags,
            )

    def _apply_ogg_tags(
        self,
        input_path: str,
        tags: MediaTags,
        cover_bytes: bytes | None,
        exclude_tags: list[str],
    ) -> None:
        file = OggVorbis(input_path)
        file.clear()
        skip_tagging = "all" in exclude_tags

        if not skip_tagging:
            ogg_tags = tags.as_vorbis_tags(self.date_tag_template)
            file.update(ogg_tags)

        if not skip_tagging and "cover" not in exclude_tags and cover_bytes:
            picture = Picture()
            picture.mime = "image/jpeg"
            picture.data = cover_bytes
            picture.type = 3
            picture.width, picture.height = Image.open(BytesIO(cover_bytes)).size
            file["METADATA_BLOCK_PICTURE"] = [
                base64.b64encode(picture.write()).decode("ascii")
            ]

        try:
            file.save()
        except OggVorbisHeaderError:
            pass

    def _apply_mp4_tags(
        self,
        input_path: str,
        tags: MediaTags,
        cover_bytes: bytes | None,
        exclude_tags: list[str],
    ) -> None:
        mp4 = MP4(input_path)
        mp4.clear()
        skip_tagging = "all" in exclude_tags

        if not skip_tagging:
            mp4_tags = tags.as_mp4_tags(self.date_tag_template)
            logger.debug(f"MP4 tags to apply: {mp4_tags}")
            mp4.update(mp4_tags)

        if not skip_tagging and "cover" not in exclude_tags and cover_bytes:
            mp4["covr"] = [
                MP4Cover(
                    data=cover_bytes,
                    imageformat=MP4Cover.FORMAT_JPEG,
                )
            ]

        mp4.save()

    def _apply_flac_tags(
        self,
        input_path: str,
        tags: MediaTags,
        cover_bytes: bytes | None,
        exclude_tags: list[str],
    ) -> None:
        flac = FLAC(input_path)
        flac.clear()
        skip_tagging = "all" in exclude_tags

        if not skip_tagging:
            flac_tags = tags.as_vorbis_tags(self.date_tag_template)
            flac.update(flac_tags)

        if not skip_tagging and "cover" not in exclude_tags and cover_bytes:
            picture = Picture()
            picture.mime = "image/jpeg"
            picture.data = cover_bytes
            picture.type = 3
            picture.width, picture.height = Image.open(BytesIO(cover_bytes)).size
            flac.add_picture(picture)

        flac.save()

    @staticmethod
    async def run_async_command(*args: str, silent: bool = False) -> None:
        if silent:
            additional_args = {
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
            }
        else:
            additional_args = {}

        proc = await asyncio.create_subprocess_exec(
            *args,
            **additional_args,
        )
        await proc.communicate()
        if proc.returncode != 0:
            raise Exception(f'"{args[0]}" exited with code {proc.returncode}')
