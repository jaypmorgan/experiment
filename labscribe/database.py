# internal imports
import sqlite3
from pathlib import Path
from typing import Tuple, List


class Database:
    """
    Manage experiments using a sqlite3 database.
    """

    def __init__(self, hparams, save_path="results.db", exp_name="default"):
        self.hparams = hparams
        self.save_path = Path(save_path)
        self.exp_name = exp_name
        self._setup()

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

    def _get_or_create_model_id(self, model_name):
        query = """SELECT id from models WHERE name=?"""
        params = (model_name,)
        model_id = self._select(self.save_path, query, params)
        if not model_id:
            # none exists, so we need to create it and return the new id
            in_query = """INSERT INTO models(name, pretty_name) VALUES (?, ?)"""
            in_params = (model_name, model_name)
            self.query(self.save_path, in_query, in_params)
            model_id = self._select(self.save_path, query, params)
        return model_id

    def _save_exp(self):
        query = """INSERT into experiments(name, model_id, dataset_id, git, datetime)
                   VALUES (?, ?, ?, ?, ?)"""
        params = (
            self.hparams["exp_name"],
            self._get_model_id(self.hparams["model_name"]),
        )
        self._query(self.save_path, query, params)

    def _setup(self) -> None:
        """
        Setup a database connection with the DB specified
        by the save_path variable
        """
        if not self.save_path.exists():
            self._first_time()
