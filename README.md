# Votify
A Python CLI app for downloading songs/podcasts from Spotify in Vorbis (OGG).

**Discord Server:** https://discord.gg/aBjMEZ9tnq

## Features
* Download songs and podcasts in Vorbis 96/128kbps or in 320kbps with a premium account
* Support for artist links to download all of their albums
* Download synced lyrics
* Highly configurable

## Prerequisites
* Python 3.8 or higher
* The cookies file of your Spotify browser session in Netscape format (free or premium)
    * You can get your cookies by using one of the following extensions on your browser of choice at the Spotify website with your account signed in:
        * Firefox: https://addons.mozilla.org/addon/export-cookies-txt
        * Chromium based browsers: https://chrome.google.com/webstore/detail/gdocmgbfkjnnpapoeobnolbbkoibbcif
* Unplayplay
    * Build it from source: https://git.gay/glomatico/unplayplay.

## Installation
1. Install the package `votify` using pip
    ```bash
    pip install votify
    ```
2. Set up the `cookies.txt`.
    * You can either move to the current directory from which you will be running Votify or specify its path using the command line arguments/config file.
3. Set up Unplayplay
    * You can either add it to your PATH or specify its path using the command line arguments/config file.

## Usage
```bash
votify [OPTIONS] URLS...
```

### Examples
* Download a song
    ```bash
    votify "https://open.spotify.com/track/18gqCQzqYb0zvurQPlRkpo"
    ```
* Download an album
    ```bash
    votify "https://open.spotify.com/album/0r8D5N674HbTXlR3zNxeU1"
    ```
* Choose which albums to download from an artist
    ```bash
    votify "https://open.spotify.com/artist/0gxyHStUsqpMadRV0Di1Qt"
    ```

### Interactive prompt controls
* Arrow keys - Move selection
* Space - Toggle selection
* Ctrl + A - Select all
* Enter - Confirm selection

## Configuration
Votify can be configured using the command line arguments or the config file.

The config file is created automatically when you run Votify for the first time at `~/.votify/config.json` on Linux and `%USERPROFILE%\.votify\config.json` on Windows.

Config file values can be overridden using command line arguments.

| Command line argument / Config file key                         | Description                                                        | Default value                                  |
| --------------------------------------------------------------- | ------------------------------------------------------------------ | ---------------------------------------------- |
| `--wait-interval`, `-w` / `wait_interval`                       | Wait interval between downloads in seconds.                        | `10`                                           |
| `--force-premium`, `-f` / `force_premium`                       | Force to detect the account as premium.                            | `false`                                        |
| `--read-urls-as-txt`, `-r` / -                                  | Interpret URLs as paths to text files containing URLs.             | `false`                                        |
| `--config-path` / -                                             | Path to config file.                                               | `<home>/.votify/config.json`                   |
| `--log-level` / `log_level`                                     | Log level.                                                         | `INFO`                                         |
| `--print-exceptions` / `print_exceptions`                       | Print exceptions.                                                  | `false`                                        |
| `--cookies-path` / `cookies_path`                               | Path to cookies file.                                              | `./cookies.txt`                                |
| `--quality`, `-q` / `quality`                                   | Audio quality.                                                     | `medium`                                       |
| `--output-path`, `-o` / `output_path`                           | Path to output directory.                                          | `./Spotify`                                    |
| `--temp-path` / `temp_path`                                     | Path to temporary directory.                                       | `./temp`                                       |
| `--download-mode`, `-d` / `download_mode`                       | Download mode.                                                     | `ytdlp`                                        |
| `--aria2c-path` / `aria2c_path`                                 | Path to aria2c binary.                                             | `aria2c`                                       |
| `--unplayplay-path` / `unplayplay_path`                         | Path to unplayplay binary.                                         | `unplayplay`                                   |
| `--template-folder-album` / `template_folder_album`             | Template folder for tracks that are part of an album.              | `{album_artist}/{album}`                       |
| `--template-folder-compilation` / `template_folder_compilation` | Template folder for tracks that are part of a compilation album.   | `Compilations/{album}`                         |
| `--template-file-single-disc` / `template_file_single_disc`     | Template file for the tracks that are part of a single-disc album. | `{track:02d} {title}`                          |
| `--template-file-multi-disc` / `template_file_multi_disc`       | Template file for the tracks that are part of a multi-disc album.  | `{disc}-{track:02d} {title}`                   |
| `--template-folder-episode` / `template_folder_episode`         | Template folder for episodes (podcasts).                           | `Podcasts/{album}`                             |
| `--template-file-episode` / `template_file_episode`             | Template file for episodes (podcasts).                             | `{track:02d} {title}`                          |
| `--template-file-playlist` / `template_file_playlist`           | Template file for the M3U8 playlist.                               | `Playlists/{playlist_artist}/{playlist_title}` |
| `--date-tag-template` / `date_tag_template`                     | Date tag template.                                                 | `%Y-%m-%dT%H:%M:%SZ`                           |
| `--save-cover`, `-s` / `save_cover`                             | Save cover as a separate file.                                     | `false`                                        |
| `--save-playlist` / `save_playlist`                             | Save a M3U8 playlist file when downloading a playlist.             | `false`                                        |
| `--overwrite` / `overwrite`                                     | Overwrite existing files.                                          | `false`                                        |
| `--exclude-tags` / `exclude_tags`                               | Comma-separated tags to exclude.                                   | `null`                                         |
| `--truncate` / `truncate`                                       | Maximum length of the file/folder names.                           | `null`                                         |
| `--lrc-only`, `-l` / `lrc_only`                                 | Download only the synced lyrics.                                   | `false`                                        |
| `--no-lrc` / `no_lrc`                                           | Don't download the synced lyrics.                                  | `false`                                        |
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
- `playlist_artist`
- `playlist_title`
- `playlist_track`
- `producer`
- `rating`
- `release_date`
- `release_year`
- `title`
- `track`
- `track_total`
- `url`
  
### Download qualities
The following qualities are available:
* `high` (320kbps, requires premium account)
* `medium` (160kbps)
* `low` (96kbps)

### Download modes
The following modes are available:
* `ytdlp`
* `aria2c`
    * Faster than `ytdlp`
    * Can be obtained from here: https://github.com/aria2/aria2/releases


## Credits
* [spotify-oggmp4-dl](https://github.com/DevLARLEY/spotify-oggmp4-dl)
* [spsync](https://github.com/baltitenger/spsync)
* [unplayplay](https://git.gay/uhwot/unplayplay)