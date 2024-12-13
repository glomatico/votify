from __future__ import annotations

import base64
import datetime
import functools
import logging
import re
import shutil
import subprocess
from io import BytesIO
from pathlib import Path

import requests
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from mutagen.flac import Picture
from mutagen.mp4 import MP4, MP4Cover, MP4FreeForm
from mutagen.oggvorbis import OggVorbis, OggVorbisHeaderError
from PIL import Image
from pywidevine import PSSH, Cdm, Device

from .constants import (
    COVER_SIZE_X_KEY_MAPPING_AUDIO,
    MEDIA_TYPE_MP4_MAPPING,
    MP4_TAGS_MAP,
    VORBIS_TAGS_MAPPING,
)
from .enums import CoverSize
from .models import DownloadQueueItem, UrlInfo
from .spotify_api import SpotifyApi
from .utils import check_response

logger = logging.getLogger("votify")


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
        output_path: Path = Path("./Spotify"),
        temp_path: Path = Path("./temp"),
        wvd_path: Path = Path("./device.wvd"),
        aria2c_path: str = "aria2c",
        ffmpeg_path: str = "ffmpeg",
        mp4box_path: str = "mp4box",
        mp4decrypt_path: str = "mp4decrypt",
        packager_path: str = "packager",
        template_folder_album: str = "{album_artist}/{album}",
        template_folder_compilation: str = "Compilations/{album}",
        template_file_single_disc: str = "{track:02d} {title}",
        template_file_multi_disc: str = "{disc}-{track:02d} {title}",
        template_folder_episode: str = "Podcasts/{album}",
        template_file_episode: str = "{track:02d} {title}",
        template_folder_music_video: str = "{artist}/Unknown Album",
        template_file_music_video: str = "{title}",
        template_file_playlist: str = "Playlists/{playlist_artist}/{playlist_title}",
        date_tag_template: str = "%Y-%m-%dT%H:%M:%SZ",
        cover_size: CoverSize = CoverSize.EXTRA_LARGE,
        save_cover: bool = False,
        save_playlist: bool = False,
        overwrite: bool = False,
        exclude_tags: str = None,
        truncate: int = None,
        silence: bool = False,
        skip_cleanup: bool = False,
    ):
        self.spotify_api = spotify_api
        self.output_path = output_path
        self.temp_path = temp_path
        self.wvd_path = wvd_path
        self.aria2c_path = aria2c_path
        self.ffmpeg_path = ffmpeg_path
        self.mp4box_path = mp4box_path
        self.mp4decrypt_path = mp4decrypt_path
        self.packager_path = packager_path
        self.template_folder_album = template_folder_album
        self.template_folder_compilation = template_folder_compilation
        self.template_file_single_disc = template_file_single_disc
        self.template_file_multi_disc = template_file_multi_disc
        self.template_folder_episode = template_folder_episode
        self.template_file_episode = template_file_episode
        self.template_folder_music_video = template_folder_music_video
        self.template_file_music_video = template_file_music_video
        self.template_file_playlist = template_file_playlist
        self.date_tag_template = date_tag_template
        self.cover_size = cover_size
        self.save_cover = save_cover
        self.save_playlist = save_playlist
        self.overwrite = overwrite
        self.exclude_tags = exclude_tags
        self.truncate = truncate
        self.silence = silence
        self.skip_cleanup = skip_cleanup
        self._set_binaries_full_path()
        self._set_exclude_tags_list()
        self._set_truncate()
        self._set_subprocess_additional_args()

    def _set_binaries_full_path(self):
        self.aria2c_path_full = shutil.which(self.aria2c_path)
        self.ffmpeg_path_full = shutil.which(self.ffmpeg_path)
        self.mp4box_path_full = shutil.which(self.mp4box_path)
        self.mp4decrypt_path_full = shutil.which(self.mp4decrypt_path)
        self.packager_path_full = shutil.which(self.packager_path)

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

    def set_cdm(self) -> None:
        self.cdm = Cdm.from_device(Device.load(self.wvd_path))

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
        elif media_type == "music-video":
            template_folder = self.template_folder_music_video.split("/")
            template_file = self.template_file_music_video.split("/")
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

    def get_gid_metadata(
        self,
        media_id: str,
        media_type: str,
    ) -> dict:
        gid = self.spotify_api.media_id_to_gid(media_id)
        return self.spotify_api.get_gid_metadata(gid, media_type)

    def get_playplay_decryption_key(self, file_id: str) -> bytes:
        raise NotImplementedError()

    def get_widevine_decryption_key(
        self,
        pssh: bytes,
        media_type: str,
    ) -> tuple[str, str]:
        try:
            pssh = PSSH(pssh)
            cdm_session = self.cdm.open()
            challenge = self.cdm.get_license_challenge(cdm_session, pssh)
            license = self.spotify_api.get_widevine_license(challenge, media_type)
            self.cdm.parse_license(cdm_session, license)
            keys = next(
                i for i in self.cdm.get_keys(cdm_session) if i.type == "CONTENT"
            )
            decryption_key = keys.key.hex()
            key_id = keys.kid.hex
        finally:
            self.cdm.close(cdm_session)
        return key_id, decryption_key

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

    def get_file_temp_path(
        self,
        track_id: str,
        extra_string: str,
        extension: str,
    ) -> Path:
        return self.temp_path / (track_id + extra_string + extension)

    def apply_tags_ogg(
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

    def apply_tags_mp4(self, fixed_location: Path, tags: dict, cover_url: str):
        to_apply_tags = [
            tag_name
            for tag_name in tags.keys()
            if tag_name not in self.exclude_tags_list
        ]
        mp4_tags = {}
        for tag_name in to_apply_tags:
            if tags.get(tag_name) is None:
                continue
            if tag_name in ("disc", "disc_total"):
                if mp4_tags.get("disk") is None:
                    mp4_tags["disk"] = [[0, 0]]
                if tag_name == "disc":
                    mp4_tags["disk"][0][0] = tags[tag_name]
                elif tag_name == "disc_total":
                    mp4_tags["disk"][0][1] = tags[tag_name]
            elif tag_name in ("track", "track_total"):
                if mp4_tags.get("trkn") is None:
                    mp4_tags["trkn"] = [[0, 0]]
                if tag_name == "track":
                    mp4_tags["trkn"][0][0] = tags[tag_name]
                elif tag_name == "track_total":
                    mp4_tags["trkn"][0][1] = tags[tag_name]
            elif tag_name == "compilation":
                mp4_tags["cpil"] = tags["compilation"]
            elif tag_name == "isrc":
                mp4_tags["----:com.apple.iTunes:ISRC"] = [
                    MP4FreeForm(tags["isrc"].encode("utf-8"))
                ]
            elif tag_name == "label":
                mp4_tags["----:com.apple.iTunes:LABEL"] = [
                    MP4FreeForm(tags["label"].encode("utf-8"))
                ]
            elif tag_name == "rating":
                mp4_tags["rtng"] = [1] if tags[tag_name] == "Explicit" else [0]
            elif tag_name == "media_type":
                mp4_tags["stik"] = [MEDIA_TYPE_MP4_MAPPING[tags[tag_name]]]
            elif MP4_TAGS_MAP.get(tag_name) is not None:
                mp4_tags[MP4_TAGS_MAP[tag_name]] = [tags[tag_name]]
        if "cover" not in self.exclude_tags_list and cover_url is not None:
            mp4_tags["covr"] = [
                MP4Cover(
                    self.get_response_bytes(cover_url), imageformat=MP4Cover.FORMAT_JPEG
                )
            ]
        mp4 = MP4(fixed_location)
        mp4.clear()
        mp4.update(mp4_tags)
        mp4.save()

    def _final_processing(
        self,
        cover_path: Path,
        cover_url: str,
        media_temp_path: Path,
        final_path: Path,
        tags: dict,
        playlist_metadata: dict,
        playlist_track: int,
    ):
        if self.save_cover and cover_path.exists() and not self.overwrite:
            logger.debug(f'Cover already exists at "{cover_path}", skipping')
        elif self.save_cover and cover_url is not None:
            logger.debug(f'Saving cover to "{cover_path}"')
            self.save_cover_file(cover_path, cover_url)
        if media_temp_path:
            logger.debug("Applying tags")
            if media_temp_path.suffix in (".mp4", ".m4a"):
                self.apply_tags_mp4(media_temp_path, tags, cover_url)
            elif media_temp_path.suffix == ".ogg":
                self.apply_tags_ogg(media_temp_path, tags, cover_url)
            logger.debug(f'Moving to "{final_path}"')
            self.move_to_final_path(media_temp_path, final_path)
        if self.save_playlist and playlist_metadata:
            playlist_file_path = self.get_playlist_file_path(tags)
            logger.debug(f'Updating M3U8 playlist from "{playlist_file_path}"')
            self.update_playlist_file(
                playlist_file_path,
                final_path,
                playlist_track,
            )

    def cleanup_temp_path(self):
        if self.temp_path.exists() and not self.skip_cleanup:
            logger.debug(f'Cleaning up "{self.temp_path}"')
            shutil.rmtree(self.temp_path)

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
