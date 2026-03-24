# Votify

[![PyPI version](https://img.shields.io/pypi/v/votify?color=blue)](https://pypi.org/project/votify/)
[![Python versions](https://img.shields.io/pypi/pyversions/votify)](https://pypi.org/project/votify/)
[![License](https://img.shields.io/github/license/glomatico/votify)](https://github.com/glomatico/votify/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/votify)](https://pypi.org/project/votify/)

A command-line app for downloading songs, podcasts and videos from Spotify.

**Join our Discord Server:** <https://discord.gg/aBjMEZ9tnq>

## ✨ Features

- 🎵 **Songs** - Download songs.
- 🎙️ **Podcasts** - Download podcasts.
- 🎬 **Videos** - Download podcast videos and music videos.
- 🎤 **Synced Lyrics** - Download synced lyrics in LRC format.
- 🧑‍🎤 **Artist Support** - Download an entire discography by providing the artist's URL.
- ⚙️ **Highly Customizable** - Extensive configuration options for advanced users.

## 📋 Prerequisites

### Required

- **Python 3.10 or higher**
- **Spotify cookies** - Export your browser cookies in Netscape format while logged in at the Spotify homepage:
  - Firefox: [Export Cookies](https://addons.mozilla.org/addon/export-cookies-txt)
  - Chromium-based browsers: [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)

> [!WARNING]
> - **Some users have reported that Spotify suspended their accounts after using Votify.** Use it at your own risk.
> - **You may not be able to download songs if your account is too new.** In this case, you can try downloading songs in AAC quality with a .wvd file, which uses a different download method that may work for new accounts.

### External Tools

Add these tools to your system PATH or specify their paths via command-line arguments or the config file. Then configure the appropriate option for your use case:

**Download songs and podcasts in Vorbis quality**:
- Votify uses default settings without requiring any optional tools

**Download songs and podcasts in AAC quality (128kbps / 256kbps)**:
- **.wvd file** (for songs only)
- **FFmpeg**, **mp4decrypt**, or **MP4Box** + **mp4decrypt**

**Download songs in FLAC quality**:
- L1-certified **.wvd file**
- **FFmpeg**

**Download music videos**:
- **.wvd file**
- **FFmpeg** or **MP4Box**
- **mp4decrypt** (for MP4) or **Shaka Packager** (for WebM)

**Download podcast videos**:
- **FFmpeg** or **MP4Box**

**Download with faster speeds**:
- **aria2c** or **cURL**

### Tools Reference

- **.wvd file** - Extract using [KeyDive](https://github.com/hyugogirubato/KeyDive) from an Android device. Extracted files from emulated devices may not work.
- **FFmpeg** - Download for Windows: [AnimMouse's FFmpeg Builds](https://github.com/AnimMouse/ffmpeg-stable-autobuild/releases), Linux: [John Van Sickle's FFmpeg Builds](https://johnvansickle.com/ffmpeg/)
- **MP4Box** - [Download](https://gpac.io/downloads/gpac-nightly-builds/)
- **mp4decrypt** - [Download](https://www.bento4.com/downloads/)
- **Shaka Packager** - [Download](https://github.com/shaka-project/shaka-packager/releases/latest)
- **cURL** - [Download](https://curl.se/download.html)
- **aria2c** - [Download](https://github.com/aria2/ari2/releases)

## 📦 Installation

1. Install Votify via pip:
   ```bash
   pip install votify[librespot]
   ```

2. Set up the cookies file:
   - Place the cookies file in your working directory as `cookies.txt`, or
   - Specify its path using `--cookies-path` or in the config file.

> [!NOTE]
> - **The 'librespot' extra is only required if you want to download in Vorbis quality.** If you only want to download in AAC quality, you can just install the main `votify` package without the extra.

## 🚀 Usage

```bash
votify [OPTIONS] URLS...
```

### Supported URL types

- Song
- Album
- Playlist
- Podcast episode
- Podcast series
- Music video
- Artist

### Examples

Download a song:
```bash
votify "https://open.spotify.com/track/18gqCQzqYb0zvurQPlRkpo"
```

Download an album:
```bash
votify "https://open.spotify.com/album/0r8D5N674HbTXlR3zNxeU1"
```

Download a podcast episode:
```bash
votify "https://open.spotify.com/episode/3kwxWnzGH8T6UY2Nq582zx"
```

Download a podcast series:
```bash
votify "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk"
```

Download a music video:
```bash
votify "https://open.spotify.com/track/31k4hgHmrbzorLZMvMWuzq"
```

Download a music video from a song:
```bash
votify "https://open.spotify.com/track/18gqCQzqYb0zvurQPlRkpo" --prefer-video
```

Download a podcast video:
```bash
votify "https://open.spotify.com/episode/3kwxWnzGH8T6UY2Nq582zx" --prefer-video
```

Choose which media to download from an artist:
```bash
votify "https://open.spotify.com/artist/0gxyHStUsqpMadRV0Di1Qt"
```

Auto-select artist albums without a prompt:
```bash
votify "https://open.spotify.com/artist/0gxyHStUsqpMadRV0Di1Qt" --auto-media-option albums
```

Download liked tracks:
```bash
votify --auto-media-option liked-tracks
```

### Interactive prompt controls

| Key | Action |
| --- | ------ |
| Arrow keys | Move selection |
| Space | Toggle selection |
| Ctrl + A | Select all |
| Enter | Confirm selection |

## ⚙️ Configuration

Votify can be configured using command-line arguments or the config file.

Config file location:
- Linux: `~/.votify/config.ini`
- Windows: `%USERPROFILE%\.votify\config.ini`

The file is created automatically on first run. Command-line arguments override config file values.

### Configuration options

| Command-line argument / Config file key | Description | Default |
| --------------------------------------- | ----------- | ------- |
| **General** | | |
| `--wait-interval` / `wait_interval` | Wait interval between downloads in seconds | `10` |
| `--read-urls-as-txt`, `-r` / - | Read URLs from text files | `false` |
| `--config-path` / - | Config file path | `<home>/.votify/config.ini` |
| `--log-level` / `log_level` | Logging level | `INFO` |
| `--log-file` / `log_file` | Log file path | `null` |
| `--no-exceptions` / `no_exceptions` | Don't print exceptions | `false` |
| `--no-config-file`, `-n` / - | Don't use a config file | `false` |
| `--database-path` / `database_path` | Path to the SQLite database file for registering downloaded media | `null` |
| `--auto-media-option` / `auto_media_option` | Auto media option | `null` |
| **Spotify** | | |
| `--cookies-path`, `-c` / `cookies_path` | Cookies file path | `./cookies.txt` |
| `--wvd-path` / `wvd_path` | .wvd file path | `null` |
| `--prefer-video` / `prefer_video` | Prefer video streams when available | `false` |
| **Output** | | |
| `--output`, `-o` / `output` | Output directory path | `./Spotify` |
| `--temp` / `temp` | Temporary directory path | `.` |
| `--save-cover-file` / `save_cover_file` | Save cover as a separate file | `false` |
| `--save-playlist-file` / `save_playlist_file` | Save a M3U8 playlist file when downloading a playlist | `false` |
| `--overwrite` / `overwrite` | Overwrite existing files | `false` |
| `--cover-size` / `cover_size` | Cover size to use | `extra-large` |
| `--exclude-tags` / `exclude_tags` | Comma-separated tags to exclude | `null` |
| `--truncate` / `truncate` | Maximum length of file/folder names | `null` |
| **Template** | | |
| `--album-folder-template` / `album_folder_template` | Folder template for album tracks | `{album_artist}/{album}` |
| `--compilation-folder-template` / `compilation_folder_template` | Folder template for compilation tracks | `Compilations/{album}` |
| `--podcast-folder-template` / `podcast_folder_template` | Folder template for podcast episodes | `Podcasts/{album}` |
| `--no-album-folder-template` / `no_album_folder_template` | Folder template for tracks not in an album | `{artist}/Unknown Album` |
| `--single-disc-file-template` / `single_disc_file_template` | File template for single-disc album tracks | `{track:02d} {title}` |
| `--multi-disc-file-template` / `multi_disc_file_template` | File template for multi-disc album tracks | `{disc}-{track:02d} {title}` |
| `--podcast-file-template` / `podcast_file_template` | File template for podcast episodes | `{track:02d} {title}` |
| `--no-album-file-template` / `no_album_file_template` | File template for tracks not in an album | `{title}` |
| `--playlist-file-template` / `playlist_file_template` | File template for M3U8 playlists | `Playlists/{playlist_artist}/{playlist_title}` |
| `--date-tag-template` / `date_tag_template` | Date tag template | `%Y-%m-%dT%H:%M:%SZ` |
| **Song / Podcast** | | |
| `--audio-quality` / `audio_quality` | Comma-separated audio quality priority | `vorbis-medium` |
| `--audio-download-mode` / `audio_download_mode` | Audio download mode to use | `ytdlp` |
| `--audio-remux-mode` / `audio_remux_mode` | Audio remux mode to use | `ffmpeg` |
| `--synced-lyrics-only` / `synced_lyrics_only` | Only download synced lyrics file | `false` |
| `--no-synced-lyrics-file` / `no_synced_lyrics_file` | Don't create synced lyrics file | `false` |
| **Video** | | |
| `--video-format` / `video_format` | Video format to use | `mp4` |
| `--video-resolution` / `video_resolution` | Video resolution to use | `1080p` |
| `--video-remux-mode` / `video_remux_mode` | Video remux mode to use | `ffmpeg` |
| **Executables** | | |
| `--aria2c-path` / `aria2c_path` | Path to aria2c binary | `aria2c` |
| `--curl-path` / `curl_path` | Path to curl binary | `curl` |
| `--ffmpeg-path` / `ffmpeg_path` | Path to FFmpeg binary | `ffmpeg` |
| `--mp4box-path` / `mp4box_path` | Path to MP4Box binary | `mp4box` |
| `--mp4decrypt-path` / `mp4decrypt_path` | Path to mp4decrypt binary | `mp4decrypt` |
| `--shaka-packager-path` / `shaka_packager_path` | Path to Shaka Packager binary | `packager` |

### Template variables

Tags usable in template folder/file options and in the `exclude_tags` list:

- `album`, `album_artist`
- `artist`
- `composer`
- `date` (supports strftime format: `{date:%Y}`)
- `disc`, `disc_total`
- `isrc`
- `label`
- `media_id`
- `media_type`
- `playlist_id`, `playlist_artist`, `playlist_title`, `playlist_track`
- `producer`, `publisher`
- `rating`
- `title`, `track`, `track_total`

Tags usable in the `exclude_tags` list only:

- `compilation`, `copyright`, `cover`
- `description`
- `lyrics`
- `url`

### Cover sizes

- `small` - Up to 64px
- `medium` - Up to 300px
- `large` - Up to 640px
- `extra-large` - Up to 2000px

### Audio qualities

- `vorbis-low` - Vorbis 96kbps
- `vorbis-medium` - Vorbis 160kbps, songs only
- `vorbis-high` - Vorbis 320kbps, songs only, requires an active premium subscription
- `aac-medium` - AAC 128kbps, .wvd file required for songs
- `aac-high` - AAC 256kbps, songs only, .wvd required, requires an active premium subscription
- `flac` - FLAC lossless, songs only, .wvd required, requires an active premium subscription

> [!NOTE]
> - **FLAC quality requires a L1 .wvd file.**

### Video formats

- `mp4` - H.264 up to 1080p with AAC 128kbps
- `webm` - VP9 up to 1080p with Opus 160kbps
- `ask` - Prompt to choose available video and audio codecs

### Download modes

- `ytdlp` - Default download mode
- `aria2c` - Faster alternative
- `curl` - Alternative using curl

> [!NOTE]
> - **yt-dlp is only used as a file download library**. Tracks are still fetched directly from Spotify's servers, and yt-dlp is only responsible for handling the file download process.

### Video remux modes

- `ffmpeg`
- `mp4box`

### Audio remux modes

- `ffmpeg`
- `mp4box`
- `mp4decrypt`

> [!NOTE]
> Audio remux modes only apply for non vorbis qualities.

### Video resolutions

- `144p`, `240p`, `360p`, `480p`, `576p`, `720p`, `1080p`

### Auto media options

- `artist-albums` - Auto-select albums
- `artist-compilations` - Auto-select compilations
- `artist-singles` - Auto-select singles
- `artist-videos` - Auto-select music videos
- `liked-tracks` - Auto-select liked tracks (URL not required)

### Log levels

- `DEBUG`, `INFO`, `WARNING`, `ERROR`

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

I'm generally not reviewing pull requests that change or add features at this time. Only critical bug fixes will be considered. Feel free to open issues for bugs or feature requests.

## 🙏 Credits

- [spotify-oggmp4-dl](https://github.com/DevLARLEY/spotify-oggmp4-dl)
- [spsync](https://github.com/baltitenger/spsync)
- [unplayplay](https://git.gay/uhwot/unplayplay)
