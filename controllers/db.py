import sqlite3



class DB:
    
    @staticmethod
    def login(username, password):
        conn = sqlite3.connect('data/data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admin WHERE username = ? AND password = ?', (username, password))
        return cursor.fetchone()
    
    @staticmethod
    def plan_call(df):
        
        conn = sqlite3.connect('data/data.db')
        cursor = conn.cursor()

        cursor.execute('CREATE TABLE IF NOT EXISTS plan_call (id INTEGER PRIMARY KEY AUTOINCREMENT, client_id TEXT, name TEXT, phone_number TEXT, debt_amount REAL, monthly_pay REAL, borrowed_date TEXT, skipped_days INTEGER,status TEXT)')

        for index, row in df.iterrows():
            cursor.execute(
                'INSERT INTO plan_call (client_id, name, phone_number, debt_amount, monthly_pay, borrowed_date, skipped_days, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (row['client_id'], row['name'], row['phone_number'], row['debt_amount'], row['monthly_pay'], row['borrowed_date'], row['skipped_days'], 'not called')
            )
        conn.commit()
        cursor.close()

    @staticmethod
    def take_plans():

        conn = sqlite3.connect('data/data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM plan_call')
        return [
            {
                'id': row[0],
                'client_id': row[1],
                'name': row[2],
                'phone_number': row[3],
                'debt_amount': row[4],
                'monthly_pay': row[5],
                'borrowed_date': row[6],
                'skipped_days': row[7],
                'status': row[8]
            } for row in cursor.fetchall()
            
        ]
    @staticmethod
    def delete_plan(phone_number):
        conn = sqlite3.connect('data/data.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM plan_call WHERE phone_number = ?', (phone_number,))
        conn.commit()
        cursor.close()

    @staticmethod
    def after_call(twillio_info):
        conn = sqlite3.connect('data/data.db')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS after_call (id INTEGER PRIMARY KEY AUTOINCREMENT, phone_number TEXT, duration INTEGER, date_created TEXT, download_url TEXT, reason TEXT, date TEXT)')
        cursor.execute(
            'INSERT INTO after_call (phone_number, duration, date_created, download_url, reason, date) VALUES (?, ?, ?, ?, ?, ?)',
            (twillio_info['phone_number'], twillio_info['duration'], twillio_info['date_created'], twillio_info['download_url'], twillio_info['reason'], twillio_info['date'])
        )
        conn.commit()
        cursor.close()

    @staticmethod
    def take_after_calls():
        conn = sqlite3.connect('data/data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM after_call')
        return [
            {
                'id': row[0],
                'phone_number': row[1],
                'duration': row[2],
                'date_created': row[3],
                'download_url': row[4],
                'reason': row[5],
                'date': row[6]
            } for row in cursor.fetchall()
        ]




    
       