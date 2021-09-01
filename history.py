import os
import yaml
from typing import List

class History():

    def __init__(self) -> None:
        self.history_file: str = "history.yaml"


    def get_history(self) -> List[str]:
        ''' get all urls from history-file'''
        if not os.path.isfile(self.history_file):
            return []
        else:
            with open(self.history_file, "r") as f:
                history : List[str] = yaml.load(f.read())
            return history


    def is_in_history(self, url: str) -> bool:
        ''' check if an url is included in the history-file'''
        return url in self.get_history()


    def add_to_history(self, url: str) -> None:
        ''' add an url to the history-file '''
        history: List[str] = self.get_history()
        history.append(url)
        with open(self.history_file, "w+") as f:
            f.write(yaml.dump(history))
