import sqlite3


conn = sqlite3.connect('data/data.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS admin (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)')
cursor.execute('INSERT INTO admin (username, password) VALUES (?, ?)', ('admin', 'admin'))
conn.commit()
cursor.close()
conn.close()