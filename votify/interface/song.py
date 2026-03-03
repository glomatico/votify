import asyncio
import datetime
import logging

from ..api import VotifyRequestException
from .audio import SpotifyAudioInterface
from .constants import COVER_SIZE_ID_MAP_SONG
from .enums import MediaType
from .exceptions import (
    VotifyMediaFormatNotAvailableException,
)
from .types import MediaLyrics, MediaTags, SpotifyMedia

logger = logging.getLogger(__name__)


class SpotifySongInterface(SpotifyAudioInterface):
    def __init__(
        self,
        audio: SpotifyAudioInterface,
    ):
        self.__dict__.update(audio.__dict__)

    async def proccess_media(
        self,
        track_id: str | None = None,
        track_data: dict | None = None,
        album_data: dict | None = None,
        album_items: list[dict] | None = None,
    ) -> SpotifyMedia:
        if not track_data:
            track_response = await self.api.get_track(track_id)
            track_data = track_response["data"]["trackUnion"]

        if not track_id:
            track_id = track_data["uri"].split(":")[-1]

        if not album_data:
            if (
                track_data["albumOfTrack"].get("tracks")
                and len(track_data["albumOfTrack"]["tracks"]["items"])
                == track_data["albumOfTrack"]["tracks"]["totalCount"]
            ):
                album_data, album_items = (
                    track_data["albumOfTrack"],
                    track_data["albumOfTrack"]["tracks"]["items"],
                )
            else:
                album_data, album_items = await self.get_album_data_cached(
                    track_data["albumOfTrack"]["uri"].split(":")[-1]
                )

        media = SpotifyMedia(track_data["uri"].split(":")[-1])

        media.media_metadata = track_data
        media.album_metadata = album_data
        media.lyrics = await self.get_lyrics(media.media_id)
        media.tags = await self.parse_tags(
            track_data,
            album_data,
            album_items,
            media.lyrics.unsynced if media.lyrics else None,
        )
        media.cover_url = self.parse_cover_url(
            media.album_metadata["coverArt"]["sources"][0]["url"]
        )

        if not self.skip_stream_info:
            try:
                media.stream_info = await self.get_stream_info(
                    media_id=track_id,
                    media_type="track",
                    skip_pssh=False,
                )
            except VotifyMediaFormatNotAvailableException as e:
                e.media_metadata = track_data
                raise

            media.decryption_key = await self.get_widevine_decryption_key(
                media.stream_info.audio_track.widevine_pssh
            )

        logger.debug(f"Processed song media: {media}")

        return media

    async def get_lyrics(self, track_id: str) -> MediaLyrics | None:
        try:
            lyrics_response = await self.api.get_lyrics(track_id)
        except VotifyRequestException as e:
            if e.response_status_code != 404:
                raise e
            return

        lyrics = self._parse_lyirics(lyrics_response)

        logger.debug(f"Parsed lyrics: {lyrics}")

        return lyrics

    async def parse_tags(
        self,
        track_data: dict,
        album_data: dict,
        album_items: list[dict],
        lyrics: str | None = None,
    ) -> MediaTags:
        iso_date = album_data["date"]["isoString"]

        (composer, producer), (album_artist, artist, isrc, label) = (
            await asyncio.gather(
                self._get_composer_producer(track_data["uri"].split(":")[-1]),
                self._get_isrc_label(track_data["uri"].split(":")[-1]),
            )
        )

        copyright = self._parse_copyright(album_data["copyright"]["items"])
        rating = self.parse_rating(track_data["contentRating"]["label"])
        disc, disc_total, track_total = self._parse_disc_info(
            album_items,
            track_data["uri"],
        )
        compilation = album_data["type"] == "COMPILATION"

        tags = MediaTags(
            title=track_data["name"],
            artist=artist,
            album=album_data["name"],
            album_artist=album_artist,
            compilation=compilation,
            composer=composer,
            copyright=copyright,
            date=self.parse_date(iso_date),
            disc=disc,
            disc_total=disc_total,
            isrc=isrc,
            label=label,
            lyrics=lyrics,
            media_id=track_data["uri"].split(":")[-1],
            media_type=MediaType.SONG,
            producer=producer,
            rating=rating,
            track=track_data["trackNumber"],
            track_total=track_total,
            url=f"https://open.spotify.com/track/{track_data['uri'].split(':')[-1]}",
        )

        logger.debug(f"Parsed song tags: {tags}")

        return tags

    def parse_cover_url(self, base_cover_url: str) -> str:
        cover_url = self._transform_cover_url(base_cover_url, COVER_SIZE_ID_MAP_SONG)

        logger.debug(f"Parsed song cover URL: {cover_url}")

        return cover_url

    @staticmethod
    def _parse_copyright(copyright_items: list[dict]) -> str | None:
        return next(
            (item["text"] for item in copyright_items if item["type"] == "P"),
            next(
                (item["text"] for item in copyright_items if item["type"] == "C"),
                None,
            ),
        )

    def _parse_disc_info(
        self,
        tracks: list[dict],
        track_uri: str,
    ) -> tuple[int, int, int]:
        track_numbers = []
        current_track_index = None

        for i, item in enumerate(tracks):
            track_num = item["track"]["trackNumber"]
            track_numbers.append(track_num)
            if item["track"]["uri"] == track_uri:
                current_track_index = i

        track_total = max(track_numbers)
        disc_total = len(track_numbers) // track_total

        disc = 1
        for i in range(1, current_track_index + 1):
            if track_numbers[i] < track_numbers[i - 1]:
                disc += 1

        return disc, disc_total, track_total

    async def _get_composer_producer(
        self,
        track_id: str,
    ) -> tuple[str | None, str | None]:
        track_credits_response = await self.api.get_track_credits(track_id)

        composers = []
        producers = []

        for role in track_credits_response.get("roleCredits", []):
            if role["roleTitle"] == "Writers":
                composers.extend([artist["name"] for artist in role["artists"]])
            elif role["roleTitle"] == "Producers":
                producers.extend([artist["name"] for artist in role["artists"]])

        return self.format_names(composers), self.format_names(producers)

    async def _get_isrc_label(
        self,
        track_id: str,
    ) -> tuple[str | None, str | None, str | None, str | None]:
        track_gid = await self.api.get_gid_metadata(track_id, "track")

        isrc = next(
            (
                external_id["id"]
                for external_id in track_gid.get("external_id", [])
                if external_id["type"] == "isrc"
            ),
            None,
        )
        label = track_gid.get("album", {}).get("label")
        album_artists = [
            artist["name"] for artist in track_gid.get("album", {}).get("artist", [])
        ]
        track_artists = [artist["name"] for artist in track_gid.get("artist", [])]

        return (
            self.format_names(album_artists),
            self.format_names(track_artists),
            isrc,
            label,
        )

    def _get_lyrics_synced_timestamp_lrc(self, time: int) -> str:
        lrc_timestamp = datetime.datetime.fromtimestamp(
            time / 1000.0, tz=datetime.timezone.utc
        )
        return lrc_timestamp.strftime("%M:%S.%f")[:-4]

    def _parse_lyirics(self, lyrics_response: dict) -> MediaLyrics:
        synced_lines = []
        unsynced_lines = []

        for line in lyrics_response["lyrics"]["lines"]:
            if lyrics_response["lyrics"]["syncType"] == "LINE_SYNCED":
                synced_lines.append(
                    f'[{self._get_lyrics_synced_timestamp_lrc(int(line["startTimeMs"]))}]'
                    + line["words"]
                )
            unsynced_lines.append(line["words"])

        return MediaLyrics(
            synced="\n".join(synced_lines) if synced_lines else None,
            unsynced="\n".join(unsynced_lines) + "\n" if unsynced_lines else None,
        )
