"""Main module for the ZDF Downloader."""
import os
import sys
import re
from typing import List

import logging
import subprocess
from dateutil import parser


from configuration import Configuration, ShowConfiguration, DownloadConfiguration
from history import History
from zdf_client import ZDFClient, ZDFEpisode

log = logging.getLogger("zdf-download")


class ZDFDownload():
    """Main-class to handle downloads."""

    def __init__(self, history: History, config: Configuration) -> None:
        self.history: History = history
        self.config: Configuration = config


    def should_download(self, episode: ZDFEpisode, show_config: ShowConfiguration) -> bool:
        """Check if an episode should be downloaded."""
        # check if episode was already downloaded
        if self.history.is_in_history(episode.sharing_url):
            log.debug('episode "%s" is in history', episode.title)
            return False

        show_filter = show_config.filter
        if show_filter:

            # check if episode before minimum date
            min_date = show_filter.min_date
            if min_date:
                min_date = parser.parse(min_date)
                # entry_date = parser.parse(episode.editorial_date)
                if episode.editorial_date < min_date:
                    log.debug('episode "%s" is before mindate', episode.title)
                    return False

        return True

    def find_filename(self, download: DownloadConfiguration) -> str:
        """Generate a new filename by adding one to the current newest filename."""
        episode_files: List[str] = list(filter(lambda filename: download.filename in filename, sorted(os.listdir(download.folder))))

        if len(episode_files) > 0:
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
            subprocess.run(["yt-dlp", url, "-o", download_path, "--force-generic"], check=True)
            self.history.add_to_history(url)
        except subprocess.CalledProcessError:
            log.error('error downloading %s', url)


    def check_show(self, show: ShowConfiguration) -> None:
        """Check all episodes of a show for new downloads."""

        downloader = ZDFClient()
        entries = downloader.get_episodes(show.canonical_id)
        entries.reverse()
        for entry in entries:
            if self.should_download(entry, show):
                log.info('downloading episode %s: %s', entry.title, entry.sharing_url)
                self.download_episode(entry.sharing_url, show.download)


    def check_all_shows(self, shows: List[ShowConfiguration]) -> None:
        """Check all shows in configuration for new downloads."""
        log.info("checking all shows")
        for show in shows:
            self.check_show(show)
        log.info("finished checking all shows")
