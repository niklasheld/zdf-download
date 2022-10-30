"""Module handles configuration of the application."""
from typing import List
import os
import yaml
import logging
from sys import stdout

log = logging.getLogger("zdf-download")

class FilterConfiguration():
    """Configures filters within a show."""

    def __setup_logging(self) -> None:
        """Configure logging for the application"""
        log = logging.getLogger("zdf-download")

        log.setLevel(logging.DEBUG)
        log_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        console_handler = logging.StreamHandler(stdout)
        console_handler.setFormatter(log_formatter)
        log.addHandler(console_handler)

    def __init__(self, regex: str, regex_field: str, min_date: str) -> None:
        self.__setup_logging()
        self.regex: str = regex
        self.regex_field: str = regex_field
        self.min_date: str = min_date


class DownloadConfiguration():
    """Configures where a show is downloaded to."""

    def __init__(self, folder: str, filename: str) -> None:
        self.folder: str = folder
        self.filename: str = filename


class ShowConfiguration():
    """Configures a show."""

    def __init__(self, feed_url: str, filter: FilterConfiguration, download: DownloadConfiguration) -> None:
        self.feed_url: str = feed_url
        self.filter: FilterConfiguration = filter
        self.download: DownloadConfiguration = download


class Configuration():
    """Configures an application."""

    def __init__(self, interval: int, shows: List[ShowConfiguration]) -> None:
        self.interval: int = interval
        self.shows: List[ShowConfiguration] = shows


def load_configuration_from_yaml(filename: str) -> Configuration:
    """Create a configuration-object from a yaml-file."""
    if not os.path.isfile(filename):
        print("Terminating... No configuration found")
        exit()

    with open(filename, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)

        interval: int = config["interval"]
        shows: List[ShowConfiguration] = []

        for show in config["shows"]:
            show_filter: FilterConfiguration = FilterConfiguration(
                regex=show.get("filter").get("regex"),
                regex_field=show.get("filter").get("regexField"),
                min_date=show.get("filter").get("minDate"))
            show_download: DownloadConfiguration = DownloadConfiguration(
                folder=show.get("download").get("folder"),
                filename=show.get("download").get("filename"))
            show: ShowConfiguration = ShowConfiguration(
                filter=show_filter,
                download=show_download,
                feed_url=show.get("feed-url"))
            shows.append(show)

        return Configuration(interval=interval, shows=shows)
