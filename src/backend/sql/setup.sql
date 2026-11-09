-- Drop existing tables if they exist (in reverse dependency order)
DROP TABLE IF EXISTS elements_to_groups;
DROP TABLE IF EXISTS compounds;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS elements;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS accounts;

-- Table: accounts
CREATE TABLE accounts (
    id          BIGSERIAL PRIMARY KEY,
    email       TEXT NOT NULL UNIQUE,
    password    TEXT NOT NULL,
    date        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table: groups
CREATE TABLE groups (
    id          BIGSERIAL PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    owner_id    BIGINT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    date        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table: elements
CREATE TABLE elements (
    symbol          TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    system_group    INTEGER NOT NULL,
    system_period   INTEGER NOT NULL
);

-- Table: elements_to_groups
CREATE TABLE elements_to_groups (
    symbol      TEXT NOT NULL REFERENCES elements(symbol) ON DELETE CASCADE,
    group_id    BIGINT NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    date        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, group_id)
);

-- Table: categories
CREATE TABLE categories (
    id          BIGSERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    type        INTEGER NOT NULL,
    group_id    BIGINT NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    date        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table: compounds
CREATE TABLE compounds (
    id              BIGSERIAL PRIMARY KEY,
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
    category_id     BIGINT NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    group_id        BIGINT NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    date            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table: questions
CREATE TABLE questions (
    id              BIGSERIAL PRIMARY KEY,
    question        TEXT NOT NULL,
    correct_answer  TEXT NOT NULL,
    wrong_answer1   TEXT NOT NULL,
    wrong_answer2   TEXT NOT NULL,
    wrong_answer3   TEXT,
    wrong_answer4   TEXT,
    difficulty      TEXT NOT NULL,
    category_id     BIGINT NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    group_id        BIGINT NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    date            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
