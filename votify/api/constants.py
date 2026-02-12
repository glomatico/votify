HOME_PAGE_URL = "https://open.spotify.com/"
COOKIE_DOMAIN = ".spotify.com"
CLIENT_VERSION = "1.2.70.61.g856ccd63"
LYRICS_API_URL = "https://spclient.wg.spotify.com/color-lyrics/v2/track/{track_id}"
GID_METADATA_URL = (
    "https://spclient.wg.spotify.com/metadata/4/{media_type}/{gid}?market=from_token"
)
PATHFINDER_API_URL = "https://api-partner.spotify.com/pathfinder/v2/query"
VIDEO_MANIFEST_API_URL = "https://gue1-spclient.spotify.com/manifests/v9/json/sources/{file_id}/options/supports_drm"
PLAYBACK_INFO_API_URL = "https://gue1-spclient.spotify.com/track-playback/v1/media/spotify:{media_type}:{media_id}"
PLAYPLAY_LICENSE_API_URL = "https://gew4-spclient.spotify.com/playplay/v1/key/{file_id}"
WIDEVINE_LICENSE_API_URL = (
    "https://gue1-spclient.spotify.com/widevine-license/v1/{type}/license"
)
SEEK_TABLE_API_URL = "https://seektables.scdn.co/seektable/{file_id}.json"
TRACK_CREDITS_API_URL = "https://spclient.wg.spotify.com/track-credits-view/v0/experimental/{track_id}/credits"
AUDIO_STREAM_URLS_API_URL = (
    "https://gue1-spclient.spotify.com/storage-resolve/v2/files/audio/interactive/11/"
    "{file_id}?version=10000000&product=9&platform=39&alt=json"
)
EXTEND_TRACK_COLLECTION_WAIT_TIME = 0.5
SERVER_TIME_URL = "https://open.spotify.com/api/server-time"
SESSION_TOKEN_URL = "https://open.spotify.com/api/token"
CLIENT_TOKEN_URL = "https://clienttoken.spotify.com/v1/clienttoken"

TOTP_PERIOD = 30
TOTP_DIGITS = 6
TOTP_SECRETS_URL = (
    "https://git.gay/thereallo/totp-secrets/raw/branch/main/secrets/secretDict.json"
)
