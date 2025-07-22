import sqlite3

connection = sqlite3.connect("formulaX.db")
cursor = connection.cursor()

# Enable foreign key support (must be done per connection in SQLite)
cursor.execute("PRAGMA foreign_keys = ON")

# Drop tables if they exist (for re-creation)
cursor.execute("DROP TABLE IF EXISTS accounts")
cursor.execute("DROP TABLE IF EXISTS groups")
cursor.execute("DROP TABLE IF EXISTS elements")
cursor.execute("DROP TABLE IF EXISTS compounds")
cursor.execute("DROP TABLE IF EXISTS categories")
cursor.execute("DROP TABLE IF EXISTS questions")

# Create table "accounts"
cursor.execute("""
CREATE TABLE accounts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    email       TEXT NOT NULL UNIQUE,
    password    TEXT NOT NULL,
    date        TEXT NOT NULL
)
""")

# Create table "groups" with foreign key reference to accounts(id)
cursor.execute("""
CREATE TABLE groups (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    owner_id    INTEGER NOT NULL,
    date        TEXT NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES accounts(id)
)
""")

# Create table "elements" with foreign key reference to categories(id)
cursor.execute("""
CREATE TABLE elements (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT NOT NULL,
    formula  TEXT NOT NULL,
    date     TEXT NOT NULL
)
""")

# Create table "categories"
cursor.execute("""
CREATE TABLE categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    date TEXT NOT NULL
)
""")

# Create table "formulas" with foreign key reference to categories(id)
cursor.execute("""
CREATE TABLE compounds (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    correct_name    TEXT NOT NULL,
    wrong_name1     TEXT NOT NULL,
    wrong_name2     TEXT NOT NULL,
    correct_formula TEXT NOT NULL,
    wrong_formula1  TEXT NOT NULL,
    wrong_formula2  TEXT NOT NULL,
    category_id        INTEGER NOT NULL,
    date            TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id)
)
""")

# Create table "questions" with foreign key reference to categories(id)
cursor.execute("""
CREATE TABLE questions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    question        TEXT NOT NULL,
    correct_answer  TEXT NOT NULL,
    wrong_answer1   TEXT NOT NULL,
    wrong_answer2   TEXT NOT NULL,
    wrong_answer3   TEXT NOT NULL,
    wrong_answer4   TEXT NOT NULL,
    date            TEXT NOT NULL
)
""")

connection.commit()
connection.close()
