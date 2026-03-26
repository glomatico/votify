from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Interactivity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_INTERACTIVITY: _ClassVar[Interactivity]
    INTERACTIVE: _ClassVar[Interactivity]
    DOWNLOAD: _ClassVar[Interactivity]

class ContentType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_CONTENT_TYPE: _ClassVar[ContentType]
    AUDIO_TRACK: _ClassVar[ContentType]
    AUDIO_EPISODE: _ClassVar[ContentType]
    AUDIO_ADD: _ClassVar[ContentType]
UNKNOWN_INTERACTIVITY: Interactivity
INTERACTIVE: Interactivity
DOWNLOAD: Interactivity
UNKNOWN_CONTENT_TYPE: ContentType
AUDIO_TRACK: ContentType
AUDIO_EPISODE: ContentType
AUDIO_ADD: ContentType

class PlayPlayLicenseRequest(_message.Message):
    __slots__ = ("version", "token", "cache_id", "interactivity", "content_type", "timestamp")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    CACHE_ID_FIELD_NUMBER: _ClassVar[int]
    INTERACTIVITY_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    version: int
    token: bytes
    cache_id: bytes
    interactivity: Interactivity
    content_type: ContentType
    timestamp: int
    def __init__(self, version: _Optional[int] = ..., token: _Optional[bytes] = ..., cache_id: _Optional[bytes] = ..., interactivity: _Optional[_Union[Interactivity, str]] = ..., content_type: _Optional[_Union[ContentType, str]] = ..., timestamp: _Optional[int] = ...) -> None: ...

class PlayPlayLicenseResponse(_message.Message):
    __slots__ = ("obfuscated_key",)
    OBFUSCATED_KEY_FIELD_NUMBER: _ClassVar[int]
    obfuscated_key: bytes
    def __init__(self, obfuscated_key: _Optional[bytes] = ...) -> None: ...
