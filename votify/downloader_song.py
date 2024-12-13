from __future__ import annotations

import datetime
import logging
from pathlib import Path

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
        album_metadata: dict,
        track_credits: dict,
        lyrics_unsynced: str,
    ) -> dict:
        external_ids = track_metadata.get("external_ids")
        external_urls = (track_metadata.get("linked_from") or track_metadata)[
            "external_urls"
        ]
        track_id = self.downloader.get_media_id(track_metadata)
        release_date_datetime_obj = self.downloader.get_release_date_datetime_obj(
            album_metadata["release_date"],
            album_metadata["release_date_precision"],
        )
        producers = next(
            role
            for role in track_credits["roleCredits"]
            if role["roleTitle"] == "Producers"
        )["artists"]
        composers = next(
            role
            for role in track_credits["roleCredits"]
            if role["roleTitle"] == "Writers"
        )["artists"]
        disc = next(
            (
                track["disc_number"]
                for track in album_metadata["tracks"]["items"]
                if self.downloader.get_media_id(track) == track_id
            ),
        )
        tags = {
            "album": album_metadata["name"],
            "album_artist": self.downloader.get_artist_string(
                album_metadata["artists"]
            ),
            "artist": self.downloader.get_artist_string(track_metadata["artists"]),
            "compilation": (
                True if album_metadata["album_type"] == "compilation" else False
            ),
            "composer": (
                self.downloader.get_artist_string(composers) if composers else None
            ),
            "copyright": next(
                (i["text"] for i in album_metadata["copyrights"] if i["type"] == "P"),
                None,
            ),
            "disc": int(disc),
            "disc_total": int(album_metadata["tracks"]["items"][-1]["disc_number"]),
            "isrc": external_ids.get("isrc") if external_ids is not None else None,
            "label": album_metadata.get("label"),
            "lyrics": lyrics_unsynced,
            "media_type": "Song",
            "producer": (
                self.downloader.get_artist_string(producers) if producers else None
            ),
            "rating": "Explicit" if track_metadata.get("explicit") else "Unknown",
            "release_date": self.downloader.get_release_date_tag(
                release_date_datetime_obj
            ),
            "release_year": str(release_date_datetime_obj.year),
            "title": track_metadata["name"],
            "track": int(
                next(
                    (
                        track["track_number"]
                        for track in album_metadata["tracks"]["items"]
                        if self.downloader.get_media_id(track) == track_id
                    ),
                )
            ),
            "track_total": int(
                max(
                    track["track_number"]
                    for track in album_metadata["tracks"]["items"]
                    if track["disc_number"] == disc
                )
            ),
            "url": external_urls["spotify"],
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
        playlist_track: int = None,
        decryption_key: bytes = None,
    ):
        if not track_metadata:
            logger.debug("Getting track metadata")
            track_metadata = self.downloader.spotify_api.get_track(track_id)
        if not album_metadata:
            logger.debug("Getting album metadata")
            album_metadata = self.downloader.spotify_api.get_album(
                track_metadata["album"]["id"]
            )
        if not gid_metadata:
            logger.debug("Getting GID metadata")
            gid_metadata = self.downloader.get_gid_metadata(track_id, "track")
        if not stream_info:
            logger.debug("Getting stream info")
            stream_info = self.get_stream_info(gid_metadata, "track")
        if not stream_info.file_id:
            logger.warning(
                "Track is not available on Spotify's "
                "servers and no alternative found, skipping"
            )
            return
        if stream_info.quality != self.audio_quality:
            logger.warning(f"Quality has been changed to {stream_info.quality.value}")
        if gid_metadata.get("has_lyrics"):
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
        cover_url = self.get_cover_url(album_metadata)
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
        if self.no_lrc or not lyrics.synced:
            pass
        elif lrc_path.exists() and not self.downloader.overwrite:
            logger.debug(f'Synced lyrics already exists at "{lrc_path}", skipping')
        else:
            logger.debug(f'Saving synced lyrics to "{lrc_path}"')
            self.downloader.save_lrc(lrc_path, lyrics.synced)
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
