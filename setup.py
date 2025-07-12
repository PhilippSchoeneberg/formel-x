import sqlite3

connection = sqlite3.connect("formulaX.db")
cursor = connection.cursor()

# Enable foreign key support (must be done per connection in SQLite)
cursor.execute("PRAGMA foreign_keys = ON")

# Drop tables if they exist (for re-creation)
cursor.execute("DROP TABLE IF EXISTS formulas")
cursor.execute("DROP TABLE IF EXISTS categories")

# Create categories table
cursor.execute("""
CREATE TABLE categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    date TEXT NOT NULL
)
""")

# Create formulas table with foreign key reference to categories(id)
cursor.execute("""
CREATE TABLE formulas (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT NOT NULL,
    formula  TEXT NOT NULL,
    category INTEGER NOT NULL,
    date     TEXT NOT NULL,
    FOREIGN KEY (category) REFERENCES categories(id)
)
""")

connection.commit()
connection.close()
