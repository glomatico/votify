# Votify
A Python CLI app for downloading songs, podcasts and videos from Spotify.

**Discord Server:** https://discord.gg/aBjMEZ9tnq

## Features
* **Songs**: Download songs up in AAC 128kbps or in AAC 256kbps with an active premium subscription.
* **Podcasts**: Download podcasts in Vorbis or AAC.
* **Videos**: Download podcast videos and music videos with an active premium subscription.
* **Synced Lyrics**: Download synced lyrics in LRC.
* **Artist Support**: Download an entire discography by providing the artist's URL.
* **Highly Customizable**: Extensive configuration options for advanced users.

## Prerequisites
* **Python 3.9 or higher** installed on your system.
* The **cookies file** of your Spotify browser session in Netscape format.
    * **Firefox**: Use the [Export Cookies](https://addons.mozilla.org/addon/export-cookies-txt) extension.
    * **Chromium-based Browsers**: Use the [Open Cookies.txt](https://chromewebstore.google.com/detail/open-cookiestxt/gdocmgbfkjnnpapoeobnolbbkoibbcif) extension.
* **FFmpeg** on your system PATH.
    * **Windows**: Download from [AnimMouse’s FFmpeg Builds](https://github.com/AnimMouse/ffmpeg-stable-autobuild/releases).
    * **Linux**: Download from [John Van Sickle’s FFmpeg Builds](https://johnvansickle.com/ffmpeg/).
* A **.wvd file**.
    * A .wvd file contains the Widevine keys from a device and is required to decrypt music videos and songs in AAC. The easiest method of obtaining one is using KeyDive, which extracts it from an Android device. Detailed instructions can be found here: https://github.com/hyugogirubato/KeyDive. **.wvd files extracted from emulated devices may not work**.

#### Notes
* The .wvd file is not required if you plan on only downloading podcasts.
* FFmpeg is not required if you plan on only downloading podcasts in Vorbis, but it's needed for downloading podcasts in AAC.

### Optional dependencies
The following tools are optional but required for specific features. Add them to your system’s PATH or specify their paths using command-line arguments or the config file.
* [MP4Box](https://gpac.io/downloads/gpac-nightly-builds/): Required when setting `mp4box` as remux mode.
* [Shaka Packager](https://github.com/shaka-project/shaka-packager/releases/latest): Required when setting `webm` as video format and when downloading music videos.
* [mp4decrypt](https://www.bento4.com/downloads/): Required when setting `mp4box` or `mp4decrypt` as remux mode.
* [aria2c](https://github.com/aria2/aria2/releases): Required when setting `aria2c` as download mode.

## Installation
1. Install the package `votify` using pip:
    ```bash
    pip install votify
    ```
2. Set up the cookies file.
    * Move the cookies file to the directory where you’ll run Votify and rename it to `cookies.txt`.
    * Alternatively, specify the path to the cookies file using command-line arguments or the config file.
3. Set up the .wvd file.
    * Move the cookies file to the directory where you’ll run Votify and rename it to `device.wvd`.
    * Alternatively, specify the path to the cookies file using command-line arguments or the config file.

## Usage
Run Votify with the following command:
```bash
votify [OPTIONS] URLS...
```

### Supported URL types
* Song
* Album
* Playlist
* Podcast episode
* Podcast series
* Music video
* Artist

### Examples
* Download a song
    ```bash
    votify "https://open.spotify.com/track/18gqCQzqYb0zvurQPlRkpo"
    ```
* Download an album
    ```bash
    votify "https://open.spotify.com/album/0r8D5N674HbTXlR3zNxeU1"
    ```
* Download a podcast episode
    ```bash
    votify "https://open.spotify.com/episode/3kwxWnzGH8T6UY2Nq582zx"
    ```
* Download a podcast series
    ```bash
    votify "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk"
* Download a music video
    ```bash
    votify "https://open.spotify.com/track/31k4hgHmrbzorLZMvMWuzq" --enable-videos
    ```
* List and select a related music video to download from a song
    ```bash
    votify "https://open.spotify.com/track/0a0n6u6j3t6m0p4k0t0k0u0" --enable-videos --download-music-videos
    ```
* Download a podcast video
    ```bash
    votify "https://open.spotify.com/episode/3kwxWnzGH8T6UY2Nq582zx" --enable-videos --download-podcast-videos
    ```
* Choose which albums to download from an artist
    ```bash
    votify "https://open.spotify.com/artist/0gxyHStUsqpMadRV0Di1Qt"
    ```

### Interactive prompt controls
* **Arrow keys**: Move selection
* **Space**: Toggle selection
* **Ctrl + A**: Select all
* **Enter**: Confirm selection

## Configuration
Votify can be configured using the command-line arguments or the config file.

The config file is created automatically when you run Votify for the first time at `~/.votify/config.json` on Linux and `%USERPROFILE%\.votify\config.json` on Windows.

Config file values can be overridden using command-line arguments.

| Command-line argument / Config file key                         | Description                                                        | Default value                                  |
| --------------------------------------------------------------- | ------------------------------------------------------------------ | ---------------------------------------------- |
| `--wait-interval`, `-w` / `wait_interval`                       | Wait interval between downloads in seconds.                        | `5`                                            |
| `--enable-videos` / `enable_videos`                             | Enable video downloads when available.                             | `false`                                        |
| `--download-music-videos` / `download_music_videos`             | List and select a related music video to download from songs.      | `false`                                        |
| `--download-podcast-videos` / `download_podcast_videos`         | Attempt to download the video version of podcasts.                 | `false`                                        |
| `--force-premium`, `-f` / `force_premium`                       | Force to detect the account as premium.                            | `false`                                        |
| `--read-urls-as-txt`, `-r` / -                                  | Interpret URLs as paths to text files containing URLs.             | `false`                                        |
| `--config-path` / -                                             | Path to config file.                                               | `<home>/.spotify-web-downloader/config.json`   |
| `--log-level` / `log_level`                                     | Log level.                                                         | `INFO`                                         |
| `--no-exceptions` / `no_exceptions`                             | Don't print exceptions.                                            | `false`                                        |
| `--cookies-path` / `cookies_path`                               | Path to cookies file.                                              | `cookies.txt`                                  |
| `--output-path`, `-o` / `output_path`                           | Path to output directory.                                          | `Spotify`                                      |
| `--temp-path` / `temp_path`                                     | Path to temporary directory.                                       | `temp`                                         |
| `--wvd-path` / `wvd_path`                                       | Path to .wvd file.                                                 | `device.wvd`                                   |
| `--aria2c-path` / `aria2c_path`                                 | Path to aria2c binary.                                             | `aria2c`                                       |
| `--ffmpeg-path` / `ffmpeg_path`                                 | Path to ffmpeg binary.                                             | `ffmpeg`                                       |
| `--mp4box-path` / `mp4box_path`                                 | Path to MP4Box binary.                                             | `mp4box`                                       |
| `--mp4decrypt-path` / `mp4decrypt_path`                         | Path to mp4decrypt binary.                                         | `mp4decrypt`                                   |
| `--packager-path` / `packager_path`                             | Path to Shaka Packager binary.                                     | `packager`                                     |
| `--template-folder-album` / `template_folder_album`             | Template folder for tracks that are part of an album.              | `{album_artist}/{album}`                       |
| `--template-folder-compilation` / `template_folder_compilation` | Template folder for tracks that are part of a compilation album.   | `Compilations/{album}`                         |
| `--template-file-single-disc` / `template_file_single_disc`     | Template file for the tracks that are part of a single-disc album. | `{track:02d} {title}`                          |
| `--template-file-multi-disc` / `template_file_multi_disc`       | Template file for the tracks that are part of a multi-disc album.  | `{disc}-{track:02d} {title}`                   |
| `--template-folder-episode` / `template_folder_episode`         | Template folder for episodes (podcasts).                           | `Podcasts/{album}`                             |
| `--template-file-episode` / `template_file_episode`             | Template file for music videos.                                    | `{track:02d} {title}`                          |
| `--template-folder-music-video` / `template_folder_music_video` | Template folder for music videos                                   | `{artist}/Unknown Album`                       |
| `--template-file-music-video` / `template_file_music_video`     | Template file for the tracks that are not part of an album.        | `{title}`                                      |
| `--template-file-playlist` / `template_file_playlist`           | Template file for the M3U8 playlist.                               | `Playlists/{playlist_artist}/{playlist_title}` |
| `--date-tag-template` / `date_tag_template`                     | Date tag template.                                                 | `%Y-%m-%dT%H:%M:%SZ`                           |
| `--cover-size` / `cover_size`                                   | Cover size.                                                        | `extra-large`                                  |
| `--save-cover` / `save_cover`                                   | Save cover as a separate file.                                     | `false`                                        |
| `--save-playlist` / `save_playlist`                             | Save a M3U8 playlist file when downloading a playlist.             | `false`                                        |
| `--overwrite` / `overwrite`                                     | Overwrite existing files.                                          | `false`                                        |
| `--exclude-tags` / `exclude_tags`                               | Comma-separated tags to exclude.                                   | `null`                                         |
| `--truncate` / `truncate`                                       | Maximum length of the file/folder names.                           | `null`                                         |
| `--audio-quality`, `-a` / `audio_quality`                       | Audio quality for songs and podcasts.                              | `vorbis-medium`                                |
| `--download-mode`, `-d` / `download_mode`                       | Download mode for songs and podcasts.                              | `ytdlp`                                        |
| `--remux-mode-audio` / `remux_mode_audio`                       | Remux mode for songs and podcasts.                                 | `ffmpeg`                                       |
| `--lrc-only`, `-l` / `lrc_only`                                 | Download only the synced lyrics.                                   | `false`                                        |
| `--no-lrc` / `no_lrc`                                           | Don't download the synced lyrics.                                  | `false`                                        |
| `--video-format` / `video_format`                               | Video format.                                                      | `mp4`                                          |
| `--remux-mode-video` / `remux_mode_video`                       | Remux mode for videos.                                             | `ffmpeg`                                       |
| `--no-config-file`, `-n` / -                                    | Do not use a config file.                                          | `false`                                        |

### Tag variables
The following variables can be used in the template folder/file and/or in the `exclude_tags` list:
- `album`
- `album_artist`
- `artist`
- `compilation`
- `composer`
- `copyright`
- `cover`
- `disc`
- `disc_total`
- `isrc`
- `label`
- `lyrics`
- `media_type`
- `playlist_artist`
- `playlist_title`
- `playlist_track`
- `publisher`
- `producer`
- `rating`
- `release_date`
- `release_year`
- `title`
- `track`
- `track_total`
- `url`
  
### Cover sizes
* `small`: up to 64px
* `medium`: up to 300px
* `large`: up to 640px
* `extra-large`: up to 2000px

### Audio qualities
* General codecs:
    * `aac-medium`: 128kbps
    * `aac-high` 256kbps, requires an active premium subscription
* Podcast only codecs:
    * `vorbis-high`: 320kbps, requires an active premium subscription
    * `vorbis-medium`: 160kbps
    * `vorbis-low`: 96kbps

### Video formats
* `mp4`: H.264 Up to 1080p with AAC 128kbps.
* `webm`: VP9 Up to 1080p with Opus 160kbps.
* `ask`: Prompt to choose available video and audio codecs.

### Download modes
* `ytdlp`: Default download mode.
* `aria2c`: Faster alternative to `ytdlp` only applicable to songs and podcasts.

### Video remux modes
* `ffmpeg`
* `mp4box`

### Audio remux modes
* `ffmpeg`
* `mp4box`
* `mp4decrypt`

### Credits
* [spotify-oggmp4-dl](https://github.com/DevLARLEY/spotify-oggmp4-dl)
* [spsync](https://github.com/baltitenger/spsync)
* [unplayplay](https://git.gay/uhwot/unplayplay)
