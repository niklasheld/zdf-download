
from configuration import Configuration
from history import History

import os
import re
import feedparser
import requests
from dateutil import parser
from typing import List

configuration = Configuration()
history = History()


def should_download(entry, show_config) -> bool:
    """ checks if an episode should be downloaded """

    # check if episode was already downloaded
    if history.is_in_history(entry.get("link")):
        print(f'{entry.get("title")} is in history')
        return False

    show_filter = show_config.get("filter")
    if show_filter:

        # check episode-field against regex filter
        regex: str = show_filter.get("regex")
        regex_field: str = show_filter.get("regexField")
        if (regex and regex_field and not re.search(regex, entry.get(regex_field))):
            print(f'{entry.get("title")} does not fit regex')
            return False
        
        # check if episode before minimum date
        min_date = show_filter.get("minDate")
        if (min_date):
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
    """ check if an episode has actually been released (rss feed has future episode) """
    r = requests.get(url)
    return "verfügbar ab" not in r.text


def find_filename(show_folder, show_episode_name) -> str:
    """ generate a new filename by adding one to the current newest filename """

    episode_files: List[str] = list(filter(lambda filename: show_episode_name in filename, os.listdir(show_folder)))
    
    if not len(episode_files) == 0:
        newest_filename = os.path.splitext(episode_files[-1])[0]
        regex = re.match(r"^(.* S\d+E)(\d+)", newest_filename)
        filename_base: str = regex.group(1)
        filename_number: str = regex.group(2)

        new_episode_number = int(filename_number) + 1
        new_filename = filename_base + "{:0>2d}".format(new_episode_number)

    else:
        new_filename = show_episode_name + " S01E01"

    return new_filename


def download_episode(url: str, show_folder: str, show_episode_name: str):
    """ download episode using youtube-dl """
    filename = find_filename(show_folder, show_episode_name)
    command = "youtube-dl " + url + " -o \"" + show_folder + "/" + filename + ".%(ext)s\""
    os.system(command)
    history.add_to_history(url)


def check_for_episodes() -> None:
    """ Check all shows from configuration for new episodes """

    config: dict = configuration.load()

    for show in config["shows"]:
        feed = feedparser.parse(show["feed-url"])
        entries = feed.entries
        entries.reverse()
        for entry in entries:
            if (should_download(entry, show)):
                show_download = show.get("download")
                print(f'Downloading episode {entry.get("title")}')
                download_episode(entry.get("link"), show_download.get("folder"), show_download.get("filename"))

check_for_episodes()
