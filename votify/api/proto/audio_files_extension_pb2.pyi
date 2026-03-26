from votify.api.proto import extendedmetadata_pb2 as _extendedmetadata_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NormalizationParams(_message.Message):
    __slots__ = ("loudness_db", "true_peak_db")
    LOUDNESS_DB_FIELD_NUMBER: _ClassVar[int]
    TRUE_PEAK_DB_FIELD_NUMBER: _ClassVar[int]
    loudness_db: float
    true_peak_db: float
    def __init__(self, loudness_db: _Optional[float] = ..., true_peak_db: _Optional[float] = ...) -> None: ...

class ExtendedAudioFile(_message.Message):
    __slots__ = ("file", "average_bitrate")
    FILE_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_BITRATE_FIELD_NUMBER: _ClassVar[int]
    file: _extendedmetadata_pb2.AudioFile
    average_bitrate: int
    def __init__(self, file: _Optional[_Union[_extendedmetadata_pb2.AudioFile, _Mapping]] = ..., average_bitrate: _Optional[int] = ...) -> None: ...

class AudioFilesExtensionResponse(_message.Message):
    __slots__ = ("files", "default_file_normalization_params", "default_album_normalization_params", "audio_id")
    FILES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_FILE_NORMALIZATION_PARAMS_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_ALBUM_NORMALIZATION_PARAMS_FIELD_NUMBER: _ClassVar[int]
    AUDIO_ID_FIELD_NUMBER: _ClassVar[int]
    files: _containers.RepeatedCompositeFieldContainer[ExtendedAudioFile]
    default_file_normalization_params: NormalizationParams
    default_album_normalization_params: NormalizationParams
    audio_id: bytes
    def __init__(self, files: _Optional[_Iterable[_Union[ExtendedAudioFile, _Mapping]]] = ..., default_file_normalization_params: _Optional[_Union[NormalizationParams, _Mapping]] = ..., default_album_normalization_params: _Optional[_Union[NormalizationParams, _Mapping]] = ..., audio_id: _Optional[bytes] = ...) -> None: ...
