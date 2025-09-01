import sqlite3

def setup_database():
    """Sets up the SQLite database and creates the users table with new columns."""
    conn = sqlite3.connect('earning_bot.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            points INTEGER DEFAULT 0,
            ads_watched_today INTEGER DEFAULT 0,
            last_ad_time INTEGER DEFAULT 0,
            referral_code TEXT UNIQUE,
            referred_by TEXT,
            language TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Database and 'users' table created/updated successfully!")

if __name__ == '__main__':
    setup_database()
