from src.database.database import Database

db = Database()

# Enable foreign key support (must be done per connection in SQLite)
db.cursor.execute("PRAGMA foreign_keys = ON")

# Drop tables if they exist (for re-creation)
db.cursor.execute("DROP TABLE IF EXISTS elements_to_groups")
db.cursor.execute("DROP TABLE IF EXISTS compounds")
db.cursor.execute("DROP TABLE IF EXISTS elements")
db.cursor.execute("DROP TABLE IF EXISTS categories")
db.cursor.execute("DROP TABLE IF EXISTS questions")
db.cursor.execute("DROP TABLE IF EXISTS groups")
db.cursor.execute("DROP TABLE IF EXISTS accounts")

# Create table "accounts"
db.cursor.execute("""
CREATE TABLE accounts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    email       TEXT NOT NULL UNIQUE,
    password    TEXT NOT NULL,
    date        TEXT NOT NULL
)
""")

# Create table "groups" with foreign key reference to accounts(id)
db.cursor.execute("""
CREATE TABLE groups (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    owner_id    INTEGER NOT NULL,
    date        TEXT NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES accounts(id)
)
""")

# Create table "elements"
db.cursor.execute("""
CREATE TABLE elements (
    symbol  TEXT PRIMARY KEY,
    name    TEXT NOT NULL,
    "group" INTEGER NOT NULL,
    period  INTEGER NOT NULL
)
""")

# Create table "elements_to_groups" with foreign key reference to elements(symbol) and groups(id)
db.cursor.execute("""
CREATE TABLE elements_to_groups (
    symbol      TEXT NOT NULL,
    group_id    INTEGER NOT NULL,
    date        TEXT NOT NULL,
    FOREIGN KEY (symbol) REFERENCES elements(symbol),
    FOREIGN KEY (group_id) REFERENCES groups(id)
)
""")

# Create table "categories"
db.cursor.execute("""
CREATE TABLE categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    group_id    INTEGER NOT NULL,
    date        TEXT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES groups(id)
)
""")

# Create table "formulas" with foreign key reference to categories(id) and groups(id)
db.cursor.execute("""
CREATE TABLE compounds (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    correct_name    TEXT NOT NULL,
    wrong_name1     TEXT NOT NULL,
    wrong_name2     TEXT NOT NULL,
    wrong_name3     TEXT NOT NULL,
    wrong_name4     TEXT NOT NULL,
    correct_formula TEXT NOT NULL,
    wrong_formula1  TEXT NOT NULL,
    wrong_formula2  TEXT NOT NULL,
    wrong_formula3  TEXT NOT NULL,
    wrong_formula4  TEXT NOT NULL,
    category_id     INTEGER NOT NULL,
    group_id        INTEGER NOT NULL,
    date            TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (group_id) REFERENCES groups(id)
)
""")

# Create table "questions" with foreign key reference to categories(id)
db.cursor.execute("""
CREATE TABLE questions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    question        TEXT NOT NULL,
    correct_answer  TEXT NOT NULL,
    wrong_answer1   TEXT NOT NULL,
    wrong_answer2   TEXT NOT NULL,
    wrong_answer3   TEXT NOT NULL,
    wrong_answer4   TEXT NOT NULL,
    group_id        INTEGER NOT NULL,
    date            TEXT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES groups(id)
)
""")

db.fill_elements_table()

db.connection.commit()
db.close()
