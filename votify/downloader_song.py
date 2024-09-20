import datetime
from pathlib import Path

from .downloader import Downloader
from .models import Lyrics, StreamInfo


class DownloaderSong:
    def __init__(
        self,
        downloader: Downloader,
    ):
        self.downloader = downloader

    def get_cover_url(self, album_metadata: dict) -> str | None:
        if not album_metadata.get("images"):
            return None
        return self.downloader.get_cover_url(album_metadata["images"])

    def get_tags(
        self,
        track_metadata: dict,
        album_metadata: dict,
        track_credits: dict,
        lyrics_unsynced: str,
    ) -> dict:
        external_ids = track_metadata.get("external_ids")
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
                i["disc_number"]
                for i in album_metadata["tracks"]["items"]
                if i["id"] == track_metadata["id"]
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
                        i["track_number"]
                        for i in album_metadata["tracks"]["items"]
                        if i["id"] == track_metadata["id"]
                    ),
                )
            ),
            "track_total": int(
                max(
                    i["track_number"]
                    for i in album_metadata["tracks"]["items"]
                    if i["disc_number"] == disc
                )
            ),
            "url": f"https://open.spotify.com/track/{track_metadata['id']}",
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
