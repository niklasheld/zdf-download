
<h1 style="text-alignment: center">ZDF-Download</h1>

[![Build Container](https://github.com/niklasheld/zdf-download/actions/workflows/build-container.yaml/badge.svg)](https://github.com/niklasheld/zdf-download/actions/workflows/build-container.yaml)

Script to automatically download new episodes of TV shows from the ZDF Mediathek. The script is meant to quickly download *new* episodes, not all available episodes.

## How to add new shows

Add RSS-feeds for the show you want to download to the configuration script. You can find a direct URL to the field in the source-code of the mediathek-page. An example for *ZDF Magazin Royale* is [https://www.zdf.de/rss/zdf/comedy/zdf-magazin-royale](https://www.zdf.de/rss/zdf/comedy/zdf-magazin-royale)  

As an option, you can also define regex-filters on fields from the rss-feed to filter out episodes you don't want, i.e. specials or short online-clips. `configuration-example.yaml` has an example for a filter to only download full ZDF Magazin Royale episodes.

## Application logic

- Script assumes that all files in the target folder are named `Showname SxxExx` naming-scheme and no files violate this scheme
- When a new episode is found, a sequential filename is generated for the new download. If you want the file to be downloaded in a new season, you have to rename it manually. The next file will then be sequentially added to this season.
- After a file is downloaded, it's URL is added to a history-file and it will not be downloaded again.


## How to start

Before starting the script, add a custom `configuration.yaml`-file to your directory. You can find an example configuration in the configuration-folder

### Docker

The recommended way to use this program is to start a lightweight Docker-container and mount your media-folders and configuration.

#### Build yourself

You can start a docker-build using the following command:

``docker build -t zdf-download .``

Afterwards, you can deploy the built container using this command:

``docker run -d --name=zdf-download -v <host-media-folder>:<docker-media-folder> -v <host-configuration-folder>:/app/configuration zdf-download:latest``

#### Use the latest pre-built image

You can also use the pre-build container and deploy directly from the GitHub container-registry:

``docker run -d --name=zdf-download -v <host-media-folder>:<docker-media-folder> -v <host-configuration-folder>:/app/configuration ghcr.io/niklasheld/zdf-download:latest``

### Without docker

Install the packages from `requirements.txt`, preferably in a python virtual environment. Make sure that `youtube-dl` and `ffmpeg` are installed and available. Start the application using `python zdf-download.py`.