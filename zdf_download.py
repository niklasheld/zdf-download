"""Main module for the ZDF Downloader."""
import os
import sys
import re
from typing import List

import logging
import subprocess
import feedparser
import requests
from dateutil import parser


from configuration import Configuration, ShowConfiguration, DownloadConfiguration
from history import History

log = logging.getLogger("zdf-download")


class ZDFDownload():
    """Main-class to handle downloads."""

    def __init__(self, history: History, config: Configuration) -> None:
        self.history: History = history
        self.config: Configuration = config


    def should_download(self, entry, show_config: ShowConfiguration) -> bool:
        """Check if an episode should be downloaded."""
        # check if episode was already downloaded
        if self.history.is_in_history(entry.get("link")):
            log.debug('episode "%s" is in history', entry.get("title"))
            return False

        show_filter = show_config.filter
        if show_filter:

            # check episode-field against regex filter
            regex: str = show_filter.regex
            regex_field: str = show_filter.regex_field
            if (regex and regex_field and not re.search(regex, entry.get(regex_field))):
                log.debug('episode "%s" does not fit regex', entry.get("title"))
                return False

            # check if episode before minimum date
            min_date = show_filter.min_date
            if min_date:
                min_date = parser.parse(min_date)
                entry_date = parser.parse(entry.get("published"))
                if entry_date < min_date:
                    log.debug('episode "%s" is before mindate', entry.get("title"))
                    return False

            if not self.is_episode_released(entry.get("link")):
                log.debug('episode "%s" is not yet released', entry.get("title"))
                return False

        return True


    def is_episode_released(self, url: str) -> bool:
        """Check if an episode has actually been released (rss feed has future episode)."""
        result = requests.get(url)
        return "verfügbar bis" in result.text


    def find_filename(self, download: DownloadConfiguration) -> str:
        """Generate a new filename by adding one to the current newest filename."""
        episode_files: List[str] = list(filter(lambda filename: download.filename in filename, sorted(os.listdir(download.folder))))

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


    def download_episode(self, url: str, download: DownloadConfiguration):
        """Download episode using youtube-dl."""
        filename = self.find_filename(download)
        download_path = download.folder + "/" + filename + ".%(ext)s"
        try:
            subprocess.run(["youtube-dl", url, "-o", download_path], check=True)
            self.history.add_to_history(url)
        except subprocess.CalledProcessError:
            log.error('error downloading %s', url)


    def check_show(self, show: ShowConfiguration) -> None:
        """Check all episodes of a show for new downloads."""
        feed = feedparser.parse(show.feed_url)
        entries = feed.entries
        entries.reverse()
        for entry in entries:
            if self.should_download(entry, show):
                log.info('downloading episode %s: %s', entry.get("title"), entry.get("link"))
                self.download_episode(entry.get("link"), show.download)


    def check_all_shows(self, shows: List[ShowConfiguration]) -> None:
        """Check all shows in configuration for new downloads."""
        log.info("checking all shows")
        for show in shows:
            self.check_show(show)
        log.info("finished checking all shows")
