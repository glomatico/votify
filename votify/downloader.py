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
from .utils import prompt_path
import requests
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from mutagen.flac import Picture
from mutagen.mp4 import MP4, MP4Cover, MP4FreeForm
from mutagen.oggvorbis import OggVorbis, OggVorbisHeaderError
from PIL import Image
from pywidevine import PSSH, Cdm, Device

from .constants import (
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
        template_folder_music_video: str = "{artist}/{album}",
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
        self.wvd_path = prompt_path(
            is_file=True,
            initial_path=wvd_path,
            description="device.wvd",
            optional=True
        )
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
        self.cdm = None
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
        if self.wvd_path.exists():
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
            for item in album:
                t = item['track']
                track_id = t['uri'].split(':')[-1]
                download_queue.append({
                    'data': {
                        'trackUnion': {
                            'id': track_id,
                            'uri': t['uri'],
                            'name': t['name'],
                            'trackNumber': t['trackNumber'],
                            'duration': {
                                'totalMilliseconds': t['duration']['totalMilliseconds']
                            },
                            'is_playable': t.get('is_playable', True),
                            'artists': {
                                'items': [
                                    {
                                        'profile': {
                                            'name': t['artists']['items'][0]['profile']['name']
                                        }
                                    }
                                ]
                            }
                        }
                    }
                })
        elif media_type == "playlist":
                playlist = self.spotify_api.get_playlist(media_id)
                playlist_metadata = playlist
                if 'content' in playlist and 'items' in playlist['content']:
                    items_list = playlist['content']['items']
                else:
                    items_list = []
                for item in items_list:
                    if 'itemV2' not in item or 'data' not in item['itemV2']:
                        continue

                    t = item['itemV2']['data']

                    if 'uri' not in t:
                        continue

                    track_id = t['uri'].split(':')[-1]

                    duration_ms = 0
                    if 'duration' in t and isinstance(t['duration'], dict):
                        duration_ms = t['duration'].get('totalMilliseconds', 0)
                    elif 'trackDuration' in t and isinstance(t['trackDuration'], dict):
                        duration_ms = t['trackDuration'].get('totalMilliseconds', 0)

                    album_data = t.get('albumOfTrack', {})
                    if 'uri' in album_data and 'id' not in album_data:
                        album_data['id'] = album_data['uri'].split(':')[-1]

                    if 'date' in album_data and isinstance(album_data['date'], dict):
                        date_obj = album_data['date']
                        if 'isoString' in date_obj and date_obj['isoString']:
                            album_data['release_date'] = date_obj['isoString']
                            album_data['release_date_precision'] = 'day'
                        elif 'year' in date_obj and date_obj['year']:
                            album_data['release_date'] = str(date_obj['year'])
                            album_data['release_date_precision'] = 'year'

                    if 'release_date' not in album_data:
                        album_data['release_date'] = '1970-01-01'
                        album_data['release_date_precision'] = 'day'

                    artist_name = "Unknown Artist"
                    try:
                        if 'artists' in t and 'items' in t['artists'] and len(t['artists']['items']) > 0:
                            profile = t['artists']['items'][0].get('profile')
                            if profile:
                                artist_name = profile.get('name', "Unknown Artist")
                    except Exception:
                        pass

                    is_playable = t.get('isPlayable', True)

                    track_object = {
                        'data': {
                            'trackUnion': {
                                'id': track_id,
                                'uri': t['uri'],
                                '__typename': 'Track',
                                'name': t.get('name', 'Unknown Track'),
                                'trackNumber': t.get('trackNumber', 1),
                                'duration': {
                                    'totalMilliseconds': duration_ms
                                },
                                'isPlayable': is_playable,
                                'albumOfTrack': album_data,
                                'artists': {
                                    'items': [
                                        {
                                            'profile': {
                                                'name': artist_name
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    }

                    download_queue.append({
                        'media_metadata': track_object,
                        'playlist_metadata': playlist_metadata
                    })

        elif media_type == "track":
            download_queue.append(
                DownloadQueueItem(
                    media_metadata=self.spotify_api.get_track(media_id),
                )
            )
        elif media_type == "episode":
            episode = self.spotify_api.get_episode(media_id)

            podcast_name = "Unknown Podcast"
            podcast_uri = ""
            podcast_cover = ""

            if 'podcastV2' in episode and 'data' in episode['podcastV2']:
                p_data = episode['podcastV2']['data']
                podcast_name = p_data.get('name', 'Unknown Podcast')
                podcast_uri = p_data.get('uri', '')
                if 'coverArt' in p_data and 'sources' in p_data['coverArt']:
                    podcast_cover = p_data['coverArt']['sources'][0]['url']

            release_date = ""
            precision = ""
            if 'releaseDate' in episode and episode['releaseDate']:
                release_date = episode['releaseDate'].get('isoString')
                precision = episode['releaseDate'].get('isoString')

            cover_url = podcast_cover
            try:
                if 'coverArt' in episode and 'sources' in episode['coverArt']:
                    sources = episode['coverArt']['sources']
                    cover_url = max(sources, key=lambda x: x.get('width', 0))['url']
            except Exception:
                pass

            download_queue.append({
                'data': {
                    'trackUnion': {
                        'id': episode['id'],
                        'uri': episode['uri'],
                        'name': episode['name'],
                        'description': episode.get('description', ''),
                        'trackNumber': 1,
                        'duration': {
                            'totalMilliseconds': episode['duration']['totalMilliseconds']
                        },
                        'is_playable': episode.get('playability', {}).get('playable', True),

                        'release_date': release_date,
                        'release_date_precision': precision,

                        'cover_url': cover_url,

                        'artists': {
                            'items': [
                                {
                                    'profile': {
                                        'name': podcast_name
                                    }
                                }
                            ]
                        },

                        'albumOfTrack': {
                            'uri': podcast_uri,
                            'name': podcast_name,
                            'coverArt': {
                                'sources': [{'url': cover_url}]
                            },
                            'id': podcast_uri.split(':')[-1] if ':' in podcast_uri else None,
                            'release_date': release_date
                        }
                    }
                },
                'show_metadata': {
                    'name': podcast_name,
                    'publisher': 'Unknown',
                    'uri': podcast_uri
                }
            })


        elif media_type == "show":
            show = self.spotify_api.get_show(media_id)
            items_list = []
            if 'episodesV2' in show and 'items' in show['episodesV2']:
                items_list = show['episodesV2']['items']
            elif 'episodes' in show and 'items' in show['episodes']:
                items_list = show['episodes']['items']
            total_items = len(items_list)
            for index, item in enumerate(items_list):
                episode_raw = None
                if 'entity' in item and 'data' in item['entity']:
                    episode_raw = item['entity']['data']
                elif 'data' in item:
                    episode_raw = item['data']
                else:
                    episode_raw = item
                if not episode_raw or not isinstance(episode_raw, dict):
                    continue
                podcast_name = "Unknown Podcast"
                podcast_uri = ""
                if 'podcastV2' in episode_raw and 'data' in episode_raw['podcastV2']:
                    p_data = episode_raw['podcastV2']['data']
                    podcast_name = p_data.get('name', 'Unknown Podcast')
                    podcast_uri = p_data.get('uri', '')
                elif show.get('name'):
                    podcast_name = show.get('name')
                    podcast_uri = show.get('uri')
                cover_url = None
                if 'coverArt' in episode_raw and episode_raw['coverArt'].get('sources'):
                    try:
                        sources = episode_raw['coverArt']['sources']
                        cover_url = max(sources, key=lambda x: x.get('width', 0))['url']
                    except Exception:
                        pass
                release_date = ""
                precision = "day"
                if 'releaseDate' in episode_raw and isinstance(episode_raw['releaseDate'], dict):
                    release_date = episode_raw['releaseDate'].get('isoString')
                    if 'T' in release_date:
                        release_date = release_date.split('T')[0]
                    precision = episode_raw['releaseDate'].get('precision', 'day')
                elif 'release_date' in episode_raw:
                    release_date = episode_raw['release_date']
                current_track_number = total_items - index
                formatted_episode = {
                    'data': {
                        'trackUnion': {
                            'id': episode_raw.get('id'),
                            'uri': episode_raw.get('uri'),
                            'name': episode_raw.get('name'),
                            'description': episode_raw.get('description', ''),
                            'trackNumber': current_track_number,
                            'duration': {
                                'totalMilliseconds': episode_raw.get('duration', {}).get('totalMilliseconds', 0)
                            },
                            'is_playable': episode_raw.get('playability', {}).get('playable', True),
                            'release_date': release_date,
                            'release_date_precision': precision,
                            'cover_url': cover_url,
                            'artists': {'items': [{'profile': {'name': podcast_name}}]},
                            'albumOfTrack': {
                                'uri': podcast_uri,
                                'name': podcast_name,
                                'coverArt': {'sources': [{'url': cover_url}]},
                                'id': podcast_uri.split(':')[-1] if ':' in podcast_uri else None,
                                'release_date': release_date
                            }
                        }
                    }
                }
                current_show_metadata = {
                    'name': podcast_name,
                    'publisher': 'Unknown',
                    'uri': podcast_uri
                }
                download_queue.append(
                    DownloadQueueItem(
                        show_metadata=current_show_metadata,
                        media_metadata=formatted_episode,
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

    def get_cover_url(self, metadata: dict, cover_size_mapping: dict) -> str | None:
        if not isinstance(metadata, dict):
            return None
        images = None
        try:
            images = (
                metadata.get("data", {})
                .get("trackUnion", {})
                .get("albumOfTrack", {})
                .get("coverArt", {})
                .get("sources")
            )
        except AttributeError:
            pass

        if not images:
            images = metadata.get("images")

        if not images:
            images = metadata.get("coverArt", {}).get("sources")

        if not images:
            return None

        return self._get_cover_url(images, cover_size_mapping)

    def _get_cover_url(self, images_dict: list[dict], cover_size_mapping: dict) -> str:
        original_cover_url = images_dict[0]["url"]
        original_cover_id = original_cover_url.split("/")[-1]
        cover_key = cover_size_mapping[self.cover_size]
        cover_id = cover_key + original_cover_id[len(cover_key) :]
        cover_url = f"{original_cover_url.rpartition('/')[0]}/{cover_id}"
        return cover_url

    def get_media_id(self, media_metadata: dict) -> str:
        linked_from = media_metadata.get("linked_from")
        if linked_from:
            media_metadata = linked_from

        if "data" in media_metadata and isinstance(media_metadata["data"], dict):
            track_union = media_metadata["data"].get("trackUnion")
            if track_union and "id" in track_union:
                return track_union["id"]

        if "id" in media_metadata:
            return media_metadata["id"]

        if "itemV2" in media_metadata:
            return media_metadata["itemV2"]["data"]["id"]

        if "media_metadata" in media_metadata:
            nested = media_metadata["media_metadata"]
            if "data" in nested and "trackUnion" in nested["data"]:
                return nested["data"]["trackUnion"]["id"]
            if "id" in nested:
                return nested["id"]

        if "uri" in media_metadata:
            return media_metadata["uri"].split(":")[-1]

        raise ValueError("Could not find media ID in metadata")

    def get_playlist_tags(self, playlist_metadata: dict, playlist_track: int) -> dict:
        playlist_title = playlist_metadata.get("name", "Unknown Playlist")
        playlist_artist = "Unknown Artist"
        try:
            if "ownerV2" in playlist_metadata:
                playlist_artist = playlist_metadata['ownerV2']['data']['name']
        except (KeyError, TypeError):
            pass

        if playlist_artist == "Unknown Artist" and "owner" in playlist_metadata:
            owner_obj = playlist_metadata["owner"]
            if isinstance(owner_obj, dict):
                playlist_artist = owner_obj.get("display_name") or owner_obj.get("id", "Unknown Artist")
            elif isinstance(owner_obj, str):
                playlist_artist = owner_obj

        if playlist_artist == "Unknown Artist":
            playlist_artist = playlist_metadata.get("owner_name", "Unknown Artist")

        return {
            "playlist_artist": playlist_artist,
            "playlist_title": playlist_title,
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
            if tags.get("playlist_title"):
                template_folder = self.template_file_playlist.split("/")
            else:
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
            audio_quality: dict,
            track_name: str,
            download_music_video: str,
            download_podcast_videos: str,
    ) -> str:
        playback_info = self.spotify_api.get_track_playback_info(media_id, media_type)
        user_product = audio_quality.get('data', {}).get('me', {}).get('account', {}).get('product', 'free')

        if media_type == 'episode':
            target_bitrate = 128000
        else:
            target_bitrate = 256000 if user_product == 'PREMIUM' else 128000

        media_items = playback_info.get("media", {})
        if download_music_video == True or download_podcast_videos == True:
            for track_key, track_data in media_items.items():
                manifest = track_data['item']['manifest']
                if 'manifest_ids_video' in manifest:
                    video_file_id = manifest['manifest_ids_video'][0]['file_id']
                else:
                    logger.error("There is no video for this media.")
                    return
            return video_file_id
        else:
            if not media_items:
                raise ValueError("No available Track (Empty response)")

            expected_key = f"spotify:{media_type}:{media_id}"

            track_manifest = media_items.get(expected_key)

            if not track_manifest:
                track_manifest = list(media_items.values())[0]

            metadata = track_manifest.get("item", {}).get("metadata", {})
            server_name = metadata.get("name")

            if not server_name:
                raise ValueError(f"Track Unavailable: No name returned")

            req_clean = track_name.lower().strip()
            srv_clean = server_name.lower().strip()

            if (req_clean in srv_clean) or (srv_clean in req_clean):
                track_manifest = track_manifest
            else:
                raise ValueError(f"Track Unavailable: No name returned")

            try:
                audio_file_id = next(
                    f["file_id"]
                    for files in track_manifest["item"]["manifest"].values()
                    if isinstance(files, list)
                    for f in files
                    if isinstance(f, dict) and f.get("bitrate") == int(target_bitrate)
                )
            except StopIteration:
                raise ValueError(f"No audio file found with bitrate {target_bitrate}")

            return audio_file_id



    def get_playplay_decryption_key(self, file_id: str) -> bytes:
        raise NotImplementedError()

    def get_widevine_decryption_key(
        self,
        pssh: bytes,
        media_type: str,
    ) -> tuple[str, str]:
        try:
            if self.cdm is None:
                cmd = self.spotify_api.extract_keys_with_cdrm(pssh, media_type)
                key_id, decryption_key = cmd.split(':')
            else:
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
            try:
                self.cdm.close(cdm_session)
            except:
                pass
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
        if not release_date:
            return datetime.datetime(1970, 1, 1)

        if not release_date_precision:
            if len(release_date) == 4:
                release_date_precision = 'year'
            elif len(release_date) == 7:
                release_date_precision = 'month'
            else:
                release_date_precision = 'day'

        try:
            precision_key = str(release_date_precision).lower()
            fmt = self.RELEASE_DATE_PRECISION_MAPPING.get(precision_key, "%Y-%m-%d")
            return datetime.datetime.strptime(release_date, fmt)
        except (ValueError, TypeError, KeyError, AttributeError):
            for fmt in ["%Y", "%Y-%m", "%Y-%m-%d"]:
                try:
                    return datetime.datetime.strptime(release_date, fmt)
                except ValueError:
                    continue
        return datetime.datetime(1970, 1, 1)

    def get_release_date_tag(self, datetime_obj: datetime.datetime) -> str:
        return datetime_obj.strftime(self.date_tag_template)

    def get_artist_string(self, artist_list: list[dict]) -> str:
        if not artist_list:
            return ""

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
