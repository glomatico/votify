import asyncio
import logging

from .enums import MediaType
from .song import SpotifySongInterface
from .types import MediaTags, SpotifyMedia
from .video import SpotifyVideoInterface

logger = logging.getLogger(__name__)


class SpotifyMusicVideoInterface(SpotifyVideoInterface):
    def __init__(
        self,
        video: SpotifyVideoInterface,
    ):
        self.__dict__.update(video.__dict__)

    async def parse_tags(
        self,
        track_data: dict,
        album_data: dict,
    ) -> MediaTags:
        iso_date = album_data["date"]["isoString"]

        (composer, producer), (_, artist, isrc, label) = await asyncio.gather(
            SpotifySongInterface._get_composer_producer(
                self, track_data["uri"].split(":")[-1]
            ),
            SpotifySongInterface._get_isrc_label(
                self, track_data["uri"].split(":")[-1]
            ),
        )

        copyright = SpotifySongInterface._parse_copyright(
            album_data["copyright"]["items"]
        )
        rating = self.parse_rating(track_data["contentRating"]["label"])

        tags = MediaTags(
            title=track_data["name"],
            artist=artist,
            composer=composer,
            copyright=copyright,
            date=self.parse_date(iso_date),
            isrc=isrc,
            label=label,
            media_id=track_data["uri"].split(":")[-1],
            media_type=MediaType.MUSIC_VIDEO,
            producer=producer,
            rating=rating,
            url=f"https://open.spotify.com/track/{track_data['uri'].split(':')[-1]}",
        )

        logger.debug(f"Parsed music video tags: {tags}")

        return tags

    async def proccess_media(
        self,
        playback_info: dict,
        track_data: dict | None = None,
        album_data: dict | None = None,
    ) -> SpotifyMedia:
        if not track_data:
            track_response = await self.api.get_track(
                playback_info["metadata"]["uri"].split(":")[-1]
            )
            track_data = track_response["data"]["trackUnion"]

        if not album_data:
            if track_data["albumOfTrack"].get("tracks"):
                album_data, _ = (
                    track_data["albumOfTrack"],
                    track_data["albumOfTrack"]["tracks"]["items"],
                )
            else:
                album_data, _ = await self.get_album_data_cached(
                    track_data["albumOfTrack"]["uri"].split(":")[-1]
                )

        media = SpotifyMedia(track_data["uri"].split(":")[-1])

        media.media_metadata = track_data

        media.tags = await self.parse_tags(track_data, album_data)

        media.cover_url = self.parse_cover_url(
            album_data["coverArt"]["sources"][0]["url"]
        )

        if not self.skip_stream_info:
            media.stream_info = await self.get_stream_info(playback_info)

            media.decryption_key = await self.get_widevine_decryption_key(
                media.stream_info.audio_track.widevine_pssh
            )

        logger.debug(f"Parsed music video media: {media}")

        return media
