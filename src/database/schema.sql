CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE accounts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    email       TEXT NOT NULL UNIQUE,
    password    TEXT NOT NULL,
    date        TEXT NOT NULL
);
CREATE TABLE groups (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    owner_id    INTEGER NOT NULL,
    date        TEXT NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES accounts(id)
);
CREATE TABLE elements (
    symbol          TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    system_group    INTEGER NOT NULL,
    system_period   INTEGER NOT NULL
);
CREATE TABLE elements_to_groups (
    symbol      TEXT NOT NULL,
    group_id    INTEGER NOT NULL,
    date        TEXT NOT NULL,
    FOREIGN KEY (symbol) REFERENCES elements(symbol),
    FOREIGN KEY (group_id) REFERENCES groups(id)
);
CREATE TABLE categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    type        INTEGER NOT NULL,
    group_id    INTEGER NOT NULL,
    date        TEXT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES groups(id)
);
CREATE TABLE compounds (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    correct_name    TEXT NOT NULL,
    wrong_name1     TEXT NOT NULL,
    wrong_name2     TEXT NOT NULL,
    wrong_name3     TEXT,
    wrong_name4     TEXT,
    correct_formula TEXT NOT NULL,
    wrong_formula1  TEXT NOT NULL,
    wrong_formula2  TEXT NOT NULL,
    wrong_formula3  TEXT,
    wrong_formula4  TEXT,
    difficulty      TEXT NOT NULL,
    category_id     INTEGER NOT NULL,
    group_id        INTEGER NOT NULL,
    date            TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (group_id) REFERENCES groups(id)
);
CREATE TABLE questions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    question        TEXT NOT NULL,
    correct_answer  TEXT NOT NULL,
    wrong_answer1   TEXT NOT NULL,
    wrong_answer2   TEXT NOT NULL,
    wrong_answer3   TEXT,
    wrong_answer4   TEXT,
    difficulty      TEXT NOT NULL,
    category_id     INTEGER NOT NULL,
    group_id        INTEGER NOT NULL,
    date            TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (group_id) REFERENCES groups(id)
);
