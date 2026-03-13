import logging

from .audio import SpotifyAudioInterface
from .constants import COVER_SIZE_ID_MAP_EPISODE, DEFAULT_EPISODE_DECRYPTION_KEY
from .enums import AudioQuality, MediaType
from .exceptions import VotifyMediaFormatNotAvailableException
from .types import DecryptionKey, MediaTags, SpotifyMedia, StreamInfo, StreamInfoAv

logger = logging.getLogger(__name__)


class SpotifyEpisodeInterface(SpotifyAudioInterface):
    def __init__(
        self,
        audio: SpotifyAudioInterface,
    ):
        self.__dict__.update(audio.__dict__)

    async def proccess_media(
        self,
        episode_id: dict | None = None,
        episode_data: dict | None = None,
        show_data: dict | None = None,
        show_items: list[dict] | None = None,
    ) -> SpotifyMedia:
        if not episode_data:
            episode_response = await self.api.get_episode(
                episode_id=episode_id,
            )
            episode_data = episode_response["data"]["episodeUnionV2"]

        if not episode_id:
            episode_id = episode_data["uri"].split(":")[-1]

        if not show_data:
            show_data, show_items = await self.get_show_data_cached(
                episode_data["podcastV2"]["data"]["uri"].split(":")[-1]
            )

        media = SpotifyMedia(episode_data["uri"].split(":")[-1])

        media.media_metadata = episode_data
        media.show_metadata = show_data

        media.tags = await self.parse_tags(
            episode_data,
            show_items,
        )

        media.cover_url = self.parse_cover_url(
            episode_data["coverArt"]["sources"][0]["url"]
        )

        if not self.skip_stream_info:
            media.stream_info = await self.get_stream_info(
                episode_data=episode_data,
            )

            media.decryption_key = DecryptionKey(
                decryption_key=DEFAULT_EPISODE_DECRYPTION_KEY,
            )

        logger.debug(f"Parsed episode media: {media}")

        return media

    @staticmethod
    async def parse_tags(
        episode_data: dict,
        show_items: list[dict],
        is_video: bool = False,
    ) -> MediaTags:
        release_date = episode_data["releaseDate"]

        tags = MediaTags(
            album=episode_data["podcastV2"]["data"]["name"],
            date=(
                SpotifyAudioInterface.parse_date(release_date["isoString"])
                if release_date
                else None
            ),
            description=episode_data.get("description"),
            media_id=episode_data["uri"].split(":")[-1],
            media_type=MediaType.PODCAST_VIDEO if is_video else MediaType.PODCAST,
            rating=SpotifyAudioInterface.parse_rating(
                episode_data["contentRating"]["label"]
            ),
            title=episode_data["name"],
            track=next(
                (
                    index + 1
                    for index, item in enumerate(reversed(show_items))
                    if item["entity"]["_uri"] == episode_data["uri"]
                ),
                None,
            ),
            track_total=len(show_items),
            url=f"https://open.spotify.com/episode/{episode_data['uri'].split(':')[-1]}",
        )

        logger.debug(f"Parsed episode tags: {tags}")

        return tags

    def parse_cover_url(self, base_cover_url: str) -> str:
        cover_url = self._transform_cover_url(base_cover_url, COVER_SIZE_ID_MAP_EPISODE)

        logger.debug(f"Parsed episode cover URL: {cover_url}")

        return cover_url

    async def get_stream_info(
        self,
        episode_data: dict,
    ) -> StreamInfoAv:
        for audio_quality in self.audio_quality_priority:
            stream_info = await self._get_stream_info(
                episode_data=episode_data,
                audio_quality=audio_quality,
            )
            if stream_info:
                return stream_info

        raise VotifyMediaFormatNotAvailableException(
            media_id=episode_data["uri"].split(":")[-1],
            media_metadata=episode_data,
        )

    async def _get_stream_info(
        self,
        episode_data: dict,
        audio_quality: AudioQuality,
    ) -> StreamInfoAv | None:
        audio_items = episode_data["audio"]["items"]
        audio_item = next(
            (
                item
                for item in audio_items
                if item["format"].startswith(audio_quality.format_name)
            ),
            None,
        )
        if not audio_item:
            return None

        audio_id = audio_item["url"].split("/")[-1]
        stream_url = await self._get_stream_url(audio_quality.format_id, audio_id)

        stream_info = StreamInfoAv(
            audio_track=StreamInfo(
                stream_url=stream_url,
                file_format=audio_quality.file_format,
                actual_file_format=audio_quality.actual_file_format,
                widevine_pssh=None,
            )
        )

        logger.debug(f"Parsed episode stream info: {stream_info}")

        return stream_info
