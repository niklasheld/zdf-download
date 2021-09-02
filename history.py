"""Module handles history of already downloaded episodes."""
import os
from typing import List
import yaml


class History():
    """Handles already downloaded episodes for all shows."""

    def __init__(self, history_file: str) -> None:
        self.history_file: str = history_file

    def get_history(self) -> List[str]:
        """Get all urls from history-file."""
        if not os.path.isfile(self.history_file):
            return []
        else:
            with open(self.history_file, "r") as file:
                history: List[str] = yaml.load(file.read())
            return history

    def is_in_history(self, url: str) -> bool:
        """Check if an url is included in the history-file."""
        return url in self.get_history()

    def add_to_history(self, url: str) -> None:
        """Add an url to the history-file."""
        history: List[str] = self.get_history()
        history.append(url)
        with open(self.history_file, "w+") as file:
            file.write(yaml.dump(history))
