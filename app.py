"""Main script for the ZDF Downloader."""
import os
import re
from typing import List
import feedparser
import requests
from dateutil import parser

from configuration import Configuration, ShowConfiguration, DownloadConfiguration, load_configuration_from_yaml
from history import History





def should_download(entry, show_config: ShowConfiguration) -> bool:
    """Check if an episode should be downloaded."""
    # check if episode was already downloaded
    if history.is_in_history(entry.get("link")):
        print(f'{entry.get("title")} is in history')
        return False

    show_filter = show_config.filter
    if show_filter:

        # check episode-field against regex filter
        regex: str = show_filter.regex
        regex_field: str = show_filter.regex_field
        if (regex and regex_field and not re.search(regex, entry.get(regex_field))):
            print(f'{entry.get("title")} does not fit regex')
            return False

        # check if episode before minimum date
        min_date = show_filter.min_date
        if min_date:
            min_date = parser.parse(min_date)
            entry_date = parser.parse(entry.get("published"))
            if entry_date < min_date:
                print(f'{entry.get("title")} is before mindate')
                return False

        if not is_episode_released(entry.get("link")):
            print(f'{entry.get("title")} is not yet released')
            return False

    return True


def is_episode_released(url: str) -> bool:
    """Check if an episode has actually been released (rss feed has future episode)."""
    result = requests.get(url)
    return "verfügbar ab" not in result.text


def find_filename(download: DownloadConfiguration) -> str:
    """Generate a new filename by adding one to the current newest filename."""
    episode_files: List[str] = list(filter(lambda filename: download.filename in filename, os.listdir(download.folder)))

    if not len(episode_files) == 0:
        newest_filename = os.path.splitext(episode_files[-1])[0]
        regex = re.match(r"^(.* S\d+E)(\d+)", newest_filename)
        filename_base: str = regex.group(1)
        filename_number: str = regex.group(2)

        new_episode_number = int(filename_number) + 1
        new_filename = filename_base + "{:0>2d}".format(new_episode_number)

    else:
        new_filename = download.filename + " S01E01"

    return new_filename


def download_episode(url: str, download: DownloadConfiguration):
    """Download episode using youtube-dl."""
    filename = find_filename(download)
    command = "youtube-dl " + url + " -o \"" + download.folder + "/" + filename + ".%(ext)s\""
    os.system(command)
    history.add_to_history(url)


def check_show(show: ShowConfiguration) -> None:
    """Check all episodes of a show for new downloads."""
    feed = feedparser.parse(show.feed_url)
    entries = feed.entries
    entries.reverse()
    for entry in entries:
        if should_download(entry, show):
            print(f'Downloading episode {entry.get("title")}')
            download_episode(entry.get("link"), show.download)


def check_all_shows(shows: List[ShowConfiguration]) -> None:
    """Check all shows in configuration for new downloads."""
    for show in shows:
        check_show(show)


history = History("history.yaml")
config: Configuration = load_configuration_from_yaml("configuration.yaml")
check_all_shows(config.shows)
