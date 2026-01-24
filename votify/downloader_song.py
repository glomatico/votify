from __future__ import annotations

import datetime
import logging
from pathlib import Path

from .constants import COVER_SIZE_X_KEY_MAPPING_SONG
from .downloader_audio import DownloaderAudio
from .models import Lyrics, StreamInfoAudio

logger = logging.getLogger("votify")


class DownloaderSong(DownloaderAudio):
    def __init__(
        self,
        downloader_audio: DownloaderAudio,
        lrc_only: bool = False,
        no_lrc: bool = False,
    ):
        self.__dict__.update(downloader_audio.__dict__)
        self.lrc_only = lrc_only
        self.no_lrc = no_lrc

    def get_tags(
            self,
            track_metadata: dict,
            album_metadata: list,
            track_credits: dict,
            lyrics_unsynced: str,
    ) -> dict:
        track_info = track_metadata.get("data", {}).get("trackUnion", {})
        album_info = track_info.get("albumOfTrack", {})

        external_url = track_info.get("sharingInfo", {}).get("shareUrl")

        isrc = None

        release_date_iso = album_info.get("date", {}).get("isoString")
        precision_raw = album_info.get("date", {}).get("precision")

        precision = precision_raw.lower() if precision_raw else "day"

        release_date_str = release_date_iso.split("T")[0] if release_date_iso else None

        release_date_datetime_obj = self.downloader.get_release_date_datetime_obj(
            release_date_str,
            precision,
        )

        track_artists = []

        raw_artist_items = track_info.get("firstArtist", {}).get("items", [])

        other_artist_items = track_info.get("otherArtists", {}).get("items", [])

        all_artist_items = raw_artist_items + other_artist_items

        for item in all_artist_items:
            name = item.get("profile", {}).get("name")
            if name:
                track_artists.append({"name": name})

        if not track_artists:
            alt_artists = track_info.get("artists", {}).get("items", [])
            for item in alt_artists:
                name = item.get("profile", {}).get("name") or item.get("name")
                if name:
                    track_artists.append({"name": name})

        if not track_artists:
            track_artists = [{"name": "Unknown Artist"}]

        album_artists = track_artists

        def get_credits_artists(role_title):
            try:
                role = next(
                    r for r in track_credits.get("roleCredits", [])
                    if r.get("roleTitle") == role_title
                )
                return role.get("artists", [])
            except StopIteration:
                return []

        producers = get_credits_artists("Producers")
        composers = get_credits_artists("Writers")

        current_uri = track_info.get("uri")

        current_track_entry = next(
            (item.get("track", {}) for item in album_metadata if item.get("track", {}).get("uri") == current_uri),
            {}
        )

        disc_number = current_track_entry.get("discNumber", 1)

        try:
            disc_total = max(
                (item.get("track", {}).get("discNumber", 1) for item in album_metadata),
                default=1
            )
        except Exception:
            disc_total = 1

        track_total = album_info.get("tracks", {}).get("totalCount")
        if not track_total:
            track_total = len(album_metadata)

        copyright_text = next(
            (c["text"] for c in album_info.get("copyright", {}).get("items", []) if c.get("type") == "P"),
            None
        )
        label = album_info.get("courtesyLine") or album_info.get("label")

        tags = {
            "album": album_info.get("name"),
            "album_artist": self.downloader.get_artist_string(album_artists),
            "artist": self.downloader.get_artist_string(track_artists),
            "compilation": False,
            "composer": (
                self.downloader.get_artist_string(composers) if composers else None
            ),
            "copyright": copyright_text,
            "disc": int(disc_number),
            "disc_total": int(disc_total),
            "isrc": isrc,
            "label": label,
            "lyrics": lyrics_unsynced,
            "media_type": "Song",
            "producer": (
                self.downloader.get_artist_string(producers) if producers else None
            ),
            "rating": "Explicit" if track_info.get("contentRating", {}).get("label") == "EXPLICIT" else "Unknown",
            "release_date": self.downloader.get_release_date_tag(
                release_date_datetime_obj
            ),
            "release_year": str(release_date_datetime_obj.year),
            "title": track_info.get("name"),
            "track": int(track_info.get("trackNumber", 1)),
            "track_total": int(track_total),
            "url": external_url,
        }
        return tags

    def get_lyrics_synced_timestamp_lrc(self, time: int) -> str:
        lrc_timestamp = datetime.datetime.fromtimestamp(
            time / 1000.0, tz=datetime.timezone.utc
        )
        return lrc_timestamp.strftime("%M:%S.%f")[:-4]

    def get_lyrics(self, track_id: str) -> Lyrics:
        lyrics = Lyrics()
        raw_lyrics = self.downloader.spotify_api.get_lyrics(track_id)
        if raw_lyrics is None:
            return lyrics
        lyrics.synced = ""
        lyrics.unsynced = ""
        for line in raw_lyrics["lyrics"]["lines"]:
            if raw_lyrics["lyrics"]["syncType"] == "LINE_SYNCED":
                lyrics.synced += f'[{self.get_lyrics_synced_timestamp_lrc(int(line["startTimeMs"]))}]{line["words"]}\n'
            lyrics.unsynced += f'{line["words"]}\n'
        lyrics.unsynced = lyrics.unsynced[:-1]
        return lyrics

    def get_cover_path(self, final_path: Path) -> Path:
        return final_path.parent / "Cover.jpg"

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
            track_id: str,
            track_metadata: dict = None,
            album_metadata: dict = None,
            gid_metadata: dict = None,
            stream_info: StreamInfoAudio = None,
            playlist_metadata: dict = None,
            product_name: dict = None,
            playlist_track: int = None,
            decryption_key: bytes = None,
    ):
        if not album_metadata:
            logger.debug("Getting track metadata")
            track_metadata = self.downloader.spotify_api.get_track(track_id)

        try:
            current_date = track_metadata['data']['trackUnion']['albumOfTrack'].get('release_date')

            if current_date == '1970-01-01':
                fresh_data = self.downloader.spotify_api.get_track(track_id)

                real_date = None
                real_precision = 'day'
                real_album_name = None

                if 'album' in fresh_data:
                    real_date = fresh_data['album']['release_date']
                    real_precision = fresh_data['album'].get('release_date_precision', 'day')
                    real_album_name = fresh_data['album']['name']

                elif 'data' in fresh_data:
                    src_album = fresh_data['data']['trackUnion']['albumOfTrack']
                    if 'date' in src_album and 'isoString' in src_album['date']:
                        real_date = src_album['date']['isoString']
                        real_precision = 'day'

                if real_date and not str(real_date).startswith('1970'):
                    track_metadata['data']['trackUnion']['albumOfTrack']['release_date'] = real_date
                    track_metadata['data']['trackUnion']['albumOfTrack']['release_date_precision'] = real_precision

                    if not album_metadata:
                        album_metadata = {}

                    album_metadata['release_date'] = real_date
                    album_metadata['release_date_precision'] = real_precision
                    if real_album_name:
                        album_metadata['name'] = real_album_name

        except Exception as e:
            pass

        if not album_metadata:
            logger.debug("Getting album metadata")
            try:
                alb_node = track_metadata['data']['trackUnion']['albumOfTrack']
                album_id = alb_node['id']
                album_metadata = self.downloader.spotify_api.get_album(album_id)
            except (KeyError, TypeError):
                pass

        if not gid_metadata:
            logger.debug("Getting GID metadata")
            try:
                gid_metadata = self.downloader.get_gid_metadata(track_id, "track", product_name)
            except TypeError:
                gid_metadata = self.downloader.get_gid_metadata(track_id, "track")

            if gid_metadata.get("original_video"):
                logger.warning("Track is a music video, skipping.")
                return

        if not stream_info:
            logger.debug("Getting stream info")
            stream_info = self.get_stream_info(gid_metadata, product_name, "track")

        if not stream_info.file_id:
            logger.warning(
                "Track is not available on Spotify's "
                "servers and no alternative found, skipping"
            )
            return

        if stream_info.quality != self.audio_quality:
            logger.warning(f"Quality has been changed to {stream_info.quality}")

        if gid_metadata:
            logger.debug("Getting lyrics")
            lyrics = self.get_lyrics(track_id)
        else:
            lyrics = Lyrics()

        logger.debug("Getting track credits")
        track_credits = self.downloader.spotify_api.get_track_credits(track_id)

        tags = self.get_tags(
            track_metadata,
            album_metadata,
            track_credits,
            lyrics.unsynced,
        )

        if playlist_metadata:
            tags = {
                **tags,
                **self.downloader.get_playlist_tags(
                    playlist_metadata,
                    playlist_track,
                ),
            }

        file_extension = self.get_file_extension()
        final_path = self.downloader.get_final_path(
            "track",
            tags,
            file_extension,
        )
        lrc_path = self.downloader.get_lrc_path(final_path)
        cover_path = self.get_cover_path(final_path)
        cover_url = self.downloader.get_cover_url(
            track_metadata,
            COVER_SIZE_X_KEY_MAPPING_SONG,
        )

        decrypted_path = None
        remuxed_path = None

        if self.lrc_only:
            pass
        elif final_path.exists() and not self.downloader.overwrite:
            logger.warning(f'Track already exists at "{final_path}", skipping')
        else:
            if not decryption_key:
                logger.debug("Getting decryption key")
                decryption_key = self.get_decryption_key(stream_info)
            encrypted_path = self.downloader.get_file_temp_path(
                track_id,
                "_encrypted",
                file_extension,
            )
            decrypted_path = self.downloader.get_file_temp_path(
                track_id,
                "_decrypted",
                file_extension,
            )
            remuxed_path = self.downloader.get_file_temp_path(
                track_id,
                "_remuxed",
                file_extension,
            )
            logger.debug(f'Downloading to "{encrypted_path}"')
            self.download_stream_url(encrypted_path, stream_info.stream_url)
            logger.debug(
                f'Decrypting to "{decrypted_path}" and remuxing to "{remuxed_path}"'
            )
            self.decrypt(
                decryption_key,
                encrypted_path,
                decrypted_path,
                remuxed_path,
            )

        if self.no_lrc:
            pass
        elif lrc_path.exists() and not self.downloader.overwrite:
            logger.debug(f'Synced lyrics already exists at "{lrc_path}", skipping')
        else:
            logger.debug(f'Saving synced lyrics to "{lrc_path}"')
            lyrics = None

        media_temp_path = (
            remuxed_path
            if remuxed_path is not None and remuxed_path.exists()
            else decrypted_path
        )

        self.downloader._final_processing(
            cover_path,
            cover_url,
            media_temp_path,
            final_path,
            tags,
            playlist_metadata,
            playlist_track,
        )
