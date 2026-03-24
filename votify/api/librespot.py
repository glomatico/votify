from librespot.proto import Authentication_pb2 as Authentication
from librespot.core import Session


class Librespot:
    def __init__(
        self,
        access_token: str,
    ) -> None:
        self.access_token = access_token

        self._initialize()

    def _initialize(self) -> None:
        login_credentials = Authentication.LoginCredentials(
            username=None,
            typ=Authentication.AuthenticationType.AUTHENTICATION_SPOTIFY_TOKEN,
            auth_data=self.access_token.encode(),
        )

        builder = Session.Builder()
        builder.login_credentials = login_credentials

        builder.conf = (
            Session.Configuration.Builder()
            .set_store_credentials(False)
            .set_cache_enabled(False)
            .build()
        )

        self.session = builder.create()
