from __future__ import annotations

from pathlib import Path

from .downloader import Downloader


class DownloaderEpisode:
    def __init__(
        self,
        downloader: Downloader,
    ):
        self.downloader = downloader

    def get_tags(
        self,
        episode_metadata: dict,
        show_metadata: dict,
    ) -> dict:
        release_date_datetime_obj = self.downloader.get_release_date_datetime_obj(
            episode_metadata["release_date"],
            episode_metadata["release_date_precision"],
        )
        tags = {
            "album": show_metadata["name"],
            "description": episode_metadata["description"],
            "publisher": show_metadata.get("publisher"),
            "rating": "Explicit" if episode_metadata.get("explicit") else "Unknown",
            "release_date": self.downloader.get_release_date_tag(
                release_date_datetime_obj
            ),
            "release_year": str(release_date_datetime_obj.year),
            "title": episode_metadata["name"],
            "track": next(
                index
                for index in range(1, len(show_metadata["episodes"]["items"]) + 1)
                if show_metadata["episodes"]["items"][
                    len(show_metadata["episodes"]["items"]) - index
                ]["id"]
                == episode_metadata["id"]
            ),
            "url": f"https://open.spotify.com/episode/{episode_metadata['id']}",
        }
        return tags

    def get_cover_path(self, final_path: Path) -> Path:
        return final_path.with_suffix(".jpg")
