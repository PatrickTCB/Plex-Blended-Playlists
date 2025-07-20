# Plex Blend Playlist Creator

This Python script creates a blended playlist from multiple Plex users, combining songs from their individual playlists into a single, shared playlist.

## Overview

The script takes configuration from a TOML file and the blend configurations from a JSON file. Then it retrieves playlists from each user's Plex server, randomly selects songs, and creates a new blended playlist on each user's server.  It also includes a mechanism to ignore specific songs.

There's no limit to the number of users you can use to create any given blend, nor is there a limit to how many different blended playlists you can create. I create one that blends all the users in the family, as well as one for each family member by themselves. That's demoed here with just two users because that's more legible. But it you can do 5, 10, whatever you want. 

Personally, I use the ignore setting to ignore my the white noise songs my kids use for sleeping.

## Prerequisites

*   **Python 3.7+:**  This script requires Python 3.7 or later.
*   **Plex Media Server:** You need access to Plex Media Servers for each user. It has to be the same server, but does not have to be accessed via the same URL. This is because the track ids are not the same across Plex servers
*   **Plex API Token:**  Plex Tokens [are retrieved in the browser](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).
*   **Dependencies:** The following Python packages are required:
    *   `tomllib` (built-in with Python 3.11+, for older versions install with `pip install tomllib`)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone git@github.com:PatrickTCB/Plex-Blended-Playlists.git
    cd plex-blended-playlists
    ```

2.  **Install dependencies:**
    ```bash
    pip install tomllib  # If using Python < 3.11
    ```

3.  **Create `conf.toml`:**  Configure the script with your desired settings.  See the "Configuration" section below for details.

4.  **Create `blends.json`:**  Define the users and their Plex server details.  See the "User Configuration" section below for details.

## Configuration

The `conf.toml` file controls the script's overall behavior. It's easiest to just clone `conf-example.toml` and update the variables you need to change.

```toml
# conf.toml
numberOfSongs = 100  # The desired number of songs in the blended playlist
songSearchTimeLimit = 180 # Time in seconds to search for songs before stopping.
```

## Blend Configuration

The `blends.json` file defines the users and their Plex server details. As with the `conf.toml` setup it's easiest to just clone `blends-example.json` and update the variables. 

The file consists of a list of blends. Each blend has two elements: `name` and `users`. Where `name` is just the name you want to use for the resulting playlist and `users` is an object like this:

* **name**: The name of the user who is a part of this blend
* **host**: The Plex server's hostname.
* **token**: Plex Tokens [are retrieved in the browser](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).
* **musicLibrary**: All users need the same library and your server may have any number of audo libraries. Navigate to [app.plex.tv](https://app.plex.tv) or whatever your plex URL is. Then select the library you want to use for this script. That should send you too a URL like this: `https://app.plex.tv/desktop/#!/media/$serverID/com.plexapp.plugins.library?source=1`. It's the value of `source` that we're interested in here, so that would mean our config should have: `musicLibrary=1`.

## Usage

Run the script from the command line:

```bash
python main.py
```

**Optional Arguments:**

*   `-v`: Enable verbose output.
*   `-conf <config_file>`: Specify a custom configuration file (defaults to `conf.toml`).
*   `-blends <blends_file>`: Specify a custom blends configuration file (defaults to `blends.json`).

Example:

```bash
python main.py -v -conf my_config.toml -blends my_blends.json
```

## Files

*   `main.py`: The main script.
*   `conf.toml`: Configuration file (see "Configuration" section).
*   `blends.json`: Blends configuration file (see "Blend Configuration" section).
*   `lib/plex.py`:  A library file containing functions for interacting with the Plex API.
*   `lib/common.py`: A library file containing common utility functions.
*   `ignoredSongs.json`: (Optional) A JSON file containing a list of songs to ignore (title, artist, album). See `ignoredSongs-example.json` for easy examples.

**Note**: While the script itself deals with songs via their id or `ratingKey` from Plex, the ignored songs are specified in a more human friendly way. This saves you from having to look up the id of any particular song and allows the ignore to still work in cases where an album is removed from and then added back into your library later.

## Troubleshooting

*   **API Token:** Ensure your Plex API token is valid and has the necessary permissions.
*   **Network Connectivity:** Verify that the script can connect to the Plex servers.
*   **Configuration Files:** Double-check the `conf.toml` and `users.toml` files for errors.
*   **Dependencies:** Make sure all required Python packages are installed.

## License

[MIT License](LICENSE)