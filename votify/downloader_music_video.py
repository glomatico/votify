from __future__ import annotations

import logging

from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from .downloader_video import DownloaderVideo

logger = logging.getLogger("votify")


class DownloaderMusicVideo(DownloaderVideo):
    def __init__(
        self,
        downloader_video: DownloaderVideo,
    ):
        self.__dict__.update(downloader_video.__dict__)

    def get_video_gid(self, gid_metadata: dict) -> str | None:
        if not gid_metadata.get("original_video"):
            return None
        return gid_metadata["original_video"][0]["gid"]

    def get_tags(
        self,
        track_metadata: dict,
        album_metadata: dict,
        track_credits: dict,
    ) -> dict:
        external_ids = track_metadata.get("external_ids")
        external_urls = (track_metadata.get("linked_from") or track_metadata)[
            "external_urls"
        ]
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
        tags = {
            "artist": self.downloader.get_artist_string(track_metadata["artists"]),
            "composer": (
                self.downloader.get_artist_string(composers) if composers else None
            ),
            "copyright": next(
                (i["text"] for i in album_metadata["copyrights"] if i["type"] == "P"),
                None,
            ),
            "isrc": external_ids.get("isrc") if external_ids is not None else None,
            "label": album_metadata.get("label"),
            "media_type": "Music video",
            "producer": (
                self.downloader.get_artist_string(producers) if producers else None
            ),
            "rating": "Explicit" if track_metadata.get("explicit") else "Unknown",
            "title": track_metadata["name"],
            "release_date": self.downloader.get_release_date_tag(
                release_date_datetime_obj
            ),
            "release_year": str(release_date_datetime_obj.year),
            "url": external_urls["spotify"],
        }
        tags["release_year"] = str(release_date_datetime_obj.year)
        return tags

    def get_music_video_id_from_song_id(
        self,
        track_id: str,
        artist_id: str,
    ) -> dict | None:
        now_playing_view = self.downloader.spotify_api.get_now_playing_view(
            track_id, artist_id
        )
        related_music_videos = now_playing_view["data"]["trackUnion"]["relatedVideos"][
            "items"
        ]
        if not related_music_videos:
            return
        choices = [
            Choice(
                name="None",
                value=None,
            )
        ]
        choices.extend(
            [
                Choice(
                    name=" | ".join(
                        [
                            self.downloader.get_artist_string(
                                [
                                    {"name": artist["profile"]["name"]}
                                    for artist in related_music_video["trackOfVideo"][
                                        "data"
                                    ]["artists"]["items"]
                                ]
                            ),
                            related_music_video["trackOfVideo"]["data"]["name"],
                        ]
                    ),
                    value=related_music_video["trackOfVideo"]["data"]["uri"].split(":")[
                        -1
                    ],
                )
                for related_music_video in related_music_videos
            ]
        )
        selected_music_video_id = inquirer.select(
            message="Select which music video to download: (Artist | Title)",
            choices=choices,
        ).execute()
        return selected_music_video_id

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
        music_video_id: str,
        music_video_metadata: dict = None,
        album_metadata: dict = None,
        gid_metadata: dict = None,
        playlist_metadata: dict = None,
        playlist_track: int = None,
    ):
        if not music_video_metadata:
            logger.debug("Getting music video metadata")
            music_video_metadata = self.downloader.spotify_api.get_track(music_video_id)
        if not album_metadata:
            logger.debug("Getting album metadata")
            album_metadata = self.downloader.spotify_api.get_album(
                music_video_metadata["album"]["id"]
            )
        if not gid_metadata:
            logger.debug("Getting GID metadata")
            gid_metadata = self.downloader.get_gid_metadata(music_video_id, "track")
        video_gid = self.get_video_gid(gid_metadata)
        if not video_gid:
            logger.debug("Getting equivalent music video ID from song ID")
            music_video_id = self.get_music_video_id_from_song_id(
                music_video_id,
                album_metadata["artists"][0]["id"],
            )
            if not music_video_id:
                logger.warning(
                    "No related music videos found or no music video selected, skipping"
                )
                return
            music_video_metadata = self.downloader.spotify_api.get_track(music_video_id)
            logger.warning(
                f'Switching to downloading music video "{music_video_metadata["name"]}"'
            )
            album_metadata = self.downloader.spotify_api.get_album(
                music_video_metadata["album"]["id"]
            )
            gid_metadata = self.downloader.get_gid_metadata(music_video_id, "track")
            video_gid = self.get_video_gid(gid_metadata)
        stream_info = self.get_stream_info(video_gid)
        logger.debug("Getting credits")
        track_credits = self.downloader.spotify_api.get_track_credits(music_video_id)
        tags = self.get_tags(
            music_video_metadata,
            album_metadata,
            track_credits,
        )
        file_extension = self.get_file_extension(
            stream_info.file_type_video,
            stream_info.file_type_audio,
        )
        final_path = self.downloader.get_final_path(
            "music-video",
            tags,
            file_extension,
        )
        cover_path = self.get_cover_path(final_path)
        cover_url = self.get_cover_url(album_metadata)
        remuxed_path = None
        if final_path.exists() and not self.downloader.overwrite:
            logger.warning(f'Music video already exists at "{final_path}", skipping')
            return
        else:
            key_id, decryption_key = self.downloader.get_widevine_decryption_key(
                stream_info.encryption_data_widevine,
                "video",
            )
            encrypted_path_video = self.downloader.get_file_temp_path(
                music_video_id,
                "_video_encrypted",
                file_extension,
            )
            encrypted_path_audio = self.downloader.get_file_temp_path(
                music_video_id,
                "_audio_encrypted",
                file_extension,
            )
            decrypted_path_video = self.downloader.get_file_temp_path(
                music_video_id,
                "_video_decrypted",
                file_extension,
            )
            decrypted_path_audio = self.downloader.get_file_temp_path(
                music_video_id,
                "_audio_decrypted",
                file_extension,
            )
            remuxed_path = self.downloader.get_file_temp_path(
                music_video_id,
                "_remuxed",
                file_extension,
            )
            logger.debug(f'Downloading video to "{encrypted_path_video}"')
            self.download_segments(stream_info.segment_urls_video, encrypted_path_video)
            logger.debug(f'Downloading audio to "{encrypted_path_audio}"')
            self.download_segments(stream_info.segment_urls_audio, encrypted_path_audio)
            logger.debug(
                f'Decryping video/audio to "{decrypted_path_video}/{decrypted_path_audio}" and remuxing to "{remuxed_path}"'
            )
            self.remux(
                decrypted_path_video,
                decrypted_path_audio,
                remuxed_path,
                key_id,
                decryption_key,
                encrypted_path_video,
                encrypted_path_audio,
            )
        self.downloader._final_processing(
            cover_path,
            cover_url,
            remuxed_path,
            final_path,
            tags,
            playlist_metadata,
            playlist_track,
        )
