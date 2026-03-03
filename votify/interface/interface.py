import logging
from typing import AsyncGenerator

from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from .audio import SpotifyAudioInterface
from .enums import ArtistMediaOption, AudioQuality
from .episode import SpotifyEpisodeInterface
from .episode_video import SpotifyEpisodeVideoInterface
from .exceptions import (
    VotifyDrmDisabledException,
    VotifyMediaNotFoundException,
    VotifyMediaUnstreamableException,
    VotifyUnsupportedMediaTypeException,
)
from .music_video import SpotifyMusicVideoInterface
from .song import SpotifySongInterface
from .types import SpotifyMedia

logger = logging.getLogger(__name__)


class SpotifyInterface:
    def __init__(
        self,
        base: SpotifyAudioInterface,
        song: SpotifySongInterface,
        episode: SpotifyEpisodeInterface,
        music_video: SpotifyMusicVideoInterface,
        episode_video: SpotifyEpisodeVideoInterface,
        prefer_video: bool = False,
        artist_media_option: ArtistMediaOption | None = None,
    ) -> None:
        self.base = base
        self.song = song
        self.episode = episode
        self.music_video = music_video
        self.episode_video = episode_video
        self.prefer_video = prefer_video
        self.artist_media_option = artist_media_option

    async def _get_track_media(
        self,
        track_id: str,
        track_data: dict | None = None,
        album_data: dict | None = None,
        album_items: list[dict] | None = None,
    ) -> SpotifyMedia | BaseException | None:
        if self.base.no_drm:
            return VotifyDrmDisabledException(track_id)

        if not track_data:
            track_response = await self.base.api.get_track(track_id)
            track_data = track_response["data"]["trackUnion"]

        if "__typename" in track_data and track_data["__typename"] != "Track":
            return VotifyMediaNotFoundException(track_id, track_data)

        if not track_data["playability"]["playable"]:
            return VotifyMediaUnstreamableException(track_id, track_data)

        try:
            if (
                track_data["mediaType"] == "VIDEO"
                or self.prefer_video
                and track_data["associationsV3"]["videoAssociations"]["totalCount"]
            ):
                return await self.music_video.proccess_media(
                    **(
                        {
                            "track_data": track_data,
                            "album_data": album_data,
                        }
                        if track_data["mediaType"] == "VIDEO"
                        else {
                            "track_id": track_id,
                        }
                    ),
                )

            return await self.song.proccess_media(
                track_data=track_data,
                album_data=album_data,
                album_items=album_items,
            )
        except BaseException as e:
            return e

    async def _get_episode_media(
        self,
        episode_id: str,
        episode_data: dict | None = None,
        show_data: dict | None = None,
        show_items: list[dict] | None = None,
    ) -> SpotifyMedia | BaseException | None:
        if not episode_data:
            episode_response = await self.base.api.get_episode(episode_id)
            episode_data = episode_response["data"]["episodeUnionV2"]

        if episode_data["__typename"] != "Episode":
            return VotifyMediaNotFoundException(episode_id, episode_data)

        if not episode_data["playability"]["playable"]:
            return VotifyMediaUnstreamableException(episode_id, episode_data)

        try:
            if "VIDEO" in episode_data["mediaTypes"] and self.prefer_video:
                return await self.episode_video.proccess_media(
                    episode_data=episode_data,
                    show_data=show_data,
                    show_items=show_items,
                )

            return await self.episode.proccess_media(
                episode_data=episode_data,
                show_data=show_data,
                show_items=show_items,
            )
        except BaseException as e:
            return e

    async def _get_album_media(
        self,
        media_id: str,
    ) -> AsyncGenerator[SpotifyMedia | BaseException, None]:
        if self.base.no_drm:
            yield VotifyDrmDisabledException(media_id)
            return

        album_data, album_items = await self.base.get_album_data_cached(
            album_id=media_id
        )

        if album_data["__typename"] != "Album":
            yield VotifyMediaNotFoundException(media_id, album_data)
        else:
            for item in album_items:
                track_data = item["track"]
                track_id = track_data["uri"].split(":")[-1]

                yield await self._get_track_media(
                    track_id=track_id,
                    track_data=track_data,
                    album_data=album_data,
                    album_items=album_items,
                )

    async def _get_show_media(
        self,
        media_id: str,
    ) -> AsyncGenerator[SpotifyMedia | BaseException, None]:
        show_data, show_items = await self.base.get_show_data_cached(show_id=media_id)

        if show_data["__typename"] != "Podcast":
            yield VotifyMediaNotFoundException(media_id, show_data)
        else:
            for item in show_items:
                episode_data = item["entity"]["data"]
                episode_id = item["entity"]["_uri"].split(":")[-1]

                yield await self._get_episode_media(
                    episode_id=episode_id,
                    episode_data=episode_data,
                    show_data=show_data,
                    show_items=show_items,
                )

    async def _get_playlist_media(
        self,
        media_id: str,
    ) -> AsyncGenerator[SpotifyMedia | BaseException, None]:
        playlist_response = await self.base.api.get_playlist(media_id)
        playlist_data = playlist_response["data"]["playlistV2"]

        if playlist_data["__typename"] != "Playlist":
            yield VotifyMediaNotFoundException(media_id, playlist_data)
        else:
            playlist_items = playlist_data["content"]["items"]
            while len(playlist_items) < playlist_data["content"]["totalCount"]:
                playlist_response = await self.base.api.get_playlist(
                    media_id,
                    len(playlist_items),
                )
                playlist_items.extend(
                    playlist_response["data"]["playlistV2"]["content"]["items"]
                )

            for index, item in enumerate(playlist_items, start=1):
                track_data = item["itemV2"]["data"]
                track_id = track_data["uri"].split(":")[-1]

                if track_data["__typename"] == "Track":
                    media = await self._get_track_media(
                        track_id=track_id,
                        track_data=track_data,
                    )
                elif track_data["__typename"] == "Episode":
                    media = await self._get_episode_media(
                        episode_id=track_id,
                        episode_data=track_data,
                    )
                else:
                    yield VotifyMediaNotFoundException(track_id, track_data)
                    return

                media.playlist_metadata = playlist_data
                media.playlist_tags = self.base.get_playlist_tags(playlist_data, index)

                yield media

    async def _get_artist_media(
        self,
        media_id: str,
    ) -> AsyncGenerator[SpotifyMedia | BaseException, None]:
        if self.artist_media_option:
            artist_media_option = self.artist_media_option
        else:
            choices = [
                Choice(name=option.value.capitalize(), value=option)
                for option in ArtistMediaOption
            ]
            artist_media_option = await inquirer.select(
                message="Select which media to download:",
                choices=choices,
            ).execute_async()

        if artist_media_option in {
            ArtistMediaOption.ALBUMS,
            ArtistMediaOption.SINGLES,
            ArtistMediaOption.COMPILATIONS,
        }:
            key = (
                "albums"
                if artist_media_option == ArtistMediaOption.ALBUMS
                else (
                    "singles"
                    if artist_media_option == ArtistMediaOption.SINGLES
                    else "compilations"
                )
            )
            async for media in self._get_artist_media_albums(media_id, key):
                yield media
        else:
            async for media in self._get_artist_media_videos(media_id):
                yield media

    async def _get_artist_media_videos(
        self,
        media_id: str,
    ) -> AsyncGenerator[SpotifyMedia | BaseException, None]:
        videos_response = await self.base.api.get_artist_videos(media_id)
        videos_data = videos_response["data"]["artistUnion"]

        if videos_data["__typename"] != "Artist":
            yield VotifyMediaNotFoundException(media_id, videos_data)
            return

        related_items = videos_data["relatedMusicVideos"]["items"]
        unmapped_items = videos_data["unmappedMusicVideos"]["items"]
        related_total = videos_data["relatedMusicVideos"]["totalCount"]
        unmapped_total = videos_data["unmappedMusicVideos"]["totalCount"]

        while (
            len(related_items) < related_total or len(unmapped_items) < unmapped_total
        ):
            offset = max(len(related_items), len(unmapped_items))
            videos_response = await self.base.api.get_artist_videos(media_id, offset)
            videos_data = videos_response["data"]["artistUnion"]
            if len(related_items) < related_total:
                related_items.extend(videos_data["relatedMusicVideos"]["items"])
            if len(unmapped_items) < unmapped_total:
                unmapped_items.extend(videos_data["unmappedMusicVideos"]["items"])

        video_items = related_items + unmapped_items

        if not video_items:
            yield VotifyMediaNotFoundException(media_id, videos_data)
            return

        if self.artist_media_option:
            selection = video_items
        else:
            choices = [
                Choice(
                    name=" | ".join(
                        [
                            video_item["data"]["name"],
                        ]
                    ),
                    value=video_item,
                )
                for video_item in video_items
            ]
            selection = await inquirer.select(
                message="Select which videos to download (Title):",
                choices=choices,
                multiselect=True,
            ).execute_async()

        for video_item in selection:
            track_id = video_item["uri"].split(":")[-1]
            media = await self._get_track_media(
                track_id=track_id,
                track_data=video_item,
            )
            yield media

    async def _get_artist_media_albums(
        self,
        media_id: str,
        key: str,
    ) -> AsyncGenerator[SpotifyMedia | BaseException, None]:
        if key == "compilations":
            albums_response = await self.base.api.get_artist_compilations(media_id)
        elif key == "singles":
            albums_response = await self.base.api.get_artist_singles(media_id)
        else:
            albums_response = await self.base.api.get_artist_albums(media_id)
        albums_data = albums_response["data"]["artistUnion"]

        if albums_data["__typename"] != "Artist":
            yield VotifyMediaNotFoundException(media_id, albums_data)
            return

        album_items = albums_data["discography"][key]["items"]
        while len(album_items) < albums_data["discography"][key]["totalCount"]:
            albums_response = await self.base.api.get_artist_albums(
                media_id,
                len(album_items),
            )
            album_items.extend(
                albums_response["data"]["artistUnion"]["discography"][key]["items"]
            )

        album_items_filtered = [
            release_item
            for album_item in album_items
            for release_item in album_item["releases"]["items"]
        ]

        if not album_items_filtered:
            yield VotifyMediaNotFoundException(media_id, albums_data)
            return

        if self.artist_media_option:
            selection = album_items_filtered
        else:
            choices = [
                Choice(
                    name=" | ".join(
                        [
                            str(album_item["date"]["year"]),
                            f"{album_item['tracks']['totalCount']:03d}",
                            album_item["name"],
                        ]
                    ),
                    value=album_item,
                )
                for album_item in album_items_filtered
            ]
            selection = await inquirer.select(
                message="Select which albums to download (Year | Track Count | Title):",
                choices=choices,
                multiselect=True,
            ).execute_async()

        for album_item in selection:
            album_id = album_item["uri"].split(":")[-1]
            async for media in self._get_album_media(album_id):
                yield media

    async def get_media_by_url(
        self,
        url: str,
    ) -> AsyncGenerator[SpotifyMedia | BaseException, None]:
        url_info = self.base.parse_url_info(url)

        if url_info.media_type in self.base.disallowed_media_types:
            yield VotifyUnsupportedMediaTypeException(url_info.media_type)
        elif url_info.media_type == "track":
            yield await self._get_track_media(url_info.media_id)
        elif url_info.media_type == "episode":
            yield await self._get_episode_media(url_info.media_id)
        elif url_info.media_type == "album":
            async for media in self._get_album_media(url_info.media_id):
                yield media
        elif url_info.media_type == "show":
            async for media in self._get_show_media(url_info.media_id):
                yield media
        elif url_info.media_type == "playlist":
            async for media in self._get_playlist_media(url_info.media_id):
                yield media
        elif url_info.media_type == "artist":
            async for media in self._get_artist_media(url_info.media_id):
                yield media
