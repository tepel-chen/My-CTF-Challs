import sqlite3
import os, re

FLAG = os.environ.get("FLAG", "")
if not re.match(r"Alpaca\{[a-zA-Z0-9_]+\}", FLAG):
    print("invalid flag")
    exit()

db = sqlite3.connect("/tmp/app.db")
db.execute("""
    CREATE TABLE IF NOT EXISTS secrets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT NOT NULL UNIQUE,
        secret TEXT NOT NULL
    )
""")
db.execute("""
    CREATE TABLE IF NOT EXISTS flag (
        flag TEXT NOT NULL
    )
""")
db.execute(f"""
    INSERT INTO flag (flag) VALUES ('{FLAG}')
""")
db.commit()