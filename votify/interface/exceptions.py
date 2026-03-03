from ..utils import VotiyException


class VotifyInterfaceException(VotiyException):
    pass


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


class VotifyDrmDisabledException(VotifyMediaException):
    def __init__(self, media_id: str, media_metadata: dict | None = None):
        super().__init__(
            "DRM is disabled, cannot process media",
            media_id=media_id,
            media_metadata=media_metadata,
        )


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
            "Selected audio quality is not available",
            media_id=media_id,
            media_metadata=media_metadata,
        )
