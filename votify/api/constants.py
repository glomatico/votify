TIMEOUT = 30
HOME_PAGE_URL = "https://open.spotify.com/"
COOKIE_DOMAIN = ".spotify.com"
CLIENT_VERSION = "1.2.87.27.ga2033a72"
LYRICS_API_URL = "https://spclient.wg.spotify.com/color-lyrics/v2/track/{track_id}"
GID_METADATA_URL = (
    "https://spclient.wg.spotify.com/metadata/4/{media_type}/{gid}?market=from_token"
)
PATHFINDER_API_URL = "https://api-partner.spotify.com/pathfinder/v2/query"
VIDEO_MANIFEST_API_URL = "https://gue1-spclient.spotify.com/manifests/v9/json/sources/{file_id}/options/supports_drm"
PLAYBACK_INFO_API_URL = "https://gue1-spclient.spotify.com/track-playback/v1/media/spotify:{media_type}:{media_id}"
PLAYPLAY_LICENSE_API_URL = "https://gew4-spclient.spotify.com/playplay/v1/key/{file_id}"
EXTENDED_METADATA_API_URL = (
    "https://spclient.wg.spotify.com/extended-metadata/v0/extended-metadata"
)
WIDEVINE_LICENSE_API_URL = (
    "https://gue1-spclient.spotify.com/widevine-license/v1/{type}/license"
)
SEEK_TABLE_API_URL = "https://seektables.scdn.co/seektable/{file_id}.json"
TRACK_CREDITS_API_URL = "https://spclient.wg.spotify.com/track-credits-view/v0/experimental/{track_id}/credits"
AUDIO_STREAM_URLS_API_URL = (
    "https://gue1-spclient.spotify.com/storage-resolve/v2/files/audio/interactive/{format_id}/"
    "{file_id}?version=10000000&product=9&platform=39&alt=json"
)
SERVER_TIME_URL = "https://open.spotify.com/api/server-time"
SESSION_TOKEN_URL = "https://open.spotify.com/api/token"
CLIENT_TOKEN_URL = "https://clienttoken.spotify.com/v1/clienttoken"

TOTP_PERIOD = 30
TOTP_DIGITS = 6
TOTP_SECRETS_URL = (
    "https://git.gay/thereallo/totp-secrets/raw/branch/main/secrets/secretDict.json"
)

DEVICE_AUTH_URL = "https://accounts.spotify.com/oauth2/device/authorize"
DEVICE_TOKEN_URL = "https://accounts.spotify.com/api/token"
DEVICE_RESOLVE_URL = "https://accounts.spotify.com/pair/api/resolve"
DEVICE_CLIENT_ID = "65b708073fc0480ea92a077233ca87bd"  # Spotify for Desktop
DEVICE_SCOPE = "app-remote-control,playlist-modify,playlist-modify-private,playlist-modify-public,playlist-read,playlist-read-collaborative,playlist-read-private,streaming,transfer-auth-session,ugc-image-upload,user-follow-modify,user-follow-read,user-library-modify,user-library-read,user-modify,user-modify-playback-state,user-modify-private,user-personalized,user-read-birthdate,user-read-currently-playing,user-read-email,user-read-play-history,user-read-playback-position,user-read-playback-state,user-read-private,user-read-recently-played,user-top-read"
DEVICE_FLOW_USER_AGENT = "Spotify/128600502 Win32_x86_64/0 (PC desktop)"
DEVICE_CLIENT_TOKEN = "AADYATyeSD/y5/hrnY8iTzYaPodQdTzz/ffPg5WV8tD5KN53Yi/93r5TSMLRYo4aQCNgzl/1ckCkhFbOjPBWigpOdpvOZxfgJ3mov8/1IBpg05yWPKxwB7xV8SjNIlphPfj9LbrfbLZczrdYD0Wa++z+7sioGtI+m2GcgkOiRQgFqwEn8kP/PkIc/vHADZ1Zs3SZKif+5pXLlJ/0SDr8eZ+xECOXtfCw6jBAkl4r+wOMFrAMmE2JuLGFLg5PDD0="
