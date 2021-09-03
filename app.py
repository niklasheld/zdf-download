"""Main script for the ZDF Downloader."""
import os
import sys
import re
from typing import List
import time
import logging
import feedparser
import requests
from dateutil import parser
import schedule

from configuration import Configuration, ShowConfiguration, DownloadConfiguration, load_configuration_from_yaml
from history import History

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

def should_download(entry, show_config: ShowConfiguration) -> bool:
    """Check if an episode should be downloaded."""
    # check if episode was already downloaded
    if history.is_in_history(entry.get("link")):
        logging.debug('%s is in history', entry.get("title"))
        return False

    show_filter = show_config.filter
    if show_filter:

        # check episode-field against regex filter
        regex: str = show_filter.regex
        regex_field: str = show_filter.regex_field
        if (regex and regex_field and not re.search(regex, entry.get(regex_field))):
            logging.debug('%s does not fit regex', entry.get("title"))
            return False

        # check if episode before minimum date
        min_date = show_filter.min_date
        if min_date:
            min_date = parser.parse(min_date)
            entry_date = parser.parse(entry.get("published"))
            if entry_date < min_date:
                logging.debug(f'%s is before mindate', entry.get("title"))
                return False

        if not is_episode_released(entry.get("link")):
            logging.debug('%s is not yet released', entry.get("title"))
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
    try:
        subprocess.run(command, check=True)
        history.add_to_history(url)
    except subprocess.CalledProcessError:
        logging.error('Error downloading %s', url)


def check_show(show: ShowConfiguration) -> None:
    """Check all episodes of a show for new downloads."""
    feed = feedparser.parse(show.feed_url)
    entries = feed.entries
    entries.reverse()
    for entry in entries:
        if should_download(entry, show):
            logging.info('Downloading episode %s: %s', entry.get("title"), entry.get("link"))
            download_episode(entry.get("link"), show.download)


def check_all_shows(shows: List[ShowConfiguration]) -> None:
    """Check all shows in configuration for new downloads."""
    logging.info("checking all shows")
    for show in shows:
        check_show(show)


history = History("history.yaml")
config: Configuration = load_configuration_from_yaml("configuration.yaml")

schedule.every(config.interval).minutes.do(check_all_shows, shows=config.shows)
schedule.run_all()

while True:
    schedule.run_pending()
    time.sleep(1)
