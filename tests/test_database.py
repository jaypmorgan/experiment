import os
import sys
import unittest
import sqlite3
from pathlib import Path

sys.path.append(str(Path(".").absolute()))
from labscribe.database import SQLDatabase


class SQLDatabaseTest(unittest.TestCase):
    def setUp(self):
        self.db = SQLDatabase(
            hparams={"test": 1, "test2": 2},
            save_path="tests/results.db",
            exp_name="test",
        )
        # test connection
        self.conn = sqlite3.connect("tests/results.db")

    def tearDown(self):
        os.remove("tests/results.db")

    def test_hyperparams(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM hyperparameters")
        results = c.fetchall()
        self.assertEqual(results[0][1], "test")
        self.assertEqual(results[1][1], "test2")
        self.assertEqual(results[1][2], "2")

    def test_git_commmit(self):
        c = self.conn.cursor()
        c.execute("SELECT git_commit FROM experiments")
        results = c.fetchall()
        self.assertTrue(any(results[0][0]))

    def test_datetime(self):
        c = self.conn.cursor()
        c.execute("SELECT datetime from experiments")
        results = c.fetchall()
        self.assertTrue(any(results[0][0]))

    def test_log_metric(self):
        self.db.log_metric("testing", 2)
        c = self.conn.cursor()
        c.execute("SELECT * from results")
        results = c.fetchall()
        self.assertTrue(len(results))
        self.assertEqual(results[0][1], "testing")
        self.assertEqual(results[0][2], 2.0)

    def test_log_step(self):
        self.db.log_step(1.0, 1, "training", 0.5)


if __name__ == "__main__":
    unittest.main()
