import yaml
import os

class Configuration():

    def load(self) -> dict:
        """ Load configuration from file """
        if not os.path.isfile("configuration.yaml"):
            print("Terminating... No configuration found")
            exit()

        with open("configuration.yaml", "r") as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)
            return config