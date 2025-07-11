import sqlite3

connection = sqlite3.connect("formulaX.db")
cursor = connection.cursor()

sql_statement = """
CREATE TABLE formula (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    formula TEXT NOT NULL,
    name TEXT NOT NULL
);
"""

cursor.execute(sql_statement)
connection.commit()
connection.close()
