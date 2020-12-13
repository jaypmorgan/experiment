# internal imports
import pickle
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Tuple, List, Dict


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

    def _query(self, db_name: str, query: str, params: Tuple = None) -> None:
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

    def _select(self, db_name: str, query: str, params: Tuple = None) -> List:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
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

    def save_args(self, hparams):
        query = """INSERT INTO hyperparameters(name, value, exp_id)
                   VALUES (?, ?, ?)"""
        for k, v in hparams.items():
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

    def _save_file(self, obj, filename):
        filepath: Path = self.save_path.parent / self.exp_name
        filepath.mkdir(parents=True, exist_ok=True)
        fn = filepath / filename
        with open(fn, "wb") as f:
            pickle.dump(obj, f)
        return str(fn)

    def log_asset(self, obj, filename, file_type: str = None):
        realised_path = self._save_file(obj, filename)
        query = """INSERT INTO assets(exp_id, name, type) VALUES (?, ?, ?)"""
        params = (
            self.exp_id,
            realised_path,
            file_type if file_type is not None else "",
        )
        self._query(self.save_path, query, params)

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
