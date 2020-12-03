# internal imports
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Tuple, List


class SQLDatabase:
    """
    Manage experiments using a sqlite3 database.
    """

    def __init__(self, hparams, save_path="results.db", exp_name="default"):
        self.hparams = hparams
        self.save_path = Path(save_path)
        self.exp_name = exp_name
        self.now = datetime.now()
        self.git_commit = self._get_git_commit()
        self.exp_id = None
        self._setup()

    def _get_git_commit(self):
        try:
            return subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
        except:
            return ""

    def _query(self, db_name: str, query: str, params: Tuple = None) -> None:
        """
        Perform a query on the database
        """
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute(query, params)
        c.commit()
        conn.close()

    def _select(self, db_name: str, query: str, params: Tuple = None) -> List:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute(query, params)
        results = c.fetchall()
        conn.close()
        return results

    def _first_time(self) -> None:
        """
        Create a brand new database
        """
        self.save_path.touch()
        create_table_query = ""  # TODO
        self.query(self.save_path, create_table_query)

    def _save_exp(self):
        query = """INSERT into experiments(name, git, datetime)
                   VALUES (?, ?, ?)"""
        params = (self.exp_name, self.gitcommit, self.now)
        self._query(self.save_path, query, params)
        query = """SELECT id FROM experiments WHERE name=? AND git=? AND datetime=?"""
        return self._select(self.save_path, query, params)

    def _log_hyperparams(self):
        query = """INSERT INTO hyperparameters(name, value, exp_id)
                   VALUES (?, ?, ?)"""
        for k, v in self.hparams.items():
            params = (k, v, self.exp_id)
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
        self._log_hyperparams()

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
