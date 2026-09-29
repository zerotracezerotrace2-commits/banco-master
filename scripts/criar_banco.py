import sqlite3

conn = sqlite3.connect("banco.db")
print("SQLite OK")
conn.close()
