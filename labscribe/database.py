# internal imports
import pickle
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Tuple, List, Callable, Union, Optional
from argparse import Namespace


def save_file(obj, filename: str):
    if filename.endswith(".pt"):
        try:
            import torch  # pyright: ignore
        except:
            raise ImportError(
                "Saving PyTorch data requires PyTorch to be installed"
            )
        torch.save(obj, filename)
    else:
        with open(filename, "wb") as f:
            pickle.dump(obj, f)
    return filename


class SQLDatabase:
    """
    Manage experiments using a sqlite3 database.
    """

    def __init__(self, name="default", log_path="results.db"):
        self.save_path = Path(log_path)
        self.exp_name = name
        self.now = datetime.now()
        self.git_commit = self._get_git_commit()
        self.exp_id = None
        self._setup()

    def _get_git_commit(self):
        try:
            return subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
        except:
            return ""

    def _query(self, db_name: Union[str, Path], query: str, params: Optional[Tuple] = None) -> None:
        """
        Perform a query on the database
        """
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        if params is None:
            c.execute(query)
        else:
            c.execute(query, params)
        conn.commit()
        conn.close()

    def _select(self, db_name: Union[str, Path], query: str, params: Optional[Tuple] = None) -> List:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        if params is None:
            c.execute(query)
        else:
            c.execute(query, params)
        results = c.fetchall()
        conn.close()
        return results

    def __get_sql_file(self):
        local_dir = Path(__file__).parent
        sql_file = local_dir / "data" / "db_setup.sql"
        with open(sql_file, "r") as open_file:
            query = open_file.read()
        return query

    def _first_time(self) -> None:
        """
        Create a brand new database
        """
        self.save_path.touch()
        create_table_queries = self.__get_sql_file().split("\n\n")
        for query in create_table_queries:
            self._query(self.save_path, query)

    def _save_exp(self):
        query = """INSERT into experiments(name, git_commit, datetime)
                   VALUES (?, ?, ?)"""
        params = (self.exp_name, self.git_commit, self.now)
        self._query(self.save_path, query, params)
        query = """SELECT id FROM experiments WHERE name=? AND git_commit=? AND datetime=?"""
        try:
            exp_id = self._select(self.save_path, query, params)[0][0]
        except sqlite3.Error as e:
            raise ValueError(f"Issue creating experiment, new experiment unknown: {e}")
        return exp_id

    def log_args(self, hparams):
        if isinstance(hparams, Namespace):
            # convert to dict
            hparams = vars(hparams)

        query = """INSERT INTO hyperparameters(name, value, exp_id)
                   VALUES (?, ?, ?)"""
        for k, v in hparams.items():
            params = (str(k), str(v), self.exp_id)
            # TODO: could insert multiple for better performance
            self._query(self.save_path, query, params)

    def _setup(self) -> None:
        """
        Setup a database connection with the DB specified
        by the save_path variable
        """
        if not self.save_path.exists():
            self._first_time()
        self.exp_id = self._save_exp()

    def log_asset(self, obj, filename, file_type: Optional[str] = None, save_fn: Callable = save_file):
        """
        Log an asset into the database, while saving it to the disk.

        :param obj: The object to save to disk and log into the asset table of the DB.
        :param filename: The location of where to save and what to call this new file.
        :param file_type: An optional type to tag in the database. This is useful for
            filtering for files in the DB, such as with:
            "SELECT * FROM assets WHERE type = '<sometype>';"
        :param save_fn: The function to use to save the file. This function should take
            the object, and filename as its parameters in that order.
        :type obj: Any
        :type filename: Optional[str]
        :type file_type: str
        :type save_fn: Callable
        :returns: The filename.
        """
        save_fn(obj, filename)
        query = """INSERT INTO assets(exp_id, name, type) VALUES (?, ?, ?)"""
        params = (
            self.exp_id,
            filename,
            file_type if file_type is not None else "",
        )
        self._query(self.save_path, query, params)
        return filename

    def log_metric(self, name: str, value: float):
        """
        Log a simple float/real metric value for this experiment.
        """
        query = """INSERT INTO results(metric, value, exp_id) VALUES (?, ?, ?)"""
        params = (name, value, self.exp_id)
        self._query(self.save_path, query, params)

    def log_step(self, epoch: int, step: int, dataset_type: str, value: float):
        """
        Log a training/validation step where the loss is recorded.
        """
        query = """INSERT INTO logs(exp_id, epoch, step, dataset_type, value)
                   VALUES (?, ?, ?, ?, ?)"""
        params = (self.exp_id, epoch, step, dataset_type, value)
        self._query(self.save_path, query, params)
