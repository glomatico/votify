from __future__ import annotations

import base64
import datetime
import functools
import re
import shutil
import subprocess
from io import BytesIO
from pathlib import Path

import requests
from Crypto.Cipher import AES
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from mutagen.flac import Picture
from mutagen.oggvorbis import OggVorbis, OggVorbisHeaderError
from PIL import Image
from yt_dlp import YoutubeDL

from .constants import QUALITY_X_FORMAT_ID_MAPPING, VORBIS_TAGS_MAPPING
from .enums import DownloadMode, Quality
from .models import DownloadQueueItem, StreamInfo, UrlInfo
from .playplay_pb2 import (
    AUDIO_TRACK,
    Interactivity,
    PlayPlayLicenseRequest,
    PlayPlayLicenseResponse,
)
from .spotify_api import SpotifyApi
from .utils import check_response


class Downloader:
    ILLEGAL_CHARACTERS_REGEX = r'[\\/:*?"<>|;]'
    URL_RE = r"(album|playlist|track|show|episode|artist)/(\w{22})"
    ILLEGAL_CHARACTERS_REPLACEMENT = "_"
    RELEASE_DATE_PRECISION_MAPPING = {
        "year": "%Y",
        "month": "%Y-%m",
        "day": "%Y-%m-%d",
    }

    def __init__(
        self,
        spotify_api: SpotifyApi,
        quality: Quality = Quality.MEDIUM,
        output_path: Path = Path("./Spotify"),
        temp_path: Path = Path("./temp"),
        download_mode: DownloadMode = DownloadMode.YTDLP,
        aria2c_path: Path = "aria2c",
        unplayplay_path: Path = "unplayplay",
        template_folder_album: str = "{album_artist}/{album}",
        template_folder_compilation: str = "Compilations/{album}",
        template_file_single_disc: str = "{track:02d} {title}",
        template_file_multi_disc: str = "{disc}-{track:02d} {title}",
        template_folder_episode: str = "Podcasts/{album}",
        template_file_episode: str = "{track:02d} {title}",
        template_file_playlist: str = "Playlists/{playlist_artist}/{playlist_title}",
        date_tag_template: str = "%Y-%m-%dT%H:%M:%SZ",
        save_cover: bool = False,
        save_playlist: bool = False,
        overwrite: bool = False,
        exclude_tags: str = None,
        truncate: int = None,
        silence: bool = False,
    ):
        self.spotify_api = spotify_api
        self.quality = quality
        self.output_path = output_path
        self.temp_path = temp_path
        self.download_mode = download_mode
        self.aria2c_path = aria2c_path
        self.unplayplay_path = unplayplay_path
        self.template_folder_album = template_folder_album
        self.template_folder_compilation = template_folder_compilation
        self.template_file_single_disc = template_file_single_disc
        self.template_file_multi_disc = template_file_multi_disc
        self.template_folder_episode = template_folder_episode
        self.template_file_episode = template_file_episode
        self.template_file_playlist = template_file_playlist
        self.date_tag_template = date_tag_template
        self.save_cover = save_cover
        self.save_playlist = save_playlist
        self.overwrite = overwrite
        self.exclude_tags = exclude_tags
        self.truncate = truncate
        self.silence = silence
        self._set_binaries_full_path()
        self._set_exclude_tags_list()
        self._set_truncate()
        self._set_subprocess_additional_args()

    def _set_binaries_full_path(self):
        self.aria2c_path_full = shutil.which(self.aria2c_path)
        self.unplayplay_path_full = shutil.which(self.unplayplay_path)

    def _set_exclude_tags_list(self):
        self.exclude_tags_list = (
            [i.lower() for i in self.exclude_tags.split(",")]
            if self.exclude_tags is not None
            else []
        )

    def _set_truncate(self):
        if self.truncate is not None:
            self.truncate = None if self.truncate < 4 else self.truncate

    def _set_subprocess_additional_args(self):
        if self.silence:
            self.subprocess_additional_args = {
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
            }
        else:
            self.subprocess_additional_args = {}

    def get_url_info(self, url: str) -> UrlInfo:
        url_regex_result = re.search(self.URL_RE, url)
        if url_regex_result is None:
            raise Exception("Invalid URL")
        return UrlInfo(type=url_regex_result.group(1), id=url_regex_result.group(2))

    def get_download_queue(
        self,
        media_type: str,
        media_id: str,
    ) -> list[DownloadQueueItem]:
        download_queue = []
        if media_type == "album":
            album = self.spotify_api.get_album(media_id)
            for track in album["tracks"]["items"]:
                download_queue.append(
                    DownloadQueueItem(
                        album_metadata=album,
                        media_metadata=track,
                    )
                )
        elif media_type == "playlist":
            playlist = self.spotify_api.get_playlist(media_id)
            for track in playlist["tracks"]["items"]:
                if track["track"] is None:
                    continue
                download_queue.append(
                    DownloadQueueItem(
                        playlist_metadata=playlist,
                        media_metadata=track["track"],
                    )
                )
        elif media_type == "track":
            download_queue.append(
                DownloadQueueItem(
                    media_metadata=self.spotify_api.get_track(media_id),
                )
            )
        elif media_type == "episode":
            download_queue.append(
                DownloadQueueItem(
                    media_metadata=self.spotify_api.get_episode(media_id),
                )
            )
        elif media_type == "show":
            show = self.spotify_api.get_show(media_id)
            for episode in show["episodes"]["items"]:
                download_queue.append(
                    DownloadQueueItem(
                        show_metadata=show,
                        media_metadata=episode,
                    )
                )
        return download_queue

    def _filter_artist_albums(
        self,
        artist_albums: list[dict],
        album_type: str,
    ) -> list[dict]:
        return [album for album in artist_albums if album["album_type"] == album_type]

    def get_download_queue_from_artist(
        self,
        artist_id: str,
    ) -> list[DownloadQueueItem]:
        download_queue = []
        artist_albums = self.spotify_api.get_artist_albums(artist_id)
        artist_albums_all = {}
        for album_type in ["album", "single", "compilation", "appears_on"]:
            artist_albums_all[album_type] = self._filter_artist_albums(
                artist_albums["items"],
                album_type,
            )
        selected_album_type = inquirer.select(
            message=f"Select which album type to download for artist:",
            choices=[
                Choice(
                    name="Albums",
                    value="album",
                ),
                Choice(
                    name="Singles",
                    value="single",
                ),
                Choice(
                    name="Compilations",
                    value="compilation",
                ),
                Choice(
                    name="Collaborations",
                    value="appears_on",
                ),
            ],
            validate=lambda result: artist_albums_all.get(result),
            invalid_message="The artist doesn't have any albums of this type",
        ).execute()
        choices = [
            Choice(
                name=" | ".join(
                    [
                        f"{album['total_tracks']:03d}",
                        album["release_date"][:4],
                        album["name"],
                    ],
                ),
                value=album["id"],
            )
            for album in artist_albums_all[selected_album_type]
        ]
        selected = inquirer.select(
            message="Select which albums to download: (Total tracks | Release year | Album name)",
            choices=choices,
            multiselect=True,
        ).execute()
        for album_id in selected:
            download_queue.extend(
                self.get_download_queue(
                    "album",
                    album_id,
                )
            )
        return download_queue

    def get_media_id(self, media_metadata: dict) -> str:
        return (media_metadata.get("linked_from") or media_metadata)["id"]

    def get_playlist_tags(self, playlist_metadata: dict, playlist_track: int) -> dict:
        return {
            "playlist_artist": playlist_metadata["owner"]["display_name"],
            "playlist_title": playlist_metadata["name"],
            "playlist_track": playlist_track,
        }

    def get_playlist_file_path(
        self,
        tags: dict,
    ):
        template_file = self.template_file_playlist.split("/")
        return Path(
            self.output_path,
            *[
                self.get_sanitized_string(i.format(**tags), True)
                for i in template_file[0:-1]
            ],
            *[
                self.get_sanitized_string(template_file[-1].format(**tags), False)
                + ".m3u8"
            ],
        )

    def get_lrc_path(self, final_path: Path) -> Path:
        return final_path.with_suffix(".lrc")

    def save_lrc(self, lrc_path: Path, lyrics_synced: str):
        if lyrics_synced:
            lrc_path.parent.mkdir(parents=True, exist_ok=True)
            lrc_path.write_text(lyrics_synced, encoding="utf8")

    def get_final_path(self, media_type: str, tags: dict, file_extension: str) -> Path:
        if media_type == "track":
            template_folder = (
                self.template_folder_compilation.split("/")
                if tags.get("compilation")
                else self.template_folder_album.split("/")
            )
            template_file = (
                self.template_file_multi_disc.split("/")
                if tags["disc_total"] > 1
                else self.template_file_single_disc.split("/")
            )
        elif media_type == "episode":
            template_folder = self.template_folder_episode.split("/")
            template_file = self.template_file_episode.split("/")
        else:
            raise RuntimeError()
        template_final = template_folder + template_file
        return Path(
            self.output_path,
            *[
                self.get_sanitized_string(i.format(**tags), True)
                for i in template_final[0:-1]
            ],
            (
                self.get_sanitized_string(template_final[-1].format(**tags), False)
                + file_extension
            ),
        )

    def update_playlist_file(
        self,
        playlist_file_path: Path,
        final_path: Path,
        playlist_track: int,
    ):
        playlist_file_path.parent.mkdir(parents=True, exist_ok=True)
        playlist_file_path_parent_parts_len = len(playlist_file_path.parent.parts)
        output_path_parts_len = len(self.output_path.parts)
        final_path_relative = Path(
            ("../" * (playlist_file_path_parent_parts_len - output_path_parts_len)),
            *final_path.parts[output_path_parts_len:],
        )
        playlist_file_lines = (
            playlist_file_path.open("r", encoding="utf8").readlines()
            if playlist_file_path.exists()
            else []
        )
        if len(playlist_file_lines) < playlist_track:
            playlist_file_lines.extend(
                "\n" for _ in range(playlist_track - len(playlist_file_lines))
            )
        playlist_file_lines[playlist_track - 1] = final_path_relative.as_posix() + "\n"
        with playlist_file_path.open("w", encoding="utf8") as playlist_file:
            playlist_file.writelines(playlist_file_lines)

    def get_audio_file(
        self,
        audio_files: list[dict],
    ) -> tuple[Quality, dict] | tuple[None, None]:
        qualities = list(Quality)
        start_index = qualities.index(self.quality)
        for quality in qualities[start_index:]:
            for audio_file in audio_files:
                if audio_file["format"] == QUALITY_X_FORMAT_ID_MAPPING[quality]:
                    return quality, audio_file
        return None, None

    def get_gid_metadata(
        self,
        media_id: str,
        media_type: str,
    ) -> dict:
        gid = self.spotify_api.media_id_to_gid(media_id)
        return self.spotify_api.get_gid_metadata(gid, media_type)

    def get_stream_info(
        self,
        gid_metadata: dict,
        media_type: str,
    ) -> StreamInfo:
        stream_info = StreamInfo()
        if media_type == "track":
            audio_files = gid_metadata.get("file")
        elif media_type == "episode":
            audio_files = gid_metadata.get("audio")
        else:
            raise RuntimeError()
        audio_files = audio_files or gid_metadata.get("alternative")
        if not audio_files:
            return stream_info
        if audio_files[0].get("gid"):
            audio_files = audio_files[0]["file"]
        quality, audio_file = self.get_audio_file(audio_files)
        if not audio_file:
            return stream_info
        file_id = audio_file["file_id"]
        stream_url = self.spotify_api.get_stream_urls(file_id)["cdnurl"][0]
        stream_info.stream_url = stream_url
        stream_info.file_id = file_id
        stream_info.quality = quality
        return stream_info

    def get_decryption_key(self, file_id: str) -> bytes:
        playplay_license_request = PlayPlayLicenseRequest(
            version=2,
            token=bytes.fromhex("01e132cae527bd21620e822f58514932"),
            interactivity=Interactivity.INTERACTIVE,
            content_type=AUDIO_TRACK,
        )
        playplay_license_response_bytes = self.spotify_api.get_playplay_license(
            file_id,
            playplay_license_request.SerializeToString(),
        )
        playplay_license_response = PlayPlayLicenseResponse()
        playplay_license_response.ParseFromString(playplay_license_response_bytes)
        obfuscated = playplay_license_response.obfuscated_key.hex()
        output = subprocess.check_output(
            [
                self.unplayplay_path_full,
                file_id,
                obfuscated,
            ],
            shell=False,
        )
        key = bytes.fromhex(output.strip().decode("utf-8"))
        assert key
        return key

    def download_stream_url(self, input_path: Path, stream_url: str):
        if self.download_mode == DownloadMode.YTDLP:
            self.download_stream_url_ytdlp(input_path, stream_url)
        elif self.download_mode == DownloadMode.ARIA2C:
            self.download_stream_url_aria2c(input_path, stream_url)

    def download_stream_url_ytdlp(self, input_path: Path, stream_url: str) -> None:
        with YoutubeDL(
            {
                "quiet": True,
                "no_warnings": True,
                "outtmpl": str(input_path),
                "allow_unplayable_formats": True,
                "fixup": "never",
                "allowed_extractors": ["generic"],
                "noprogress": self.silence,
            }
        ) as ydl:
            ydl.download(stream_url)

    def download_stream_url_aria2c(self, input_path: Path, stream_url: str) -> None:
        input_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                self.aria2c_path_full,
                "--no-conf",
                "--download-result=hide",
                "--console-log-level=error",
                "--summary-interval=0",
                "--file-allocation=none",
                stream_url,
                "--out",
                input_path,
            ],
            check=True,
            **self.subprocess_additional_args,
        )
        print("\r", end="")

    def decrypt(
        self,
        decryption_key: bytes,
        encrypted_path: Path,
        decrypted_path: Path,
    ):
        cipher = AES.new(
            decryption_key,
            AES.MODE_CTR,
            nonce=bytes.fromhex("72e067fbddcbcf77"),
            initial_value=bytes.fromhex("ebe8bc643f630d93"),
        )
        skip = 167
        with decrypted_path.open("wb") as decrypted_file:
            with encrypted_path.open("rb") as encrypted_file:
                decrypted_file.write(cipher.decrypt(encrypted_file.read())[skip:])

    def get_sanitized_string(self, dirty_string: str, is_folder: bool) -> str:
        dirty_string = re.sub(
            self.ILLEGAL_CHARACTERS_REGEX,
            self.ILLEGAL_CHARACTERS_REPLACEMENT,
            dirty_string,
        )
        if is_folder:
            dirty_string = dirty_string[: self.truncate]
            if dirty_string.endswith("."):
                dirty_string = dirty_string[:-1] + self.ILLEGAL_CHARACTERS_REPLACEMENT
        else:
            if self.truncate is not None:
                dirty_string = dirty_string[: self.truncate - 4]
        return dirty_string.strip()

    def get_release_date_datetime_obj(
        self,
        release_date: str,
        release_date_precision: str,
    ) -> datetime.datetime:
        return datetime.datetime.strptime(
            release_date,
            self.RELEASE_DATE_PRECISION_MAPPING[release_date_precision],
        )

    def get_release_date_tag(self, datetime_obj: datetime.datetime) -> str:
        return datetime_obj.strftime(self.date_tag_template)

    def get_artist_string(self, artist_list: list[dict]) -> str:
        if len(artist_list) == 1:
            return artist_list[0]["name"]
        return (
            ", ".join(i["name"] for i in artist_list[:-1])
            + f' & {artist_list[-1]["name"]}'
        )

    def get_cover_url(self, metadata: dict) -> str | None:
        if not metadata.get("images"):
            return None
        return self._get_cover_url(metadata["images"])

    def _get_cover_url(self, images_dict: list[dict]) -> str:
        return max(images_dict, key=lambda img: img["height"])["url"]

    def get_encrypted_path(
        self,
        track_id: str,
    ) -> Path:
        return self.temp_path / (f"{track_id}_encrypted.ogg")

    def get_decrypted_path(
        self,
        track_id: str,
    ) -> Path:
        return self.temp_path / (f"{track_id}_decrypted.ogg")

    def apply_tags(
        self,
        input_path: Path,
        tags: dict,
        cover_url: str,
    ) -> None:
        file = OggVorbis(input_path)
        file.clear()
        ogg_tags = {
            v: str(tags[k])
            for k, v in VORBIS_TAGS_MAPPING.items()
            if k not in self.exclude_tags_list and tags.get(k) is not None
        }
        if "cover" not in self.exclude_tags_list and cover_url:
            cover_bytes = self.get_response_bytes(cover_url)
            picture = Picture()
            picture.mime = "image/jpeg"
            picture.data = cover_bytes
            picture.type = 3
            picture.width, picture.height = Image.open(BytesIO(cover_bytes)).size
            ogg_tags["METADATA_BLOCK_PICTURE"] = base64.b64encode(
                picture.write()
            ).decode("ascii")
        file.update(ogg_tags)
        try:
            file.save()
        except OggVorbisHeaderError:
            pass

    @staticmethod
    @functools.lru_cache()
    def get_response_bytes(url: str) -> bytes:
        response = requests.get(url)
        check_response(response)
        return response.content

    def move_to_final_path(self, input_path: Path, final_path: Path):
        final_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(input_path, final_path)

    @functools.lru_cache()
    def save_cover_file(self, cover_path: Path, cover_url: str):
        if cover_url is not None:
            cover_path.parent.mkdir(parents=True, exist_ok=True)
            cover_path.write_bytes(self.get_response_bytes(cover_url))

    def cleanup_temp_path(self):
        shutil.rmtree(self.temp_path)
