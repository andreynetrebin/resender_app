import sqlite3
from os import path, getcwd

connection = sqlite3.connect(path.join(getcwd(), 'database', '../../app.db'))

with open(path.join(getcwd(), 'database', 'schema.sql')) as f:
    connection.executescript(f.read())

connection.close()
