from typing import Any

from ..api.enums import SessionType
from ..utils import VotiyException


class VotifyInterfaceException(VotiyException):
    pass


class VotifyNoCdmException(VotifyInterfaceException):
    def __init__(self):
        super().__init__("Content requires a CDM but no .wvd file was provided")


class VotifyUrlParseException(VotifyInterfaceException):
    def __init__(self, url: str):
        super().__init__(f"Failed to parse Spotify URL: {url}")

        self.url = url


class VotifyUnsupportedMediaTypeException(VotifyInterfaceException):
    def __init__(self, media_type: str):
        super().__init__(f"Unsupported URL media type: {media_type}")

        self.media_type = media_type


class VotifyMediaException(VotifyInterfaceException):
    def __init__(self, message: str, media_id: str, media_metadata: dict | None = None):
        super().__init__(f"{message}: {media_id}")

        self.media_id = media_id
        self.media_metadata = media_metadata


class VotifyMediaFlatFilterException(VotifyMediaException):
    def __init__(
        self,
        media_id: str,
        media_metadata: dict | None = None,
        result: Any = None,
    ):
        super().__init__(
            "Media filtered out by flat filter",
            media_id=media_id,
            media_metadata=media_metadata,
        )

        self.result = result


class VotifyMediaNotFoundException(VotifyMediaException):
    def __init__(self, media_id: str, media_metadata: dict | None = None):
        super().__init__(
            "Media not found",
            media_id=media_id,
            media_metadata=media_metadata,
        )


class VotifyMediaUnstreamableException(VotifyMediaException):
    def __init__(self, media_id: str, media_metadata: dict | None = None):
        super().__init__(
            "Media is not streamable",
            media_id=media_id,
            media_metadata=media_metadata,
        )


class VotifyMediaFormatNotAvailableException(VotifyMediaException):
    def __init__(
        self,
        media_id: str,
        media_metadata: dict | None = None,
    ):
        super().__init__(
            "Selected format is not available",
            media_id=media_id,
            media_metadata=media_metadata,
        )


class VotifyMediaFormatNotAvailableForSessionTypeException(
    VotifyMediaFormatNotAvailableException
):
    def __init__(
        self,
        media_id: str,
        media_metadata: dict | None = None,
        session_type: SessionType | None = None,
    ):
        message = "Selected format is not available for session type"
        if session_type:
            message += f": {session_type.value}"

        super().__init__(
            media_id=media_id,
            media_metadata=media_metadata,
            message=message,
        )
