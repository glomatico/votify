import logging

from .audio import SpotifyAudioInterface
from .constants import COVER_SIZE_ID_MAP_EPISODE, DEFAULT_EPISODE_DECRYPTION_KEY
from .enums import MediaType
from .exceptions import VotifyMediaFormatNotAvailableException
from .types import DecryptionKey, MediaTags, SpotifyMedia

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
            try:
                media.stream_info = await self.get_stream_info(
                    media_id=episode_id,
                    media_type="episode",
                    skip_pssh=True,
                )
            except VotifyMediaFormatNotAvailableException as e:
                e.media_metadata = episode_data
                raise

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
