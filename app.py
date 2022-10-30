"""Main module for the ZDF Downloader."""
import time
import schedule
import logging
from zdf_download import ZDFDownload
from configuration import Configuration, load_configuration_from_yaml
from history import History

def main() -> None:

    config: Configuration = load_configuration_from_yaml("configuration/configuration.yaml")
    history: History = History("configuration/history.yaml")
    zdf_downloader: ZDFDownload = ZDFDownload(history=history, config=config)

    log = logging.getLogger("zdf-download")
    log.info("launching application")

    schedule.every(config.interval).minutes.do(zdf_downloader.check_all_shows, shows=config.shows)
    schedule.run_all()

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
