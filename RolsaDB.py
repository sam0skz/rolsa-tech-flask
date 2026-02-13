import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    first_name TEXT,
    surname TEXT,
    dob TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS rolsa_carbon(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT NOT NULL,
    activity_name TEXT NOT NULL,
    carbon_output DECIMAL CHECK(carbon_output BETWEEN 1 AND 10),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    service_type TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")

test = [
    ('user1', 'pass1', 'email@example.com', 'Monkey', 'DLuffy', '1990-12-17'),
    ('him', 'othy', 'goat@majesty.com', 'Lebonbon', 'James', '1995-11-23'),
]

try:
    cursor.executemany("INSERT INTO users (username, password, email, first_name, surname, dob) VALUES(?,?,?,?,?,?)", test)
    print('Sample users successfully added.')
except sqlite3.IntegrityError:
    print('Sample users already exist.')
conn.commit()
conn.close()