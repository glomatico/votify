from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExtensionKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_EXTENSION: _ClassVar[ExtensionKind]
    CANVAZ: _ClassVar[ExtensionKind]
    STORYLINES: _ClassVar[ExtensionKind]
    PODCAST_TOPICS: _ClassVar[ExtensionKind]
    PODCAST_SEGMENTS: _ClassVar[ExtensionKind]
    AUDIO_FILES: _ClassVar[ExtensionKind]
    TRACK_DESCRIPTOR: _ClassVar[ExtensionKind]
    PODCAST_COUNTER: _ClassVar[ExtensionKind]
    ARTIST_V4: _ClassVar[ExtensionKind]
    ALBUM_V4: _ClassVar[ExtensionKind]
    TRACK_V4: _ClassVar[ExtensionKind]
    SHOW_V4: _ClassVar[ExtensionKind]
    EPISODE_V4: _ClassVar[ExtensionKind]
    PODCAST_HTML_DESCRIPTION: _ClassVar[ExtensionKind]
    PODCAST_QUOTES: _ClassVar[ExtensionKind]
    USER_PROFILE: _ClassVar[ExtensionKind]
    CANVAS_V1: _ClassVar[ExtensionKind]
    SHOW_V4_BASE: _ClassVar[ExtensionKind]
    SHOW_V4_EPISODES_ASSOC: _ClassVar[ExtensionKind]
    TRACK_DESCRIPTOR_SIGNATURES: _ClassVar[ExtensionKind]
    PODCAST_AD_SEGMENTS: _ClassVar[ExtensionKind]
    EPISODE_TRANSCRIPTS: _ClassVar[ExtensionKind]
    PODCAST_SUBSCRIPTIONS: _ClassVar[ExtensionKind]
    EXTRACTED_COLOR: _ClassVar[ExtensionKind]
    PODCAST_VIRALITY: _ClassVar[ExtensionKind]
    IMAGE_SPARKLES_HACK: _ClassVar[ExtensionKind]
    PODCAST_POPULARITY_HACK: _ClassVar[ExtensionKind]
    AUTOMIX_MODE: _ClassVar[ExtensionKind]
    CUEPOINTS: _ClassVar[ExtensionKind]
    PODCAST_POLL: _ClassVar[ExtensionKind]
    EPISODE_ACCESS: _ClassVar[ExtensionKind]
    SHOW_ACCESS: _ClassVar[ExtensionKind]
    PODCAST_QNA: _ClassVar[ExtensionKind]
    CLIPS: _ClassVar[ExtensionKind]
    SHOW_V5: _ClassVar[ExtensionKind]
    EPISODE_V5: _ClassVar[ExtensionKind]
    PODCAST_CTA_CARDS: _ClassVar[ExtensionKind]
    PODCAST_RATING: _ClassVar[ExtensionKind]
    DISPLAY_SEGMENTS: _ClassVar[ExtensionKind]
    GREENROOM: _ClassVar[ExtensionKind]
    USER_CREATED: _ClassVar[ExtensionKind]
    SHOW_DESCRIPTION: _ClassVar[ExtensionKind]
    SHOW_HTML_DESCRIPTION: _ClassVar[ExtensionKind]
    SHOW_PLAYABILITY: _ClassVar[ExtensionKind]
    EPISODE_DESCRIPTION: _ClassVar[ExtensionKind]
    EPISODE_HTML_DESCRIPTION: _ClassVar[ExtensionKind]
    EPISODE_PLAYABILITY: _ClassVar[ExtensionKind]
    SHOW_EPISODES_ASSOC: _ClassVar[ExtensionKind]
    CLIENT_CONFIG: _ClassVar[ExtensionKind]
    PLAYLISTABILITY: _ClassVar[ExtensionKind]
    AUDIOBOOK_V5: _ClassVar[ExtensionKind]
    CHAPTER_V5: _ClassVar[ExtensionKind]
    AUDIOBOOK_SPECIFICS: _ClassVar[ExtensionKind]
    EPISODE_RANKING: _ClassVar[ExtensionKind]
    HTML_DESCRIPTION: _ClassVar[ExtensionKind]
    CREATOR_CHANNEL: _ClassVar[ExtensionKind]
    AUDIOBOOK_PROVIDERS: _ClassVar[ExtensionKind]
    PLAY_TRAIT: _ClassVar[ExtensionKind]
    CONTENT_WARNING: _ClassVar[ExtensionKind]
    IMAGE_CUE: _ClassVar[ExtensionKind]
    STREAM_COUNT: _ClassVar[ExtensionKind]
    AUDIO_ATTRIBUTES: _ClassVar[ExtensionKind]
    NAVIGABLE_TRAIT: _ClassVar[ExtensionKind]
    NEXT_BEST_EPISODE: _ClassVar[ExtensionKind]
    AUDIOBOOK_PRICE: _ClassVar[ExtensionKind]
    EXPRESSIVE_PLAYLISTS: _ClassVar[ExtensionKind]
    DYNAMIC_SHOW_EPISODE: _ClassVar[ExtensionKind]
    LIVE: _ClassVar[ExtensionKind]
    SKIP_PLAYED: _ClassVar[ExtensionKind]
    AD_BREAK_FREE_PODCASTS: _ClassVar[ExtensionKind]
    ASSOCIATIONS: _ClassVar[ExtensionKind]
    PLAYLIST_EVALUATION: _ClassVar[ExtensionKind]
    CACHE_INVALIDATIONS: _ClassVar[ExtensionKind]
    LIVESTREAM_ENTITY: _ClassVar[ExtensionKind]
    SINGLE_TAP_REACTIONS: _ClassVar[ExtensionKind]
    USER_COMMENTS: _ClassVar[ExtensionKind]
    CLIENT_RESTRICTIONS: _ClassVar[ExtensionKind]
    PODCAST_GUEST: _ClassVar[ExtensionKind]
    PLAYABILITY: _ClassVar[ExtensionKind]
    COVER_IMAGE: _ClassVar[ExtensionKind]
    SHARE_TRAIT: _ClassVar[ExtensionKind]
    INSTANCE_SHARING: _ClassVar[ExtensionKind]
    ARTIST_TOUR: _ClassVar[ExtensionKind]
    AUDIOBOOK_GENRE: _ClassVar[ExtensionKind]
    CONCEPT: _ClassVar[ExtensionKind]
    ORIGINAL_VIDEO: _ClassVar[ExtensionKind]
    SMART_SHUFFLE: _ClassVar[ExtensionKind]
    LIVE_EVENTS: _ClassVar[ExtensionKind]
    AUDIOBOOK_RELATIONS: _ClassVar[ExtensionKind]
    HOME_POC_BASECARD: _ClassVar[ExtensionKind]
    AUDIOBOOK_SUPPLEMENTS: _ClassVar[ExtensionKind]
    PAID_PODCAST_BANNER: _ClassVar[ExtensionKind]
    FEWER_ADS: _ClassVar[ExtensionKind]
    WATCH_FEED_SHOW_EXPLORER: _ClassVar[ExtensionKind]
    TRACK_EXTRA_DESCRIPTORS: _ClassVar[ExtensionKind]
    TRACK_EXTRA_AUDIO_ATTRIBUTES: _ClassVar[ExtensionKind]
    TRACK_EXTENDED_CREDITS: _ClassVar[ExtensionKind]
    SIMPLE_TRAIT: _ClassVar[ExtensionKind]
    AUDIO_ASSOCIATIONS: _ClassVar[ExtensionKind]
    VIDEO_ASSOCIATIONS: _ClassVar[ExtensionKind]
    PLAYLIST_TUNER: _ClassVar[ExtensionKind]
    ARTIST_VIDEOS_ENTRYPOINT: _ClassVar[ExtensionKind]
    ALBUM_PRERELEASE: _ClassVar[ExtensionKind]
    CONTENT_ALTERNATIVES: _ClassVar[ExtensionKind]
    SNAPSHOT_SHARING: _ClassVar[ExtensionKind]
    DISPLAY_SEGMENTS_COUNT: _ClassVar[ExtensionKind]
    PODCAST_FEATURED_EPISODE: _ClassVar[ExtensionKind]
    PODCAST_SPONSORED_CONTENT: _ClassVar[ExtensionKind]
    PODCAST_EPISODE_TOPICS_LLM: _ClassVar[ExtensionKind]
    PODCAST_EPISODE_TOPICS_KG: _ClassVar[ExtensionKind]
    EPISODE_RANKING_POPULARITY: _ClassVar[ExtensionKind]
    MERCH: _ClassVar[ExtensionKind]
    COMPANION_CONTENT: _ClassVar[ExtensionKind]
    WATCH_FEED_ENTITY_EXPLORER: _ClassVar[ExtensionKind]
    ANCHOR_CARD_TRAIT: _ClassVar[ExtensionKind]
    AUDIO_PREVIEW_PLAYBACK_TRAIT: _ClassVar[ExtensionKind]
    VIDEO_PREVIEW_STILL_TRAIT: _ClassVar[ExtensionKind]
    PREVIEW_CARD_TRAIT: _ClassVar[ExtensionKind]
    SHORTCUTS_CARD_TRAIT: _ClassVar[ExtensionKind]
    VIDEO_PREVIEW_PLAYBACK_TRAIT: _ClassVar[ExtensionKind]
    COURSE_SPECIFICS: _ClassVar[ExtensionKind]
    CONCERT: _ClassVar[ExtensionKind]
    CONCERT_LOCATION: _ClassVar[ExtensionKind]
    CONCERT_MARKETING: _ClassVar[ExtensionKind]
    CONCERT_PERFORMERS: _ClassVar[ExtensionKind]
    TRACK_PAIR_TRANSITION: _ClassVar[ExtensionKind]
    CONTENT_TYPE_TRAIT: _ClassVar[ExtensionKind]
    NAME_TRAIT: _ClassVar[ExtensionKind]
    ARTWORK_TRAIT: _ClassVar[ExtensionKind]
    RELEASE_DATE_TRAIT: _ClassVar[ExtensionKind]
    CREDITS_TRAIT: _ClassVar[ExtensionKind]
    RELEASE_URI_TRAIT: _ClassVar[ExtensionKind]
    ENTITY_CAPPING: _ClassVar[ExtensionKind]
    LESSON_SPECIFICS: _ClassVar[ExtensionKind]
    CONCERT_OFFERS: _ClassVar[ExtensionKind]
    TRANSITION_MAPS: _ClassVar[ExtensionKind]
    ARTIST_HAS_CONCERTS: _ClassVar[ExtensionKind]
    PRERELEASE: _ClassVar[ExtensionKind]
    PLAYLIST_ATTRIBUTES_V2: _ClassVar[ExtensionKind]
    LIST_ATTRIBUTES_V2: _ClassVar[ExtensionKind]
    LIST_METADATA: _ClassVar[ExtensionKind]
    LIST_TUNER_AUDIO_ANALYSIS: _ClassVar[ExtensionKind]
    LIST_TUNER_CUEPOINTS: _ClassVar[ExtensionKind]
    CONTENT_RATING_TRAIT: _ClassVar[ExtensionKind]
    COPYRIGHT_TRAIT: _ClassVar[ExtensionKind]
    SUPPORTED_BADGES: _ClassVar[ExtensionKind]
    BADGES: _ClassVar[ExtensionKind]
    PREVIEW_TRAIT: _ClassVar[ExtensionKind]
    ROOTLISTABILITY_TRAIT: _ClassVar[ExtensionKind]
    LOCAL_CONCERTS: _ClassVar[ExtensionKind]
    RECOMMENDED_PLAYLISTS: _ClassVar[ExtensionKind]
    POPULAR_RELEASES: _ClassVar[ExtensionKind]
    RELATED_RELEASES: _ClassVar[ExtensionKind]
    SHARE_RESTRICTIONS: _ClassVar[ExtensionKind]
    CONCERT_OFFER: _ClassVar[ExtensionKind]
    CONCERT_OFFER_PROVIDER: _ClassVar[ExtensionKind]
    ENTITY_BOOKMARKS: _ClassVar[ExtensionKind]
    PRIVACY_TRAIT: _ClassVar[ExtensionKind]
    DUPLICATE_ITEMS_TRAIT: _ClassVar[ExtensionKind]
    REORDERING_TRAIT: _ClassVar[ExtensionKind]
    PODCAST_RESUMPTION_SEGMENTS: _ClassVar[ExtensionKind]
    ARTIST_EXPRESSION_VIDEO: _ClassVar[ExtensionKind]
    PRERELEASE_VIDEO: _ClassVar[ExtensionKind]
    GATED_ENTITY_RELATIONS: _ClassVar[ExtensionKind]
    RELATED_CREATORS_SECTION: _ClassVar[ExtensionKind]
    CREATORS_APPEARS_ON_SECTION: _ClassVar[ExtensionKind]
    PROMO_V1_TRAIT: _ClassVar[ExtensionKind]
    SPEECHLESS_SHARE_CARD: _ClassVar[ExtensionKind]
    TOP_PLAYABLES_SECTION: _ClassVar[ExtensionKind]
    AUTO_LENS: _ClassVar[ExtensionKind]
    PROMO_V3_TRAIT: _ClassVar[ExtensionKind]
    TRACK_CONTENT_FILTER: _ClassVar[ExtensionKind]
    HIGHLIGHTABILITY: _ClassVar[ExtensionKind]
    LINK_CARD_WITH_IMAGE_TRAIT: _ClassVar[ExtensionKind]
    TRACK_CLOUD_SECTION: _ClassVar[ExtensionKind]
    EPISODE_TOPICS: _ClassVar[ExtensionKind]
    VIDEO_THUMBNAIL: _ClassVar[ExtensionKind]
    IDENTITY_TRAIT: _ClassVar[ExtensionKind]
    VISUAL_IDENTITY_TRAIT: _ClassVar[ExtensionKind]
    CONTENT_TYPE_V2_TRAIT: _ClassVar[ExtensionKind]
    PREVIEW_PLAYBACK_TRAIT: _ClassVar[ExtensionKind]
    CONSUMPTION_EXPERIENCE_TRAIT: _ClassVar[ExtensionKind]
    PUBLISHING_METADATA_TRAIT: _ClassVar[ExtensionKind]
    DETAILED_EVALUATION_TRAIT: _ClassVar[ExtensionKind]
    ON_PLATFORM_REPUTATION_TRAIT: _ClassVar[ExtensionKind]
    CREDITS_V2_TRAIT: _ClassVar[ExtensionKind]
    HIGHLIGHT_PLAYABILITY_TRAIT: _ClassVar[ExtensionKind]
    SHOW_EPISODE_LIST: _ClassVar[ExtensionKind]
    AVAILABLE_RELEASES: _ClassVar[ExtensionKind]
    PLAYLIST_DESCRIPTORS: _ClassVar[ExtensionKind]
    LINK_CARD_WITH_ANIMATIONS_TRAIT: _ClassVar[ExtensionKind]
    RECAP: _ClassVar[ExtensionKind]
    AUDIOBOOK_COMPANION_CONTENT: _ClassVar[ExtensionKind]
    THREE_OH_THREE_PLAY_TRAIT: _ClassVar[ExtensionKind]
    ARTIST_WRAPPED_2024_VIDEO: _ClassVar[ExtensionKind]
    CONTAINED_CONTENT_TYPES: _ClassVar[ExtensionKind]
    CONTENT_CLASSIFICATION: _ClassVar[ExtensionKind]
    CHAPTER_SPECIFICS: _ClassVar[ExtensionKind]
    CREATOR_FAN_FUNDING: _ClassVar[ExtensionKind]
    CREATOR_PLAYLISTS_SECTION: _ClassVar[ExtensionKind]
    CREATOR_PINNED_ITEM: _ClassVar[ExtensionKind]
    PODCAST_POLL_V2: _ClassVar[ExtensionKind]
    CREATOR_APPEARS_ON_SECTION: _ClassVar[ExtensionKind]
    ARTIST_CONCERTS: _ClassVar[ExtensionKind]
UNKNOWN_EXTENSION: ExtensionKind
CANVAZ: ExtensionKind
STORYLINES: ExtensionKind
PODCAST_TOPICS: ExtensionKind
PODCAST_SEGMENTS: ExtensionKind
AUDIO_FILES: ExtensionKind
TRACK_DESCRIPTOR: ExtensionKind
PODCAST_COUNTER: ExtensionKind
ARTIST_V4: ExtensionKind
ALBUM_V4: ExtensionKind
TRACK_V4: ExtensionKind
SHOW_V4: ExtensionKind
EPISODE_V4: ExtensionKind
PODCAST_HTML_DESCRIPTION: ExtensionKind
PODCAST_QUOTES: ExtensionKind
USER_PROFILE: ExtensionKind
CANVAS_V1: ExtensionKind
SHOW_V4_BASE: ExtensionKind
SHOW_V4_EPISODES_ASSOC: ExtensionKind
TRACK_DESCRIPTOR_SIGNATURES: ExtensionKind
PODCAST_AD_SEGMENTS: ExtensionKind
EPISODE_TRANSCRIPTS: ExtensionKind
PODCAST_SUBSCRIPTIONS: ExtensionKind
EXTRACTED_COLOR: ExtensionKind
PODCAST_VIRALITY: ExtensionKind
IMAGE_SPARKLES_HACK: ExtensionKind
PODCAST_POPULARITY_HACK: ExtensionKind
AUTOMIX_MODE: ExtensionKind
CUEPOINTS: ExtensionKind
PODCAST_POLL: ExtensionKind
EPISODE_ACCESS: ExtensionKind
SHOW_ACCESS: ExtensionKind
PODCAST_QNA: ExtensionKind
CLIPS: ExtensionKind
SHOW_V5: ExtensionKind
EPISODE_V5: ExtensionKind
PODCAST_CTA_CARDS: ExtensionKind
PODCAST_RATING: ExtensionKind
DISPLAY_SEGMENTS: ExtensionKind
GREENROOM: ExtensionKind
USER_CREATED: ExtensionKind
SHOW_DESCRIPTION: ExtensionKind
SHOW_HTML_DESCRIPTION: ExtensionKind
SHOW_PLAYABILITY: ExtensionKind
EPISODE_DESCRIPTION: ExtensionKind
EPISODE_HTML_DESCRIPTION: ExtensionKind
EPISODE_PLAYABILITY: ExtensionKind
SHOW_EPISODES_ASSOC: ExtensionKind
CLIENT_CONFIG: ExtensionKind
PLAYLISTABILITY: ExtensionKind
AUDIOBOOK_V5: ExtensionKind
CHAPTER_V5: ExtensionKind
AUDIOBOOK_SPECIFICS: ExtensionKind
EPISODE_RANKING: ExtensionKind
HTML_DESCRIPTION: ExtensionKind
CREATOR_CHANNEL: ExtensionKind
AUDIOBOOK_PROVIDERS: ExtensionKind
PLAY_TRAIT: ExtensionKind
CONTENT_WARNING: ExtensionKind
IMAGE_CUE: ExtensionKind
STREAM_COUNT: ExtensionKind
AUDIO_ATTRIBUTES: ExtensionKind
NAVIGABLE_TRAIT: ExtensionKind
NEXT_BEST_EPISODE: ExtensionKind
AUDIOBOOK_PRICE: ExtensionKind
EXPRESSIVE_PLAYLISTS: ExtensionKind
DYNAMIC_SHOW_EPISODE: ExtensionKind
LIVE: ExtensionKind
SKIP_PLAYED: ExtensionKind
AD_BREAK_FREE_PODCASTS: ExtensionKind
ASSOCIATIONS: ExtensionKind
PLAYLIST_EVALUATION: ExtensionKind
CACHE_INVALIDATIONS: ExtensionKind
LIVESTREAM_ENTITY: ExtensionKind
SINGLE_TAP_REACTIONS: ExtensionKind
USER_COMMENTS: ExtensionKind
CLIENT_RESTRICTIONS: ExtensionKind
PODCAST_GUEST: ExtensionKind
PLAYABILITY: ExtensionKind
COVER_IMAGE: ExtensionKind
SHARE_TRAIT: ExtensionKind
INSTANCE_SHARING: ExtensionKind
ARTIST_TOUR: ExtensionKind
AUDIOBOOK_GENRE: ExtensionKind
CONCEPT: ExtensionKind
ORIGINAL_VIDEO: ExtensionKind
SMART_SHUFFLE: ExtensionKind
LIVE_EVENTS: ExtensionKind
AUDIOBOOK_RELATIONS: ExtensionKind
HOME_POC_BASECARD: ExtensionKind
AUDIOBOOK_SUPPLEMENTS: ExtensionKind
PAID_PODCAST_BANNER: ExtensionKind
FEWER_ADS: ExtensionKind
WATCH_FEED_SHOW_EXPLORER: ExtensionKind
TRACK_EXTRA_DESCRIPTORS: ExtensionKind
TRACK_EXTRA_AUDIO_ATTRIBUTES: ExtensionKind
TRACK_EXTENDED_CREDITS: ExtensionKind
SIMPLE_TRAIT: ExtensionKind
AUDIO_ASSOCIATIONS: ExtensionKind
VIDEO_ASSOCIATIONS: ExtensionKind
PLAYLIST_TUNER: ExtensionKind
ARTIST_VIDEOS_ENTRYPOINT: ExtensionKind
ALBUM_PRERELEASE: ExtensionKind
CONTENT_ALTERNATIVES: ExtensionKind
SNAPSHOT_SHARING: ExtensionKind
DISPLAY_SEGMENTS_COUNT: ExtensionKind
PODCAST_FEATURED_EPISODE: ExtensionKind
PODCAST_SPONSORED_CONTENT: ExtensionKind
PODCAST_EPISODE_TOPICS_LLM: ExtensionKind
PODCAST_EPISODE_TOPICS_KG: ExtensionKind
EPISODE_RANKING_POPULARITY: ExtensionKind
MERCH: ExtensionKind
COMPANION_CONTENT: ExtensionKind
WATCH_FEED_ENTITY_EXPLORER: ExtensionKind
ANCHOR_CARD_TRAIT: ExtensionKind
AUDIO_PREVIEW_PLAYBACK_TRAIT: ExtensionKind
VIDEO_PREVIEW_STILL_TRAIT: ExtensionKind
PREVIEW_CARD_TRAIT: ExtensionKind
SHORTCUTS_CARD_TRAIT: ExtensionKind
VIDEO_PREVIEW_PLAYBACK_TRAIT: ExtensionKind
COURSE_SPECIFICS: ExtensionKind
CONCERT: ExtensionKind
CONCERT_LOCATION: ExtensionKind
CONCERT_MARKETING: ExtensionKind
CONCERT_PERFORMERS: ExtensionKind
TRACK_PAIR_TRANSITION: ExtensionKind
CONTENT_TYPE_TRAIT: ExtensionKind
NAME_TRAIT: ExtensionKind
ARTWORK_TRAIT: ExtensionKind
RELEASE_DATE_TRAIT: ExtensionKind
CREDITS_TRAIT: ExtensionKind
RELEASE_URI_TRAIT: ExtensionKind
ENTITY_CAPPING: ExtensionKind
LESSON_SPECIFICS: ExtensionKind
CONCERT_OFFERS: ExtensionKind
TRANSITION_MAPS: ExtensionKind
ARTIST_HAS_CONCERTS: ExtensionKind
PRERELEASE: ExtensionKind
PLAYLIST_ATTRIBUTES_V2: ExtensionKind
LIST_ATTRIBUTES_V2: ExtensionKind
LIST_METADATA: ExtensionKind
LIST_TUNER_AUDIO_ANALYSIS: ExtensionKind
LIST_TUNER_CUEPOINTS: ExtensionKind
CONTENT_RATING_TRAIT: ExtensionKind
COPYRIGHT_TRAIT: ExtensionKind
SUPPORTED_BADGES: ExtensionKind
BADGES: ExtensionKind
PREVIEW_TRAIT: ExtensionKind
ROOTLISTABILITY_TRAIT: ExtensionKind
LOCAL_CONCERTS: ExtensionKind
RECOMMENDED_PLAYLISTS: ExtensionKind
POPULAR_RELEASES: ExtensionKind
RELATED_RELEASES: ExtensionKind
SHARE_RESTRICTIONS: ExtensionKind
CONCERT_OFFER: ExtensionKind
CONCERT_OFFER_PROVIDER: ExtensionKind
ENTITY_BOOKMARKS: ExtensionKind
PRIVACY_TRAIT: ExtensionKind
DUPLICATE_ITEMS_TRAIT: ExtensionKind
REORDERING_TRAIT: ExtensionKind
PODCAST_RESUMPTION_SEGMENTS: ExtensionKind
ARTIST_EXPRESSION_VIDEO: ExtensionKind
PRERELEASE_VIDEO: ExtensionKind
GATED_ENTITY_RELATIONS: ExtensionKind
RELATED_CREATORS_SECTION: ExtensionKind
CREATORS_APPEARS_ON_SECTION: ExtensionKind
PROMO_V1_TRAIT: ExtensionKind
SPEECHLESS_SHARE_CARD: ExtensionKind
TOP_PLAYABLES_SECTION: ExtensionKind
AUTO_LENS: ExtensionKind
PROMO_V3_TRAIT: ExtensionKind
TRACK_CONTENT_FILTER: ExtensionKind
HIGHLIGHTABILITY: ExtensionKind
LINK_CARD_WITH_IMAGE_TRAIT: ExtensionKind
TRACK_CLOUD_SECTION: ExtensionKind
EPISODE_TOPICS: ExtensionKind
VIDEO_THUMBNAIL: ExtensionKind
IDENTITY_TRAIT: ExtensionKind
VISUAL_IDENTITY_TRAIT: ExtensionKind
CONTENT_TYPE_V2_TRAIT: ExtensionKind
PREVIEW_PLAYBACK_TRAIT: ExtensionKind
CONSUMPTION_EXPERIENCE_TRAIT: ExtensionKind
PUBLISHING_METADATA_TRAIT: ExtensionKind
DETAILED_EVALUATION_TRAIT: ExtensionKind
ON_PLATFORM_REPUTATION_TRAIT: ExtensionKind
CREDITS_V2_TRAIT: ExtensionKind
HIGHLIGHT_PLAYABILITY_TRAIT: ExtensionKind
SHOW_EPISODE_LIST: ExtensionKind
AVAILABLE_RELEASES: ExtensionKind
PLAYLIST_DESCRIPTORS: ExtensionKind
LINK_CARD_WITH_ANIMATIONS_TRAIT: ExtensionKind
RECAP: ExtensionKind
AUDIOBOOK_COMPANION_CONTENT: ExtensionKind
THREE_OH_THREE_PLAY_TRAIT: ExtensionKind
ARTIST_WRAPPED_2024_VIDEO: ExtensionKind
CONTAINED_CONTENT_TYPES: ExtensionKind
CONTENT_CLASSIFICATION: ExtensionKind
CHAPTER_SPECIFICS: ExtensionKind
CREATOR_FAN_FUNDING: ExtensionKind
CREATOR_PLAYLISTS_SECTION: ExtensionKind
CREATOR_PINNED_ITEM: ExtensionKind
PODCAST_POLL_V2: ExtensionKind
CREATOR_APPEARS_ON_SECTION: ExtensionKind
ARTIST_CONCERTS: ExtensionKind

class Entity(_message.Message):
    __slots__ = ("artist", "album", "track", "show", "episode", "albumGroup")
    ARTIST_FIELD_NUMBER: _ClassVar[int]
    ALBUM_FIELD_NUMBER: _ClassVar[int]
    TRACK_FIELD_NUMBER: _ClassVar[int]
    SHOW_FIELD_NUMBER: _ClassVar[int]
    EPISODE_FIELD_NUMBER: _ClassVar[int]
    ALBUMGROUP_FIELD_NUMBER: _ClassVar[int]
    artist: Artist
    album: Album
    track: Track
    show: Show
    episode: Episode
    albumGroup: AlbumGroup
    def __init__(self, artist: _Optional[_Union[Artist, _Mapping]] = ..., album: _Optional[_Union[Album, _Mapping]] = ..., track: _Optional[_Union[Track, _Mapping]] = ..., show: _Optional[_Union[Show, _Mapping]] = ..., episode: _Optional[_Union[Episode, _Mapping]] = ..., albumGroup: _Optional[_Union[AlbumGroup, _Mapping]] = ...) -> None: ...

class LocalizedString(_message.Message):
    __slots__ = ("language", "value")
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    language: str
    value: str
    def __init__(self, language: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class Artist(_message.Message):
    __slots__ = ("gid", "name", "popularity", "top_track", "album_group", "single_group", "compilation_group", "appears_on_group", "genre", "external_id", "portrait", "biography", "activity_period", "restriction", "related", "is_portrait_album_cover", "portrait_group", "sale_period", "localized_name", "availability", "index_version", "compressed_top_track")
    GID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    POPULARITY_FIELD_NUMBER: _ClassVar[int]
    TOP_TRACK_FIELD_NUMBER: _ClassVar[int]
    ALBUM_GROUP_FIELD_NUMBER: _ClassVar[int]
    SINGLE_GROUP_FIELD_NUMBER: _ClassVar[int]
    COMPILATION_GROUP_FIELD_NUMBER: _ClassVar[int]
    APPEARS_ON_GROUP_FIELD_NUMBER: _ClassVar[int]
    GENRE_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_ID_FIELD_NUMBER: _ClassVar[int]
    PORTRAIT_FIELD_NUMBER: _ClassVar[int]
    BIOGRAPHY_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_PERIOD_FIELD_NUMBER: _ClassVar[int]
    RESTRICTION_FIELD_NUMBER: _ClassVar[int]
    RELATED_FIELD_NUMBER: _ClassVar[int]
    IS_PORTRAIT_ALBUM_COVER_FIELD_NUMBER: _ClassVar[int]
    PORTRAIT_GROUP_FIELD_NUMBER: _ClassVar[int]
    SALE_PERIOD_FIELD_NUMBER: _ClassVar[int]
    LOCALIZED_NAME_FIELD_NUMBER: _ClassVar[int]
    AVAILABILITY_FIELD_NUMBER: _ClassVar[int]
    INDEX_VERSION_FIELD_NUMBER: _ClassVar[int]
    COMPRESSED_TOP_TRACK_FIELD_NUMBER: _ClassVar[int]
    gid: bytes
    name: str
    popularity: int
    top_track: _containers.RepeatedCompositeFieldContainer[TopTracks]
    album_group: _containers.RepeatedCompositeFieldContainer[AlbumGroup]
    single_group: _containers.RepeatedCompositeFieldContainer[AlbumGroup]
    compilation_group: _containers.RepeatedCompositeFieldContainer[AlbumGroup]
    appears_on_group: _containers.RepeatedCompositeFieldContainer[AlbumGroup]
    genre: _containers.RepeatedScalarFieldContainer[str]
    external_id: _containers.RepeatedCompositeFieldContainer[ExternalId]
    portrait: _containers.RepeatedCompositeFieldContainer[Image]
    biography: _containers.RepeatedCompositeFieldContainer[Biography]
    activity_period: _containers.RepeatedCompositeFieldContainer[ActivityPeriod]
    restriction: _containers.RepeatedCompositeFieldContainer[Restriction]
    related: _containers.RepeatedCompositeFieldContainer[Artist]
    is_portrait_album_cover: bool
    portrait_group: ImageGroup
    sale_period: _containers.RepeatedCompositeFieldContainer[SalePeriod]
    localized_name: _containers.RepeatedCompositeFieldContainer[LocalizedString]
    availability: _containers.RepeatedCompositeFieldContainer[Availability]
    index_version: int
    compressed_top_track: _containers.RepeatedCompositeFieldContainer[CompressedTopTracks]
    def __init__(self, gid: _Optional[bytes] = ..., name: _Optional[str] = ..., popularity: _Optional[int] = ..., top_track: _Optional[_Iterable[_Union[TopTracks, _Mapping]]] = ..., album_group: _Optional[_Iterable[_Union[AlbumGroup, _Mapping]]] = ..., single_group: _Optional[_Iterable[_Union[AlbumGroup, _Mapping]]] = ..., compilation_group: _Optional[_Iterable[_Union[AlbumGroup, _Mapping]]] = ..., appears_on_group: _Optional[_Iterable[_Union[AlbumGroup, _Mapping]]] = ..., genre: _Optional[_Iterable[str]] = ..., external_id: _Optional[_Iterable[_Union[ExternalId, _Mapping]]] = ..., portrait: _Optional[_Iterable[_Union[Image, _Mapping]]] = ..., biography: _Optional[_Iterable[_Union[Biography, _Mapping]]] = ..., activity_period: _Optional[_Iterable[_Union[ActivityPeriod, _Mapping]]] = ..., restriction: _Optional[_Iterable[_Union[Restriction, _Mapping]]] = ..., related: _Optional[_Iterable[_Union[Artist, _Mapping]]] = ..., is_portrait_album_cover: _Optional[bool] = ..., portrait_group: _Optional[_Union[ImageGroup, _Mapping]] = ..., sale_period: _Optional[_Iterable[_Union[SalePeriod, _Mapping]]] = ..., localized_name: _Optional[_Iterable[_Union[LocalizedString, _Mapping]]] = ..., availability: _Optional[_Iterable[_Union[Availability, _Mapping]]] = ..., index_version: _Optional[int] = ..., compressed_top_track: _Optional[_Iterable[_Union[CompressedTopTracks, _Mapping]]] = ...) -> None: ...

class Album(_message.Message):
    __slots__ = ("gid", "name", "artist", "type", "label", "date", "popularity", "genre", "cover", "external_id", "disc", "review", "copyright", "restriction", "related", "sale_period", "cover_group", "original_title", "version_title", "type_str", "visibility_block", "earliest_live_timestamp", "availability", "windowed_track", "licensor", "version", "feed_gid", "delivery_id", "localized_name", "index_version", "segment_block_gid", "courtesy_line", "title", "is_metadata_hidden", "canonical_uri", "artist_with_role", "prerelease_config", "label_id", "implementation_details", "release_admin")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FOO: _ClassVar[Album.Type]
        ALBUM: _ClassVar[Album.Type]
        SINGLE: _ClassVar[Album.Type]
        COMPILATION: _ClassVar[Album.Type]
        EP: _ClassVar[Album.Type]
        AUDIOBOOK: _ClassVar[Album.Type]
        PODCAST: _ClassVar[Album.Type]
    FOO: Album.Type
    ALBUM: Album.Type
    SINGLE: Album.Type
    COMPILATION: Album.Type
    EP: Album.Type
    AUDIOBOOK: Album.Type
    PODCAST: Album.Type
    GID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ARTIST_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    POPULARITY_FIELD_NUMBER: _ClassVar[int]
    GENRE_FIELD_NUMBER: _ClassVar[int]
    COVER_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_ID_FIELD_NUMBER: _ClassVar[int]
    DISC_FIELD_NUMBER: _ClassVar[int]
    REVIEW_FIELD_NUMBER: _ClassVar[int]
    COPYRIGHT_FIELD_NUMBER: _ClassVar[int]
    RESTRICTION_FIELD_NUMBER: _ClassVar[int]
    RELATED_FIELD_NUMBER: _ClassVar[int]
    SALE_PERIOD_FIELD_NUMBER: _ClassVar[int]
    COVER_GROUP_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_TITLE_FIELD_NUMBER: _ClassVar[int]
    VERSION_TITLE_FIELD_NUMBER: _ClassVar[int]
    TYPE_STR_FIELD_NUMBER: _ClassVar[int]
    VISIBILITY_BLOCK_FIELD_NUMBER: _ClassVar[int]
    EARLIEST_LIVE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    AVAILABILITY_FIELD_NUMBER: _ClassVar[int]
    WINDOWED_TRACK_FIELD_NUMBER: _ClassVar[int]
    LICENSOR_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    FEED_GID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_ID_FIELD_NUMBER: _ClassVar[int]
    LOCALIZED_NAME_FIELD_NUMBER: _ClassVar[int]
    INDEX_VERSION_FIELD_NUMBER: _ClassVar[int]
    SEGMENT_BLOCK_GID_FIELD_NUMBER: _ClassVar[int]
    COURTESY_LINE_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    IS_METADATA_HIDDEN_FIELD_NUMBER: _ClassVar[int]
    CANONICAL_URI_FIELD_NUMBER: _ClassVar[int]
    ARTIST_WITH_ROLE_FIELD_NUMBER: _ClassVar[int]
    PRERELEASE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    IMPLEMENTATION_DETAILS_FIELD_NUMBER: _ClassVar[int]
    RELEASE_ADMIN_FIELD_NUMBER: _ClassVar[int]
    gid: bytes
    name: str
    artist: _containers.RepeatedCompositeFieldContainer[Artist]
    type: Album.Type
    label: str
    date: Date
    popularity: int
    genre: _containers.RepeatedScalarFieldContainer[str]
    cover: _containers.RepeatedCompositeFieldContainer[Image]
    external_id: _containers.RepeatedCompositeFieldContainer[ExternalId]
    disc: _containers.RepeatedCompositeFieldContainer[Disc]
    review: _containers.RepeatedScalarFieldContainer[str]
    copyright: _containers.RepeatedCompositeFieldContainer[Copyright]
    restriction: _containers.RepeatedCompositeFieldContainer[Restriction]
    related: _containers.RepeatedCompositeFieldContainer[Album]
    sale_period: _containers.RepeatedCompositeFieldContainer[SalePeriod]
    cover_group: ImageGroup
    original_title: str
    version_title: str
    type_str: str
    visibility_block: _containers.RepeatedCompositeFieldContainer[Block]
    earliest_live_timestamp: int
    availability: _containers.RepeatedCompositeFieldContainer[Availability]
    windowed_track: _containers.RepeatedCompositeFieldContainer[Track]
    licensor: Licensor
    version: int
    feed_gid: str
    delivery_id: str
    localized_name: _containers.RepeatedCompositeFieldContainer[LocalizedString]
    index_version: int
    segment_block_gid: _containers.RepeatedScalarFieldContainer[bytes]
    courtesy_line: str
    title: _containers.RepeatedCompositeFieldContainer[LocalizedTitle]
    is_metadata_hidden: bool
    canonical_uri: str
    artist_with_role: _containers.RepeatedCompositeFieldContainer[ArtistWithRole]
    prerelease_config: AlbumPrerelease
    label_id: _containers.RepeatedCompositeFieldContainer[LabelId]
    implementation_details: AlbumImplDetails
    release_admin: _containers.RepeatedCompositeFieldContainer[ReleaseAdmin]
    def __init__(self, gid: _Optional[bytes] = ..., name: _Optional[str] = ..., artist: _Optional[_Iterable[_Union[Artist, _Mapping]]] = ..., type: _Optional[_Union[Album.Type, str]] = ..., label: _Optional[str] = ..., date: _Optional[_Union[Date, _Mapping]] = ..., popularity: _Optional[int] = ..., genre: _Optional[_Iterable[str]] = ..., cover: _Optional[_Iterable[_Union[Image, _Mapping]]] = ..., external_id: _Optional[_Iterable[_Union[ExternalId, _Mapping]]] = ..., disc: _Optional[_Iterable[_Union[Disc, _Mapping]]] = ..., review: _Optional[_Iterable[str]] = ..., copyright: _Optional[_Iterable[_Union[Copyright, _Mapping]]] = ..., restriction: _Optional[_Iterable[_Union[Restriction, _Mapping]]] = ..., related: _Optional[_Iterable[_Union[Album, _Mapping]]] = ..., sale_period: _Optional[_Iterable[_Union[SalePeriod, _Mapping]]] = ..., cover_group: _Optional[_Union[ImageGroup, _Mapping]] = ..., original_title: _Optional[str] = ..., version_title: _Optional[str] = ..., type_str: _Optional[str] = ..., visibility_block: _Optional[_Iterable[_Union[Block, _Mapping]]] = ..., earliest_live_timestamp: _Optional[int] = ..., availability: _Optional[_Iterable[_Union[Availability, _Mapping]]] = ..., windowed_track: _Optional[_Iterable[_Union[Track, _Mapping]]] = ..., licensor: _Optional[_Union[Licensor, _Mapping]] = ..., version: _Optional[int] = ..., feed_gid: _Optional[str] = ..., delivery_id: _Optional[str] = ..., localized_name: _Optional[_Iterable[_Union[LocalizedString, _Mapping]]] = ..., index_version: _Optional[int] = ..., segment_block_gid: _Optional[_Iterable[bytes]] = ..., courtesy_line: _Optional[str] = ..., title: _Optional[_Iterable[_Union[LocalizedTitle, _Mapping]]] = ..., is_metadata_hidden: _Optional[bool] = ..., canonical_uri: _Optional[str] = ..., artist_with_role: _Optional[_Iterable[_Union[ArtistWithRole, _Mapping]]] = ..., prerelease_config: _Optional[_Union[AlbumPrerelease, _Mapping]] = ..., label_id: _Optional[_Iterable[_Union[LabelId, _Mapping]]] = ..., implementation_details: _Optional[_Union[AlbumImplDetails, _Mapping]] = ..., release_admin: _Optional[_Iterable[_Union[ReleaseAdmin, _Mapping]]] = ...) -> None: ...

class AlbumImplDetails(_message.Message):
    __slots__ = ("media_type",)
    MEDIA_TYPE_FIELD_NUMBER: _ClassVar[int]
    media_type: str
    def __init__(self, media_type: _Optional[str] = ...) -> None: ...

class LocalizedTitle(_message.Message):
    __slots__ = ("language", "is_default", "display_text", "title", "subtitle")
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    IS_DEFAULT_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_TEXT_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    SUBTITLE_FIELD_NUMBER: _ClassVar[int]
    language: str
    is_default: bool
    display_text: str
    title: str
    subtitle: str
    def __init__(self, language: _Optional[str] = ..., is_default: _Optional[bool] = ..., display_text: _Optional[str] = ..., title: _Optional[str] = ..., subtitle: _Optional[str] = ...) -> None: ...

class Track(_message.Message):
    __slots__ = ("gid", "name", "album", "artist", "number", "disc_number", "duration", "popularity", "explicit", "external_id", "restriction", "file", "alternative", "sale_period", "preview", "tags", "earliest_live_timestamp", "has_lyrics", "availability", "lyrics_country", "licensor", "language_of_performance", "localized_name", "original_audio", "content_rating", "index_version", "original_title", "version_title", "segment_block_gid", "artist_with_role", "title", "is_metadata_hidden", "visibility_block", "canonical_uri", "prerelease_config", "original_video")
    GID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ALBUM_FIELD_NUMBER: _ClassVar[int]
    ARTIST_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    DISC_NUMBER_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    POPULARITY_FIELD_NUMBER: _ClassVar[int]
    EXPLICIT_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_ID_FIELD_NUMBER: _ClassVar[int]
    RESTRICTION_FIELD_NUMBER: _ClassVar[int]
    FILE_FIELD_NUMBER: _ClassVar[int]
    ALTERNATIVE_FIELD_NUMBER: _ClassVar[int]
    SALE_PERIOD_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    EARLIEST_LIVE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    HAS_LYRICS_FIELD_NUMBER: _ClassVar[int]
    AVAILABILITY_FIELD_NUMBER: _ClassVar[int]
    LYRICS_COUNTRY_FIELD_NUMBER: _ClassVar[int]
    LICENSOR_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_OF_PERFORMANCE_FIELD_NUMBER: _ClassVar[int]
    LOCALIZED_NAME_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_AUDIO_FIELD_NUMBER: _ClassVar[int]
    CONTENT_RATING_FIELD_NUMBER: _ClassVar[int]
    INDEX_VERSION_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_TITLE_FIELD_NUMBER: _ClassVar[int]
    VERSION_TITLE_FIELD_NUMBER: _ClassVar[int]
    SEGMENT_BLOCK_GID_FIELD_NUMBER: _ClassVar[int]
    ARTIST_WITH_ROLE_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    IS_METADATA_HIDDEN_FIELD_NUMBER: _ClassVar[int]
    VISIBILITY_BLOCK_FIELD_NUMBER: _ClassVar[int]
    CANONICAL_URI_FIELD_NUMBER: _ClassVar[int]
    PRERELEASE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_VIDEO_FIELD_NUMBER: _ClassVar[int]
    gid: bytes
    name: str
    album: Album
    artist: _containers.RepeatedCompositeFieldContainer[Artist]
    number: int
    disc_number: int
    duration: int
    popularity: int
    explicit: bool
    external_id: _containers.RepeatedCompositeFieldContainer[ExternalId]
    restriction: _containers.RepeatedCompositeFieldContainer[Restriction]
    file: _containers.RepeatedCompositeFieldContainer[AudioFile]
    alternative: _containers.RepeatedCompositeFieldContainer[Track]
    sale_period: _containers.RepeatedCompositeFieldContainer[SalePeriod]
    preview: _containers.RepeatedCompositeFieldContainer[AudioFile]
    tags: _containers.RepeatedScalarFieldContainer[str]
    earliest_live_timestamp: int
    has_lyrics: bool
    availability: _containers.RepeatedCompositeFieldContainer[Availability]
    lyrics_country: _containers.RepeatedScalarFieldContainer[str]
    licensor: Licensor
    language_of_performance: _containers.RepeatedScalarFieldContainer[str]
    localized_name: _containers.RepeatedCompositeFieldContainer[LocalizedString]
    original_audio: Audio
    content_rating: _containers.RepeatedCompositeFieldContainer[ContentRating]
    index_version: int
    original_title: str
    version_title: str
    segment_block_gid: _containers.RepeatedScalarFieldContainer[bytes]
    artist_with_role: _containers.RepeatedCompositeFieldContainer[ArtistWithRole]
    title: _containers.RepeatedCompositeFieldContainer[LocalizedTitle]
    is_metadata_hidden: bool
    visibility_block: _containers.RepeatedCompositeFieldContainer[Block]
    canonical_uri: str
    prerelease_config: TrackPrerelease
    original_video: _containers.RepeatedCompositeFieldContainer[Video]
    def __init__(self, gid: _Optional[bytes] = ..., name: _Optional[str] = ..., album: _Optional[_Union[Album, _Mapping]] = ..., artist: _Optional[_Iterable[_Union[Artist, _Mapping]]] = ..., number: _Optional[int] = ..., disc_number: _Optional[int] = ..., duration: _Optional[int] = ..., popularity: _Optional[int] = ..., explicit: _Optional[bool] = ..., external_id: _Optional[_Iterable[_Union[ExternalId, _Mapping]]] = ..., restriction: _Optional[_Iterable[_Union[Restriction, _Mapping]]] = ..., file: _Optional[_Iterable[_Union[AudioFile, _Mapping]]] = ..., alternative: _Optional[_Iterable[_Union[Track, _Mapping]]] = ..., sale_period: _Optional[_Iterable[_Union[SalePeriod, _Mapping]]] = ..., preview: _Optional[_Iterable[_Union[AudioFile, _Mapping]]] = ..., tags: _Optional[_Iterable[str]] = ..., earliest_live_timestamp: _Optional[int] = ..., has_lyrics: _Optional[bool] = ..., availability: _Optional[_Iterable[_Union[Availability, _Mapping]]] = ..., lyrics_country: _Optional[_Iterable[str]] = ..., licensor: _Optional[_Union[Licensor, _Mapping]] = ..., language_of_performance: _Optional[_Iterable[str]] = ..., localized_name: _Optional[_Iterable[_Union[LocalizedString, _Mapping]]] = ..., original_audio: _Optional[_Union[Audio, _Mapping]] = ..., content_rating: _Optional[_Iterable[_Union[ContentRating, _Mapping]]] = ..., index_version: _Optional[int] = ..., original_title: _Optional[str] = ..., version_title: _Optional[str] = ..., segment_block_gid: _Optional[_Iterable[bytes]] = ..., artist_with_role: _Optional[_Iterable[_Union[ArtistWithRole, _Mapping]]] = ..., title: _Optional[_Iterable[_Union[LocalizedTitle, _Mapping]]] = ..., is_metadata_hidden: _Optional[bool] = ..., visibility_block: _Optional[_Iterable[_Union[Block, _Mapping]]] = ..., canonical_uri: _Optional[str] = ..., prerelease_config: _Optional[_Union[TrackPrerelease, _Mapping]] = ..., original_video: _Optional[_Iterable[_Union[Video, _Mapping]]] = ...) -> None: ...

class ArtistWithRole(_message.Message):
    __slots__ = ("artist_gid", "artist_name", "role", "localized_name")
    class ArtistRole(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ARTIST_ROLE_UNKNOWN: _ClassVar[ArtistWithRole.ArtistRole]
        ARTIST_ROLE_MAIN_ARTIST: _ClassVar[ArtistWithRole.ArtistRole]
        ARTIST_ROLE_FEATURED_ARTIST: _ClassVar[ArtistWithRole.ArtistRole]
        ARTIST_ROLE_REMIXER: _ClassVar[ArtistWithRole.ArtistRole]
        ARTIST_ROLE_ACTOR: _ClassVar[ArtistWithRole.ArtistRole]
        ARTIST_ROLE_COMPOSER: _ClassVar[ArtistWithRole.ArtistRole]
        ARTIST_ROLE_CONDUCTOR: _ClassVar[ArtistWithRole.ArtistRole]
        ARTIST_ROLE_ORCHESTRA: _ClassVar[ArtistWithRole.ArtistRole]
    ARTIST_ROLE_UNKNOWN: ArtistWithRole.ArtistRole
    ARTIST_ROLE_MAIN_ARTIST: ArtistWithRole.ArtistRole
    ARTIST_ROLE_FEATURED_ARTIST: ArtistWithRole.ArtistRole
    ARTIST_ROLE_REMIXER: ArtistWithRole.ArtistRole
    ARTIST_ROLE_ACTOR: ArtistWithRole.ArtistRole
    ARTIST_ROLE_COMPOSER: ArtistWithRole.ArtistRole
    ARTIST_ROLE_CONDUCTOR: ArtistWithRole.ArtistRole
    ARTIST_ROLE_ORCHESTRA: ArtistWithRole.ArtistRole
    ARTIST_GID_FIELD_NUMBER: _ClassVar[int]
    ARTIST_NAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    LOCALIZED_NAME_FIELD_NUMBER: _ClassVar[int]
    artist_gid: bytes
    artist_name: str
    role: ArtistWithRole.ArtistRole
    localized_name: _containers.RepeatedCompositeFieldContainer[LocalizedString]
    def __init__(self, artist_gid: _Optional[bytes] = ..., artist_name: _Optional[str] = ..., role: _Optional[_Union[ArtistWithRole.ArtistRole, str]] = ..., localized_name: _Optional[_Iterable[_Union[LocalizedString, _Mapping]]] = ...) -> None: ...

class Show(_message.Message):
    __slots__ = ("gid", "name", "localized_name", "description", "deprecated_popularity", "publisher", "language", "explicit", "cover_image", "episode", "copyright", "restriction", "keyword", "media_type", "consumption_order", "interpret_restriction_using_geoip", "sale_period", "availability", "country_of_origin", "categories", "passthrough", "employee_only", "trailer_uri", "html_description", "music_and_talk", "authorization", "is_enterprise_content", "show_type", "is_audiobook", "is_creator_channel", "is_searchable", "deprecated_spotify_user_id", "is_paywall_content", "is_podcast_show")
    class MediaType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MIXED: _ClassVar[Show.MediaType]
        AUDIO: _ClassVar[Show.MediaType]
        VIDEO: _ClassVar[Show.MediaType]
    MIXED: Show.MediaType
    AUDIO: Show.MediaType
    VIDEO: Show.MediaType
    class ConsumptionOrder(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FOO: _ClassVar[Show.ConsumptionOrder]
        SEQUENTIAL: _ClassVar[Show.ConsumptionOrder]
        EPISODIC: _ClassVar[Show.ConsumptionOrder]
        RECENT: _ClassVar[Show.ConsumptionOrder]
    FOO: Show.ConsumptionOrder
    SEQUENTIAL: Show.ConsumptionOrder
    EPISODIC: Show.ConsumptionOrder
    RECENT: Show.ConsumptionOrder
    class Passthrough(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[Show.Passthrough]
        NONE: _ClassVar[Show.Passthrough]
        ALLOWED: _ClassVar[Show.Passthrough]
        MANDATORY: _ClassVar[Show.Passthrough]
    UNKNOWN: Show.Passthrough
    NONE: Show.Passthrough
    ALLOWED: Show.Passthrough
    MANDATORY: Show.Passthrough
    GID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LOCALIZED_NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DEPRECATED_POPULARITY_FIELD_NUMBER: _ClassVar[int]
    PUBLISHER_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    EXPLICIT_FIELD_NUMBER: _ClassVar[int]
    COVER_IMAGE_FIELD_NUMBER: _ClassVar[int]
    EPISODE_FIELD_NUMBER: _ClassVar[int]
    COPYRIGHT_FIELD_NUMBER: _ClassVar[int]
    RESTRICTION_FIELD_NUMBER: _ClassVar[int]
    KEYWORD_FIELD_NUMBER: _ClassVar[int]
    MEDIA_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONSUMPTION_ORDER_FIELD_NUMBER: _ClassVar[int]
    INTERPRET_RESTRICTION_USING_GEOIP_FIELD_NUMBER: _ClassVar[int]
    SALE_PERIOD_FIELD_NUMBER: _ClassVar[int]
    AVAILABILITY_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_OF_ORIGIN_FIELD_NUMBER: _ClassVar[int]
    CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    PASSTHROUGH_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ONLY_FIELD_NUMBER: _ClassVar[int]
    TRAILER_URI_FIELD_NUMBER: _ClassVar[int]
    HTML_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MUSIC_AND_TALK_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_FIELD_NUMBER: _ClassVar[int]
    IS_ENTERPRISE_CONTENT_FIELD_NUMBER: _ClassVar[int]
    SHOW_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_AUDIOBOOK_FIELD_NUMBER: _ClassVar[int]
    IS_CREATOR_CHANNEL_FIELD_NUMBER: _ClassVar[int]
    IS_SEARCHABLE_FIELD_NUMBER: _ClassVar[int]
    DEPRECATED_SPOTIFY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    IS_PAYWALL_CONTENT_FIELD_NUMBER: _ClassVar[int]
    IS_PODCAST_SHOW_FIELD_NUMBER: _ClassVar[int]
    gid: bytes
    name: str
    localized_name: _containers.RepeatedCompositeFieldContainer[LocalizedString]
    description: str
    deprecated_popularity: int
    publisher: str
    language: str
    explicit: bool
    cover_image: ImageGroup
    episode: _containers.RepeatedCompositeFieldContainer[Episode]
    copyright: _containers.RepeatedCompositeFieldContainer[Copyright]
    restriction: _containers.RepeatedCompositeFieldContainer[Restriction]
    keyword: _containers.RepeatedScalarFieldContainer[str]
    media_type: Show.MediaType
    consumption_order: Show.ConsumptionOrder
    interpret_restriction_using_geoip: bool
    sale_period: _containers.RepeatedCompositeFieldContainer[SalePeriod]
    availability: _containers.RepeatedCompositeFieldContainer[Availability]
    country_of_origin: str
    categories: _containers.RepeatedCompositeFieldContainer[Categories]
    passthrough: Show.Passthrough
    employee_only: bool
    trailer_uri: str
    html_description: str
    music_and_talk: bool
    authorization: Authorization
    is_enterprise_content: bool
    show_type: ShowType
    is_audiobook: bool
    is_creator_channel: bool
    is_searchable: bool
    deprecated_spotify_user_id: str
    is_paywall_content: bool
    is_podcast_show: bool
    def __init__(self, gid: _Optional[bytes] = ..., name: _Optional[str] = ..., localized_name: _Optional[_Iterable[_Union[LocalizedString, _Mapping]]] = ..., description: _Optional[str] = ..., deprecated_popularity: _Optional[int] = ..., publisher: _Optional[str] = ..., language: _Optional[str] = ..., explicit: _Optional[bool] = ..., cover_image: _Optional[_Union[ImageGroup, _Mapping]] = ..., episode: _Optional[_Iterable[_Union[Episode, _Mapping]]] = ..., copyright: _Optional[_Iterable[_Union[Copyright, _Mapping]]] = ..., restriction: _Optional[_Iterable[_Union[Restriction, _Mapping]]] = ..., keyword: _Optional[_Iterable[str]] = ..., media_type: _Optional[_Union[Show.MediaType, str]] = ..., consumption_order: _Optional[_Union[Show.ConsumptionOrder, str]] = ..., interpret_restriction_using_geoip: _Optional[bool] = ..., sale_period: _Optional[_Iterable[_Union[SalePeriod, _Mapping]]] = ..., availability: _Optional[_Iterable[_Union[Availability, _Mapping]]] = ..., country_of_origin: _Optional[str] = ..., categories: _Optional[_Iterable[_Union[Categories, _Mapping]]] = ..., passthrough: _Optional[_Union[Show.Passthrough, str]] = ..., employee_only: _Optional[bool] = ..., trailer_uri: _Optional[str] = ..., html_description: _Optional[str] = ..., music_and_talk: _Optional[bool] = ..., authorization: _Optional[_Union[Authorization, _Mapping]] = ..., is_enterprise_content: _Optional[bool] = ..., show_type: _Optional[_Union[ShowType, _Mapping]] = ..., is_audiobook: _Optional[bool] = ..., is_creator_channel: _Optional[bool] = ..., is_searchable: _Optional[bool] = ..., deprecated_spotify_user_id: _Optional[str] = ..., is_paywall_content: _Optional[bool] = ..., is_podcast_show: _Optional[bool] = ...) -> None: ...

class Episode(_message.Message):
    __slots__ = ("gid", "name", "duration", "audio", "localized_name", "description", "number", "publish_time", "deprecated_popularity", "cover_image", "language", "explicit", "show", "video", "video_preview", "audio_preview", "restriction", "freeze_frame", "keyword", "interpret_restriction_using_geoip", "suppress_monetization", "sale_period", "allow_background_playback", "availability", "external_url", "original_audio", "employee_only", "rss_guid", "type", "season_number", "episode_number", "html_description", "music_and_talk", "authorization", "is_enterprise_content", "is_paywall_content", "content_rating", "is_audiobook_chapter", "is_podcast_short", "is_searchable", "deprecated_spotify_user_id", "is_podcast_episode")
    class EpisodeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FULL: _ClassVar[Episode.EpisodeType]
        TRAILER: _ClassVar[Episode.EpisodeType]
        BONUS: _ClassVar[Episode.EpisodeType]
    FULL: Episode.EpisodeType
    TRAILER: Episode.EpisodeType
    BONUS: Episode.EpisodeType
    GID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    AUDIO_FIELD_NUMBER: _ClassVar[int]
    LOCALIZED_NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_TIME_FIELD_NUMBER: _ClassVar[int]
    DEPRECATED_POPULARITY_FIELD_NUMBER: _ClassVar[int]
    COVER_IMAGE_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    EXPLICIT_FIELD_NUMBER: _ClassVar[int]
    SHOW_FIELD_NUMBER: _ClassVar[int]
    VIDEO_FIELD_NUMBER: _ClassVar[int]
    VIDEO_PREVIEW_FIELD_NUMBER: _ClassVar[int]
    AUDIO_PREVIEW_FIELD_NUMBER: _ClassVar[int]
    RESTRICTION_FIELD_NUMBER: _ClassVar[int]
    FREEZE_FRAME_FIELD_NUMBER: _ClassVar[int]
    KEYWORD_FIELD_NUMBER: _ClassVar[int]
    INTERPRET_RESTRICTION_USING_GEOIP_FIELD_NUMBER: _ClassVar[int]
    SUPPRESS_MONETIZATION_FIELD_NUMBER: _ClassVar[int]
    SALE_PERIOD_FIELD_NUMBER: _ClassVar[int]
    ALLOW_BACKGROUND_PLAYBACK_FIELD_NUMBER: _ClassVar[int]
    AVAILABILITY_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_URL_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_AUDIO_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ONLY_FIELD_NUMBER: _ClassVar[int]
    RSS_GUID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SEASON_NUMBER_FIELD_NUMBER: _ClassVar[int]
    EPISODE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    HTML_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MUSIC_AND_TALK_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_FIELD_NUMBER: _ClassVar[int]
    IS_ENTERPRISE_CONTENT_FIELD_NUMBER: _ClassVar[int]
    IS_PAYWALL_CONTENT_FIELD_NUMBER: _ClassVar[int]
    CONTENT_RATING_FIELD_NUMBER: _ClassVar[int]
    IS_AUDIOBOOK_CHAPTER_FIELD_NUMBER: _ClassVar[int]
    IS_PODCAST_SHORT_FIELD_NUMBER: _ClassVar[int]
    IS_SEARCHABLE_FIELD_NUMBER: _ClassVar[int]
    DEPRECATED_SPOTIFY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    IS_PODCAST_EPISODE_FIELD_NUMBER: _ClassVar[int]
    gid: bytes
    name: str
    duration: int
    audio: _containers.RepeatedCompositeFieldContainer[AudioFile]
    localized_name: _containers.RepeatedCompositeFieldContainer[LocalizedString]
    description: str
    number: int
    publish_time: Date
    deprecated_popularity: int
    cover_image: ImageGroup
    language: str
    explicit: bool
    show: Show
    video: _containers.RepeatedCompositeFieldContainer[VideoFile]
    video_preview: _containers.RepeatedCompositeFieldContainer[VideoFile]
    audio_preview: _containers.RepeatedCompositeFieldContainer[AudioFile]
    restriction: _containers.RepeatedCompositeFieldContainer[Restriction]
    freeze_frame: ImageGroup
    keyword: _containers.RepeatedScalarFieldContainer[str]
    interpret_restriction_using_geoip: bool
    suppress_monetization: bool
    sale_period: _containers.RepeatedCompositeFieldContainer[SalePeriod]
    allow_background_playback: bool
    availability: _containers.RepeatedCompositeFieldContainer[Availability]
    external_url: str
    original_audio: Audio
    employee_only: bool
    rss_guid: str
    type: Episode.EpisodeType
    season_number: int
    episode_number: int
    html_description: str
    music_and_talk: bool
    authorization: Authorization
    is_enterprise_content: bool
    is_paywall_content: bool
    content_rating: _containers.RepeatedCompositeFieldContainer[ContentRating]
    is_audiobook_chapter: bool
    is_podcast_short: bool
    is_searchable: bool
    deprecated_spotify_user_id: str
    is_podcast_episode: bool
    def __init__(self, gid: _Optional[bytes] = ..., name: _Optional[str] = ..., duration: _Optional[int] = ..., audio: _Optional[_Iterable[_Union[AudioFile, _Mapping]]] = ..., localized_name: _Optional[_Iterable[_Union[LocalizedString, _Mapping]]] = ..., description: _Optional[str] = ..., number: _Optional[int] = ..., publish_time: _Optional[_Union[Date, _Mapping]] = ..., deprecated_popularity: _Optional[int] = ..., cover_image: _Optional[_Union[ImageGroup, _Mapping]] = ..., language: _Optional[str] = ..., explicit: _Optional[bool] = ..., show: _Optional[_Union[Show, _Mapping]] = ..., video: _Optional[_Iterable[_Union[VideoFile, _Mapping]]] = ..., video_preview: _Optional[_Iterable[_Union[VideoFile, _Mapping]]] = ..., audio_preview: _Optional[_Iterable[_Union[AudioFile, _Mapping]]] = ..., restriction: _Optional[_Iterable[_Union[Restriction, _Mapping]]] = ..., freeze_frame: _Optional[_Union[ImageGroup, _Mapping]] = ..., keyword: _Optional[_Iterable[str]] = ..., interpret_restriction_using_geoip: _Optional[bool] = ..., suppress_monetization: _Optional[bool] = ..., sale_period: _Optional[_Iterable[_Union[SalePeriod, _Mapping]]] = ..., allow_background_playback: _Optional[bool] = ..., availability: _Optional[_Iterable[_Union[Availability, _Mapping]]] = ..., external_url: _Optional[str] = ..., original_audio: _Optional[_Union[Audio, _Mapping]] = ..., employee_only: _Optional[bool] = ..., rss_guid: _Optional[str] = ..., type: _Optional[_Union[Episode.EpisodeType, str]] = ..., season_number: _Optional[int] = ..., episode_number: _Optional[int] = ..., html_description: _Optional[str] = ..., music_and_talk: _Optional[bool] = ..., authorization: _Optional[_Union[Authorization, _Mapping]] = ..., is_enterprise_content: _Optional[bool] = ..., is_paywall_content: _Optional[bool] = ..., content_rating: _Optional[_Iterable[_Union[ContentRating, _Mapping]]] = ..., is_audiobook_chapter: _Optional[bool] = ..., is_podcast_short: _Optional[bool] = ..., is_searchable: _Optional[bool] = ..., deprecated_spotify_user_id: _Optional[str] = ..., is_podcast_episode: _Optional[bool] = ...) -> None: ...

class Licensor(_message.Message):
    __slots__ = ("uuid",)
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: bytes
    def __init__(self, uuid: _Optional[bytes] = ...) -> None: ...

class Audio(_message.Message):
    __slots__ = ("uuid",)
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: bytes
    def __init__(self, uuid: _Optional[bytes] = ...) -> None: ...

class TopTracks(_message.Message):
    __slots__ = ("country", "track")
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    TRACK_FIELD_NUMBER: _ClassVar[int]
    country: str
    track: _containers.RepeatedCompositeFieldContainer[Track]
    def __init__(self, country: _Optional[str] = ..., track: _Optional[_Iterable[_Union[Track, _Mapping]]] = ...) -> None: ...

class CompressedTopTracks(_message.Message):
    __slots__ = ("country", "track")
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    TRACK_FIELD_NUMBER: _ClassVar[int]
    country: _containers.RepeatedScalarFieldContainer[str]
    track: _containers.RepeatedCompositeFieldContainer[Track]
    def __init__(self, country: _Optional[_Iterable[str]] = ..., track: _Optional[_Iterable[_Union[Track, _Mapping]]] = ...) -> None: ...

class ActivityPeriod(_message.Message):
    __slots__ = ("start_year", "end_year", "decade")
    START_YEAR_FIELD_NUMBER: _ClassVar[int]
    END_YEAR_FIELD_NUMBER: _ClassVar[int]
    DECADE_FIELD_NUMBER: _ClassVar[int]
    start_year: int
    end_year: int
    decade: int
    def __init__(self, start_year: _Optional[int] = ..., end_year: _Optional[int] = ..., decade: _Optional[int] = ...) -> None: ...

class AlbumGroup(_message.Message):
    __slots__ = ("album",)
    ALBUM_FIELD_NUMBER: _ClassVar[int]
    album: _containers.RepeatedCompositeFieldContainer[Album]
    def __init__(self, album: _Optional[_Iterable[_Union[Album, _Mapping]]] = ...) -> None: ...

class Date(_message.Message):
    __slots__ = ("year", "month", "day", "hour", "minute")
    YEAR_FIELD_NUMBER: _ClassVar[int]
    MONTH_FIELD_NUMBER: _ClassVar[int]
    DAY_FIELD_NUMBER: _ClassVar[int]
    HOUR_FIELD_NUMBER: _ClassVar[int]
    MINUTE_FIELD_NUMBER: _ClassVar[int]
    year: int
    month: int
    day: int
    hour: int
    minute: int
    def __init__(self, year: _Optional[int] = ..., month: _Optional[int] = ..., day: _Optional[int] = ..., hour: _Optional[int] = ..., minute: _Optional[int] = ...) -> None: ...

class Image(_message.Message):
    __slots__ = ("file_id", "size", "width", "height")
    class Size(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFAULT: _ClassVar[Image.Size]
        SMALL: _ClassVar[Image.Size]
        LARGE: _ClassVar[Image.Size]
        XLARGE: _ClassVar[Image.Size]
        XXLARGE: _ClassVar[Image.Size]
    DEFAULT: Image.Size
    SMALL: Image.Size
    LARGE: Image.Size
    XLARGE: Image.Size
    XXLARGE: Image.Size
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    file_id: bytes
    size: Image.Size
    width: int
    height: int
    def __init__(self, file_id: _Optional[bytes] = ..., size: _Optional[_Union[Image.Size, str]] = ..., width: _Optional[int] = ..., height: _Optional[int] = ...) -> None: ...

class ImageGroup(_message.Message):
    __slots__ = ("image",)
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    image: _containers.RepeatedCompositeFieldContainer[Image]
    def __init__(self, image: _Optional[_Iterable[_Union[Image, _Mapping]]] = ...) -> None: ...

class Biography(_message.Message):
    __slots__ = ("text", "portrait", "portrait_group", "localized_text")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    PORTRAIT_FIELD_NUMBER: _ClassVar[int]
    PORTRAIT_GROUP_FIELD_NUMBER: _ClassVar[int]
    LOCALIZED_TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    portrait: _containers.RepeatedCompositeFieldContainer[Image]
    portrait_group: _containers.RepeatedCompositeFieldContainer[ImageGroup]
    localized_text: _containers.RepeatedCompositeFieldContainer[LocalizedString]
    def __init__(self, text: _Optional[str] = ..., portrait: _Optional[_Iterable[_Union[Image, _Mapping]]] = ..., portrait_group: _Optional[_Iterable[_Union[ImageGroup, _Mapping]]] = ..., localized_text: _Optional[_Iterable[_Union[LocalizedString, _Mapping]]] = ...) -> None: ...

class Disc(_message.Message):
    __slots__ = ("number", "name", "track")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TRACK_FIELD_NUMBER: _ClassVar[int]
    number: int
    name: str
    track: _containers.RepeatedCompositeFieldContainer[Track]
    def __init__(self, number: _Optional[int] = ..., name: _Optional[str] = ..., track: _Optional[_Iterable[_Union[Track, _Mapping]]] = ...) -> None: ...

class Copyright(_message.Message):
    __slots__ = ("type", "text")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        P: _ClassVar[Copyright.Type]
        C: _ClassVar[Copyright.Type]
    P: Copyright.Type
    C: Copyright.Type
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    type: Copyright.Type
    text: str
    def __init__(self, type: _Optional[_Union[Copyright.Type, str]] = ..., text: _Optional[str] = ...) -> None: ...

class Restriction(_message.Message):
    __slots__ = ("catalogue", "countries_allowed", "countries_forbidden", "type", "catalogue_str")
    class Catalogue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AD: _ClassVar[Restriction.Catalogue]
        SUBSCRIPTION: _ClassVar[Restriction.Catalogue]
        CATALOGUE_ALL: _ClassVar[Restriction.Catalogue]
        SHUFFLE: _ClassVar[Restriction.Catalogue]
        COMMERCIAL: _ClassVar[Restriction.Catalogue]
    AD: Restriction.Catalogue
    SUBSCRIPTION: Restriction.Catalogue
    CATALOGUE_ALL: Restriction.Catalogue
    SHUFFLE: Restriction.Catalogue
    COMMERCIAL: Restriction.Catalogue
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STREAMING: _ClassVar[Restriction.Type]
    STREAMING: Restriction.Type
    CATALOGUE_FIELD_NUMBER: _ClassVar[int]
    COUNTRIES_ALLOWED_FIELD_NUMBER: _ClassVar[int]
    COUNTRIES_FORBIDDEN_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CATALOGUE_STR_FIELD_NUMBER: _ClassVar[int]
    catalogue: _containers.RepeatedScalarFieldContainer[Restriction.Catalogue]
    countries_allowed: str
    countries_forbidden: str
    type: Restriction.Type
    catalogue_str: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, catalogue: _Optional[_Iterable[_Union[Restriction.Catalogue, str]]] = ..., countries_allowed: _Optional[str] = ..., countries_forbidden: _Optional[str] = ..., type: _Optional[_Union[Restriction.Type, str]] = ..., catalogue_str: _Optional[_Iterable[str]] = ...) -> None: ...

class Availability(_message.Message):
    __slots__ = ("catalogue_str", "start")
    CATALOGUE_STR_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    catalogue_str: _containers.RepeatedScalarFieldContainer[str]
    start: Date
    def __init__(self, catalogue_str: _Optional[_Iterable[str]] = ..., start: _Optional[_Union[Date, _Mapping]] = ...) -> None: ...

class Categories(_message.Message):
    __slots__ = ("name", "subcategories")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SUBCATEGORIES_FIELD_NUMBER: _ClassVar[int]
    name: str
    subcategories: _containers.RepeatedCompositeFieldContainer[SubCategories]
    def __init__(self, name: _Optional[str] = ..., subcategories: _Optional[_Iterable[_Union[SubCategories, _Mapping]]] = ...) -> None: ...

class SubCategories(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class SalePeriod(_message.Message):
    __slots__ = ("restriction", "start", "end")
    RESTRICTION_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    restriction: _containers.RepeatedCompositeFieldContainer[Restriction]
    start: Date
    end: Date
    def __init__(self, restriction: _Optional[_Iterable[_Union[Restriction, _Mapping]]] = ..., start: _Optional[_Union[Date, _Mapping]] = ..., end: _Optional[_Union[Date, _Mapping]] = ...) -> None: ...

class ExternalId(_message.Message):
    __slots__ = ("type", "id")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    type: str
    id: str
    def __init__(self, type: _Optional[str] = ..., id: _Optional[str] = ...) -> None: ...

class LabelId(_message.Message):
    __slots__ = ("type", "value")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    type: str
    value: str
    def __init__(self, type: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class AudioFile(_message.Message):
    __slots__ = ("file_id", "format")
    class Format(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OGG_VORBIS_96: _ClassVar[AudioFile.Format]
        OGG_VORBIS_160: _ClassVar[AudioFile.Format]
        OGG_VORBIS_320: _ClassVar[AudioFile.Format]
        MP3_256: _ClassVar[AudioFile.Format]
        MP3_320: _ClassVar[AudioFile.Format]
        MP3_160: _ClassVar[AudioFile.Format]
        MP3_96: _ClassVar[AudioFile.Format]
        MP3_160_ENC: _ClassVar[AudioFile.Format]
        AAC_24: _ClassVar[AudioFile.Format]
        AAC_48: _ClassVar[AudioFile.Format]
        MP4_128: _ClassVar[AudioFile.Format]
        MP4_256: _ClassVar[AudioFile.Format]
        MP4_128_DUAL: _ClassVar[AudioFile.Format]
        MP4_256_DUAL: _ClassVar[AudioFile.Format]
        MP4_128_CBCS: _ClassVar[AudioFile.Format]
        MP4_256_CBCS: _ClassVar[AudioFile.Format]
        FLAC_FLAC: _ClassVar[AudioFile.Format]
        MP4_FLAC: _ClassVar[AudioFile.Format]
        XHE_AAC_24: _ClassVar[AudioFile.Format]
        XHE_AAC_16: _ClassVar[AudioFile.Format]
        XHE_AAC_12: _ClassVar[AudioFile.Format]
        HE_AAC_64: _ClassVar[AudioFile.Format]
        FLAC_FLAC_24BIT: _ClassVar[AudioFile.Format]
        MP4_FLAC_24BIT: _ClassVar[AudioFile.Format]
    OGG_VORBIS_96: AudioFile.Format
    OGG_VORBIS_160: AudioFile.Format
    OGG_VORBIS_320: AudioFile.Format
    MP3_256: AudioFile.Format
    MP3_320: AudioFile.Format
    MP3_160: AudioFile.Format
    MP3_96: AudioFile.Format
    MP3_160_ENC: AudioFile.Format
    AAC_24: AudioFile.Format
    AAC_48: AudioFile.Format
    MP4_128: AudioFile.Format
    MP4_256: AudioFile.Format
    MP4_128_DUAL: AudioFile.Format
    MP4_256_DUAL: AudioFile.Format
    MP4_128_CBCS: AudioFile.Format
    MP4_256_CBCS: AudioFile.Format
    FLAC_FLAC: AudioFile.Format
    MP4_FLAC: AudioFile.Format
    XHE_AAC_24: AudioFile.Format
    XHE_AAC_16: AudioFile.Format
    XHE_AAC_12: AudioFile.Format
    HE_AAC_64: AudioFile.Format
    FLAC_FLAC_24BIT: AudioFile.Format
    MP4_FLAC_24BIT: AudioFile.Format
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    file_id: bytes
    format: AudioFile.Format
    def __init__(self, file_id: _Optional[bytes] = ..., format: _Optional[_Union[AudioFile.Format, str]] = ...) -> None: ...

class Video(_message.Message):
    __slots__ = ("gid",)
    GID_FIELD_NUMBER: _ClassVar[int]
    gid: bytes
    def __init__(self, gid: _Optional[bytes] = ...) -> None: ...

class VideoFile(_message.Message):
    __slots__ = ("file_id", "ad_placements", "sale_periods")
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    AD_PLACEMENTS_FIELD_NUMBER: _ClassVar[int]
    SALE_PERIODS_FIELD_NUMBER: _ClassVar[int]
    file_id: bytes
    ad_placements: _containers.RepeatedCompositeFieldContainer[AdPlacement]
    sale_periods: _containers.RepeatedCompositeFieldContainer[SalePeriod]
    def __init__(self, file_id: _Optional[bytes] = ..., ad_placements: _Optional[_Iterable[_Union[AdPlacement, _Mapping]]] = ..., sale_periods: _Optional[_Iterable[_Union[SalePeriod, _Mapping]]] = ...) -> None: ...

class AdPlacement(_message.Message):
    __slots__ = ("ad_type", "start_time", "finish_time")
    class AdType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PRE: _ClassVar[AdPlacement.AdType]
        MID: _ClassVar[AdPlacement.AdType]
        POST: _ClassVar[AdPlacement.AdType]
    PRE: AdPlacement.AdType
    MID: AdPlacement.AdType
    POST: AdPlacement.AdType
    AD_TYPE_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    FINISH_TIME_FIELD_NUMBER: _ClassVar[int]
    ad_type: AdPlacement.AdType
    start_time: int
    finish_time: int
    def __init__(self, ad_type: _Optional[_Union[AdPlacement.AdType, str]] = ..., start_time: _Optional[int] = ..., finish_time: _Optional[int] = ...) -> None: ...

class Block(_message.Message):
    __slots__ = ("countries", "type")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TOTAL: _ClassVar[Block.Type]
        COVERARTCP: _ClassVar[Block.Type]
    TOTAL: Block.Type
    COVERARTCP: Block.Type
    COUNTRIES_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    countries: str
    type: Block.Type
    def __init__(self, countries: _Optional[str] = ..., type: _Optional[_Union[Block.Type, str]] = ...) -> None: ...

class ContentRating(_message.Message):
    __slots__ = ("country", "tag")
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    country: str
    tag: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, country: _Optional[str] = ..., tag: _Optional[_Iterable[str]] = ...) -> None: ...

class Grant(_message.Message):
    __slots__ = ("market", "groups", "is_override_grant")
    MARKET_FIELD_NUMBER: _ClassVar[int]
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    IS_OVERRIDE_GRANT_FIELD_NUMBER: _ClassVar[int]
    market: str
    groups: _containers.RepeatedScalarFieldContainer[str]
    is_override_grant: bool
    def __init__(self, market: _Optional[str] = ..., groups: _Optional[_Iterable[str]] = ..., is_override_grant: _Optional[bool] = ...) -> None: ...

class GrantV2(_message.Message):
    __slots__ = ("markets", "group", "is_override_grant", "start", "end")
    MARKETS_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    IS_OVERRIDE_GRANT_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    markets: _containers.RepeatedScalarFieldContainer[str]
    group: str
    is_override_grant: bool
    start: Date
    end: Date
    def __init__(self, markets: _Optional[_Iterable[str]] = ..., group: _Optional[str] = ..., is_override_grant: _Optional[bool] = ..., start: _Optional[_Union[Date, _Mapping]] = ..., end: _Optional[_Union[Date, _Mapping]] = ...) -> None: ...

class Authorization(_message.Message):
    __slots__ = ("groups", "should_check_auth_groups", "grants", "grants_v2")
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    SHOULD_CHECK_AUTH_GROUPS_FIELD_NUMBER: _ClassVar[int]
    GRANTS_FIELD_NUMBER: _ClassVar[int]
    GRANTS_V2_FIELD_NUMBER: _ClassVar[int]
    groups: _containers.RepeatedScalarFieldContainer[str]
    should_check_auth_groups: bool
    grants: _containers.RepeatedCompositeFieldContainer[Grant]
    grants_v2: _containers.RepeatedCompositeFieldContainer[GrantV2]
    def __init__(self, groups: _Optional[_Iterable[str]] = ..., should_check_auth_groups: _Optional[bool] = ..., grants: _Optional[_Iterable[_Union[Grant, _Mapping]]] = ..., grants_v2: _Optional[_Iterable[_Union[GrantV2, _Mapping]]] = ...) -> None: ...

class ShowType(_message.Message):
    __slots__ = ("original", "exclusive", "adaptation")
    ORIGINAL_FIELD_NUMBER: _ClassVar[int]
    EXCLUSIVE_FIELD_NUMBER: _ClassVar[int]
    ADAPTATION_FIELD_NUMBER: _ClassVar[int]
    original: bool
    exclusive: bool
    adaptation: bool
    def __init__(self, original: _Optional[bool] = ..., exclusive: _Optional[bool] = ..., adaptation: _Optional[bool] = ...) -> None: ...

class AlbumPrerelease(_message.Message):
    __slots__ = ("earliest_reveal_date", "earliest_coverart_reveal_date")
    EARLIEST_REVEAL_DATE_FIELD_NUMBER: _ClassVar[int]
    EARLIEST_COVERART_REVEAL_DATE_FIELD_NUMBER: _ClassVar[int]
    earliest_reveal_date: Date
    earliest_coverart_reveal_date: Date
    def __init__(self, earliest_reveal_date: _Optional[_Union[Date, _Mapping]] = ..., earliest_coverart_reveal_date: _Optional[_Union[Date, _Mapping]] = ...) -> None: ...

class TrackPrerelease(_message.Message):
    __slots__ = ("earliest_reveal_date",)
    EARLIEST_REVEAL_DATE_FIELD_NUMBER: _ClassVar[int]
    earliest_reveal_date: Date
    def __init__(self, earliest_reveal_date: _Optional[_Union[Date, _Mapping]] = ...) -> None: ...

class ReleaseAdmin(_message.Message):
    __slots__ = ("release_admin_id", "personnel_description", "system_description")
    RELEASE_ADMIN_ID_FIELD_NUMBER: _ClassVar[int]
    PERSONNEL_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    release_admin_id: str
    personnel_description: str
    system_description: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, release_admin_id: _Optional[str] = ..., personnel_description: _Optional[str] = ..., system_description: _Optional[_Iterable[str]] = ...) -> None: ...

class ExtensionQuery(_message.Message):
    __slots__ = ("extension_kind", "etag")
    EXTENSION_KIND_FIELD_NUMBER: _ClassVar[int]
    ETAG_FIELD_NUMBER: _ClassVar[int]
    extension_kind: ExtensionKind
    etag: str
    def __init__(self, extension_kind: _Optional[_Union[ExtensionKind, str]] = ..., etag: _Optional[str] = ...) -> None: ...

class EntityRequest(_message.Message):
    __slots__ = ("entity_uri", "query")
    ENTITY_URI_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    entity_uri: str
    query: _containers.RepeatedCompositeFieldContainer[ExtensionQuery]
    def __init__(self, entity_uri: _Optional[str] = ..., query: _Optional[_Iterable[_Union[ExtensionQuery, _Mapping]]] = ...) -> None: ...

class BatchedEntityRequestHeader(_message.Message):
    __slots__ = ("country", "catalogue", "task_id")
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    CATALOGUE_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    country: str
    catalogue: str
    task_id: bytes
    def __init__(self, country: _Optional[str] = ..., catalogue: _Optional[str] = ..., task_id: _Optional[bytes] = ...) -> None: ...

class BatchedEntityRequest(_message.Message):
    __slots__ = ("header", "entity_request")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    ENTITY_REQUEST_FIELD_NUMBER: _ClassVar[int]
    header: BatchedEntityRequestHeader
    entity_request: _containers.RepeatedCompositeFieldContainer[EntityRequest]
    def __init__(self, header: _Optional[_Union[BatchedEntityRequestHeader, _Mapping]] = ..., entity_request: _Optional[_Iterable[_Union[EntityRequest, _Mapping]]] = ...) -> None: ...

class EntityExtensionDataArrayHeader(_message.Message):
    __slots__ = ("provider_error_status", "cache_ttl_in_seconds", "offline_ttl_in_seconds")
    PROVIDER_ERROR_STATUS_FIELD_NUMBER: _ClassVar[int]
    CACHE_TTL_IN_SECONDS_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_TTL_IN_SECONDS_FIELD_NUMBER: _ClassVar[int]
    provider_error_status: int
    cache_ttl_in_seconds: int
    offline_ttl_in_seconds: int
    def __init__(self, provider_error_status: _Optional[int] = ..., cache_ttl_in_seconds: _Optional[int] = ..., offline_ttl_in_seconds: _Optional[int] = ...) -> None: ...

class EntityExtensionDataArray(_message.Message):
    __slots__ = ("header", "extension_kind", "extension_data")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_KIND_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_DATA_FIELD_NUMBER: _ClassVar[int]
    header: EntityExtensionDataArrayHeader
    extension_kind: ExtensionKind
    extension_data: _containers.RepeatedCompositeFieldContainer[EntityExtensionData]
    def __init__(self, header: _Optional[_Union[EntityExtensionDataArrayHeader, _Mapping]] = ..., extension_kind: _Optional[_Union[ExtensionKind, str]] = ..., extension_data: _Optional[_Iterable[_Union[EntityExtensionData, _Mapping]]] = ...) -> None: ...

class BatchedExtensionResponseHeader(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BatchedExtensionResponse(_message.Message):
    __slots__ = ("header", "extended_metadata")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    EXTENDED_METADATA_FIELD_NUMBER: _ClassVar[int]
    header: BatchedExtensionResponseHeader
    extended_metadata: _containers.RepeatedCompositeFieldContainer[EntityExtensionDataArray]
    def __init__(self, header: _Optional[_Union[BatchedExtensionResponseHeader, _Mapping]] = ..., extended_metadata: _Optional[_Iterable[_Union[EntityExtensionDataArray, _Mapping]]] = ...) -> None: ...

class EntityExtensionDataHeader(_message.Message):
    __slots__ = ("status_code", "etag", "locale", "cache_ttl_in_seconds", "offline_ttl_in_seconds")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    ETAG_FIELD_NUMBER: _ClassVar[int]
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    CACHE_TTL_IN_SECONDS_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_TTL_IN_SECONDS_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    etag: str
    locale: str
    cache_ttl_in_seconds: int
    offline_ttl_in_seconds: int
    def __init__(self, status_code: _Optional[int] = ..., etag: _Optional[str] = ..., locale: _Optional[str] = ..., cache_ttl_in_seconds: _Optional[int] = ..., offline_ttl_in_seconds: _Optional[int] = ...) -> None: ...

class EntityExtensionData(_message.Message):
    __slots__ = ("header", "entity_uri", "extension_data")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    ENTITY_URI_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_DATA_FIELD_NUMBER: _ClassVar[int]
    header: EntityExtensionDataHeader
    entity_uri: str
    extension_data: _any_pb2.Any
    def __init__(self, header: _Optional[_Union[EntityExtensionDataHeader, _Mapping]] = ..., entity_uri: _Optional[str] = ..., extension_data: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
