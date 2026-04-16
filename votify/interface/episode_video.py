import logging

from .episode import SpotifyEpisodeInterface
from .types import SpotifyMedia
from .video import SpotifyVideoInterface

logger = logging.getLogger(__name__)


class SpotifyEpisodeVideoInterface(SpotifyVideoInterface):
    def __init__(
        self,
        video: SpotifyVideoInterface,
    ):
        self.__dict__.update(video.__dict__)

    async def proccess_media(
        self,
        episode_id: dict | None = None,
        episode_data: dict | None = None,
        show_data: dict | None = None,
        show_items: list[dict] | None = None,
    ) -> SpotifyMedia:
        if not episode_data:
            episode_response = await self.api.get_episode(episode_id)
            episode_data = episode_response["data"]["episodeUnionV2"]

        if not episode_id:
            episode_id = episode_data["uri"].split(":")[-1]

        if not show_data:
            show_data, show_items = await self.get_show_data_cached(
                episode_data["podcastV2"]["data"]["uri"].split(":")[-1]
            )

        media = SpotifyMedia(episode_data["uri"].split(":")[-1], episode_data)

        media.show_metadata = show_data

        media.tags = await SpotifyEpisodeInterface.parse_tags(
            episode_data,
            show_items,
            True,
        )

        media.cover_url = (
            self.parse_cover_url(episode_data["coverArt"]["sources"][0]["url"])
            if episode_data["coverArt"]["sources"]
            else None
        )

        if not self.skip_stream_info:
            media.stream_info = await self.get_stream_info(episode_id, "episode")

            if media.stream_info.audio_track.widevine_pssh:
                media.decryption_key = await self.get_widevine_decryption_key(
                    media.stream_info.audio_track.widevine_pssh
                )

        logger.debug(f"Parsed episode video media: {media}")

        return media
