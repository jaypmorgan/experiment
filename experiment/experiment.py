"""
A very simple class to manage experiments
"""
# internal imports
import json
import pickle
from pathlib import Path
from typing import Any


class Experiment:
    """ Simple experiment """

    def __init__(self, name: str = "default", log_path: str = "data/logs"):
        self.name = name
        self.log_path = Path(log_path)
        self.save_path = self.log_path / self.name

    def _setup(self):
        self.save_path.mkdir(exist_ok=True, parents=True)

    def _make_filepath(self, filename: str) -> str:
        return str(self.save_path / filename)

    def save_args(self, args) -> None:
        """ Save Args as a text file """
        name = self._make_filepath("hparams.json")
        with open(name, "w") as file:
            json.dump(vars(args), file)

    def log_asset(self, asset: Any, name: str) -> None:
        """ Save a python object to a pickle file """
        name = self._make_filepath(name)
        with open(name, "wb") as pkl_file:
            pickle.dump(asset, pkl_file)
