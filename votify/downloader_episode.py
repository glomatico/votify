from __future__ import annotations

import logging
from pathlib import Path

from .constants import AAC_AUDIO_QUALITIES, COVER_SIZE_X_KEY_MAPPING_EPISODE
from .downloader_audio import DownloaderAudio
from .models import StreamInfoAudio

logger = logging.getLogger("votify")

class DownloaderEpisode(DownloaderAudio):
    def __init__(
        self,
        downloader_audio: DownloaderAudio,
    ):
        self.__dict__.update(downloader_audio.__dict__)

    def get_tags(
            self,
            episode_metadata: dict,
            show_metadata: dict,
    ) -> dict:
        try:
            release_date = episode_metadata.get("release_date")
            if release_date and "T" in release_date:
                release_date = release_date.split("T")[0]

            release_date_datetime_obj = self.downloader.get_release_date_datetime_obj(
                release_date,
                episode_metadata.get("release_date_precision", "day"),
            )
            tag_release_date = self.downloader.get_release_date_tag(release_date_datetime_obj)
            tag_release_year = str(release_date_datetime_obj.year)
        except Exception:
            tag_release_date = str(episode_metadata.get("release_date"))
            tag_release_year = tag_release_date.split("-")[0] if "-" in tag_release_date else "2024"

        track_number = 1
        try:
            if 'trackNumber' in episode_metadata and isinstance(episode_metadata['trackNumber'], int):
                track_number = episode_metadata['trackNumber']

            elif show_metadata and "episodes" in show_metadata and "items" in show_metadata["episodes"]:
                items = show_metadata["episodes"]["items"]
                total_items = len(items)

                for index, item in enumerate(items):
                    item_id = item.get('id')
                    if not item_id and 'entity' in item:
                        item_id = item['entity'].get('data', {}).get('id')

                    if item_id == episode_metadata['id']:
                        track_number = total_items - index
                        break
        except (KeyError, TypeError, IndexError):
            track_number = 1

        tags = {
            "album": show_metadata.get("name"),
            "description": episode_metadata.get("description"),
            "media_type": "Podcast",
            "publisher": show_metadata.get("publisher"),
            "rating": "Explicit" if episode_metadata.get("explicit") else "Unknown",
            "release_date": tag_release_date,
            "release_year": tag_release_year,
            "title": episode_metadata.get("name"),
            "track": track_number,
            "url": f"https://open.spotify.com/episode/{episode_metadata['id']}",
        }
        return tags

    def get_cover_path(self, final_path: Path) -> Path:
        return final_path.with_suffix(".jpg")

    def download(
        self,
        *args,
        **kwargs,
    ):
        try:
            self._download(*args, **kwargs)
        finally:
            self.downloader.cleanup_temp_path()

    def _download(
            self,
            episode_id: str,
            episode_metadata: dict = None,
            show_metadata: dict = None,
            gid_metadata: dict = None,
            stream_info: StreamInfoAudio = None,
            playlist_metadata: dict = None,
            playlist_track: int = None,
            product_name: dict = None,
            decryption_key: bytes = None,
    ):
        if not episode_metadata:
            episode_metadata = self.downloader.spotify_api.get_episode(episode_id)

        if 'data' in episode_metadata and 'trackUnion' in episode_metadata['data']:
            episode_metadata = episode_metadata['data']['trackUnion']

        if 'release_date' in episode_metadata:

            raw_date = str(episode_metadata['release_date'])
            if 'T' in raw_date:
                episode_metadata['release_date'] = raw_date.split('T')[0]

            precision = str(episode_metadata.get('release_date_precision', ''))
            if 'T' in precision or len(precision) > 10:
                episode_metadata['release_date_precision'] = 'day'

        else:

            if 'releaseDate' in episode_metadata and isinstance(episode_metadata['releaseDate'], dict):
                r_node = episode_metadata['releaseDate']
                episode_metadata['release_date'] = r_node.get('isoString', '1970-01-01').split('T')[0]
                episode_metadata['release_date_precision'] = r_node.get('precision', 'day')
            else:
                episode_metadata['release_date'] = '1970-01-01'
                episode_metadata['release_date_precision'] = 'year'

        if not show_metadata or show_metadata.get('name') == 'Unknown Show':
            logger.debug("Attempting to extract Show Metadata from alternative fields...")
            found_show_id = None

            try:
                if 'podcastV2' in episode_metadata:
                    uri = episode_metadata['podcastV2']['data']['uri']
                    found_show_id = uri.split(':')[-1]
            except (KeyError, IndexError, AttributeError):
                pass

            if not found_show_id and 'show' in episode_metadata:
                found_show_id = episode_metadata['show'].get('id')

            if found_show_id:
                logger.debug(f"Found Show ID: {found_show_id}, fetching details...")
                try:
                    show_metadata = self.downloader.spotify_api.get_show(found_show_id)
                except Exception as e:
                    logger.warning(f"Failed to fetch show details: {e}")

        if not show_metadata:
            show_name = "Unknown Show"
            try:
                show_name = episode_metadata['data']['trackUnion']['artists']['items'][0]['profile']['name']
            except:
                pass
            show_metadata = {'name': show_name, 'publisher': 'Unknown', 'episodes': {'items': []}}

        if not gid_metadata:
            logger.debug("Getting GID metadata")
            try:
                gid_metadata = self.downloader.get_gid_metadata(episode_id, "episode", None)
            except TypeError:
                gid_metadata = self.downloader.get_gid_metadata(episode_id, "episode")

        if not stream_info:
            logger.debug("Getting stream info")
            stream_info = self.get_stream_info(gid_metadata, product_name, "episode")

        if not stream_info.file_id:
            logger.warning("Episode not available, skipping")
            return

        tags = self.get_tags(episode_metadata, show_metadata)

        if playlist_metadata:
            tags = {**tags, **self.downloader.get_playlist_tags(playlist_metadata, playlist_track)}

        file_extension = self.get_file_extension()
        final_path = self.downloader.get_final_path("episode", tags, file_extension)

        cover_url = None

        if 'cover_url' in episode_metadata:
            cover_url = episode_metadata['cover_url']

        if not cover_url and 'coverArt' in episode_metadata and 'sources' in episode_metadata['coverArt']:
            try:
                cover_url = episode_metadata['coverArt']['sources'][0]['url']
            except (IndexError, KeyError, TypeError):
                pass

        if not cover_url and 'albumOfTrack' in episode_metadata:
            alb = episode_metadata['albumOfTrack']
            if 'coverArt' in alb and 'sources' in alb['coverArt']:
                try:
                    cover_url = alb['coverArt']['sources'][0]['url']
                except (IndexError, KeyError, TypeError):
                    pass

            elif 'images' in alb and isinstance(alb['images'], list) and len(alb['images']) > 0:
                cover_url = alb['images'][0]['url']


        if not cover_url:
            key_mapping = COVER_SIZE_X_KEY_MAPPING_EPISODE if 'COVER_SIZE_X_KEY_MAPPING_EPISODE' in globals() else COVER_SIZE_X_KEY_MAPPING_SONG
            cover_url = self.downloader.get_cover_url(episode_metadata, key_mapping)

        cover_path = self.get_cover_path(final_path)

        decrypted_path = None
        remuxed_path = None

        if final_path.exists() and not self.downloader.overwrite:
            logger.warning(f'Episode already exists at "{final_path}", skipping')
        else:
            if not decryption_key:
                decryption_key = self.get_decryption_key(stream_info)

            encrypted_path = self.downloader.get_file_temp_path(episode_id, "_encrypted", file_extension)
            decrypted_path = self.downloader.get_file_temp_path(episode_id, "_decrypted", file_extension)
            remuxed_path = self.downloader.get_file_temp_path(episode_id, "_remuxed", file_extension)

            self.download_stream_url(encrypted_path, stream_info.stream_url)
            self.decrypt(decryption_key, encrypted_path, decrypted_path, remuxed_path)

        media_temp_path = remuxed_path if remuxed_path and remuxed_path.exists() else decrypted_path

        self.downloader._final_processing(
            cover_path,
            cover_url,
            media_temp_path,
            final_path,
            tags,
            playlist_metadata,
            playlist_track,
        )
