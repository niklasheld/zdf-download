
<h1 style="text-alignment: center">ZDF-Download</h1>

[![Build Container](https://github.com/niklasheld/zdf-download/actions/workflows/build-container.yaml/badge.svg)](https://github.com/niklasheld/zdf-download/actions/workflows/build-container.yaml)
[![Build Container](https://github.com/niklasheld/zdf-download/actions/workflows/quality.yaml/badge.svg)](https://github.com/niklasheld/zdf-download/actions/workflows/quality.yaml)
[![semantic-release: angular](https://img.shields.io/badge/semantic--release-angular-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)
[![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=zdf-download)](https://sonarcloud.io/summary/new_code?id=zdf-download)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=zdf-download&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=zdf-download)
[![Known Vulnerabilities](https://snyk.io/test/github/niklasheld/zdf-download/badge.svg)](https://snyk.io/test/github/niklasheld/zdf-download)

Script to automatically download new episodes of TV shows from the ZDF Mediathek. The script is meant to quickly download *new* episodes, not all available episodes.

## How to add new shows

The downloader needs the "canonical url" of a given show within the ZDF Mediathek. An example for *ZDF Magazin Royale* (https://www.zdf.de/shows/zdf-magazin-royale-102) would be `zdf-magazin-royale-102`


## Application logic

- Script assumes that all files in the target folder are named `<Showname> SxxExx` naming-scheme and no files violate this scheme. It also asumes that you are using a flat filestructure for all seasons.
- When a new episode is found, a sequential filename is generated for the new download. If you want the file to be downloaded in a new season, you have to rename it manually. The next file will then be sequentially added to this season.
- After a file is downloaded, its URL is added to a history-file and it will not be downloaded again.


## How to start

Before starting the script, add a custom `configuration.yaml`-file to your directory. You can find an example configuration in the configuration-folder

### Full Configuration

See `configuration-example.yaml` for an example configuration. The configuration file has to be placed at `/app/configuration/configuration.yaml`.

| Paramter | Description | Example |
| --- | --- | --- |
| interval | Minutes between each scan for new episodes | `60` |
| shows[].canonical-id | Canonical ID of the show to download | `"zdf-magazin-royale-102"` |
| shows[].filter.minDate | Minimum date of episode to download | `"2021-09-01 00:00+00:00"` |
| shows[].download.folder | Path to the folder where the downloaded files are located for this show | `"/serien/ZDF Magazin Royale"` |
| shows[].download.filename | Base filename that is used to consecutively name episodes. | `"ZDF Magazin Royale"` |

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

Install the packages from `requirements.txt`, preferably in a python virtual environment. Make sure that `yt-dlp` and `ffmpeg` are installed and available. Start the application using `python app.py`.