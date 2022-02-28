import os
import sys
import shutil
import pickle
import unittest
import sqlite3
from pathlib import Path

sys.path.append(str(Path(".").absolute()))
from labscribe.database import SQLDatabase


class SQLDatabaseTest(unittest.TestCase):
    def setUp(self):
        self.db = SQLDatabase(log_path="tests/results.db", name="test")
        self.conn = sqlite3.connect("tests/results.db")
        self.db.save_args({"test": 1, "test2": 2})

    def tearDown(self):
        os.remove("tests/results.db")
        shutil.rmtree("tests/test/", ignore_errors=True)

    def test_save_args(self):
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

    def test_log_asset(self):
        os.makedirs("tests/test/")
        self.db.log_asset([1], "tests/test/test.pkl")
        c = self.conn.cursor()
        c.execute("SELECT name from assets")
        results = c.fetchall()
        self.assertEqual(results[0][0], "tests/test/test.pkl")
        with open(results[0][0], "rb") as f:
            contents = pickle.load(f)
        self.assertEqual(contents[0], 1)

        # create a save function that add '.2' to the end of the filename
        def save_fn(obj, filename):
            filename += ".2"
            with open(filename, "wb") as f:
                pickle.dump(obj, f)
            return filename

        # test with the save function passed to the log_asset function
        self.db.log_asset([1], "tests/test/test.pkl", save_fn = save_fn)
        c = self.conn.cursor()
        c.execute("SELECT name from assets")
        results = c.fetchall()
        self.assertEqual(results[1][0], "tests/test/test.pkl.2")
        with open(results[0][0], "rb") as f:
            contents = pickle.load(f)
        self.assertEqual(contents[0], 1)


if __name__ == "__main__":
    unittest.main()
