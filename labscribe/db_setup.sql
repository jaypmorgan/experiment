CREATE TABLE models (
       id integer PRIMARY KEY,
       name text NOT NULL,
       pretty_name text NOT NULL,
)

CREATE TABLE datasets (
       id integer PRIMARY KEY,
       name text NOT NULL,
       pretty_name text NOT NULL,
)

CREATE TABLE experiments (
       id integer PRIMARY KEY,
       name text,
       model_id integer,
       dataset_id integer,
       git_commit text,
       datetime text NOT NULL,
       FOREIGN KEY (model_id) REFERENCES models(id),
       FOREIGN KEY (dataset_id) REFERENCES datasets(id),
)

CREATE TABLE assets (
       id integer PRIMARY KEY,
       exp_id integer,
       name text,
       type text,
       FOREIGN KEY (exp_id) REFERENCES experiments(id),
)

CREATE TABLE hyperparameters (
       id integer PRIMARY KEY,
       name text NOT NULL,
       value text NOT NULL,
       exp_id integer,
       FOREIGN KEY (exp_id) REFERENCES experiments(id)
)

CREATE TABLE logs (
       id integer PRIMARY KEY,
       exp_id integer,
       epoch integer,
       step integer,
       dataset_type name,
       value real,
       FOREIGN KEY (exp_id) REFERENCES experiments(id)
)

CREATE TABLE results (
       id integer PRIMARY KEY,
       metric text NOT NULL,
       value real NOT NULL,
       exp_id integer,
       FOREIGN KEY (exp_id) REFERENCES experiments(id)
)
