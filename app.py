"""Main module for the ZDF Downloader."""
import time
import schedule
from zdf_download import ZDFDownload
from configuration import Configuration, load_configuration_from_yaml
from history import History


history: History = History("history.yaml")
config: Configuration = load_configuration_from_yaml("configuration/configuration.yaml")
zdf_downloader: ZDFDownload = ZDFDownload(history=history, config=config)

schedule.every(config.interval).minutes.do(zdf_downloader.check_all_shows, shows=config.shows)
schedule.run_all()

while True:
    schedule.run_pending()
    time.sleep(1)
