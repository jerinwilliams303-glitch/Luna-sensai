import sqlite3
import hashlib
import pandas as pd

DATABASE_NAME = "luna_sensai.db"

def init_db():
    """Initializes the database and creates/updates tables."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Create logs table with new columns for notes and tags
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            breakfast TEXT,
            lunch TEXT,
            dinner TEXT,
            mood TEXT,
            sleep_hours REAL,
            stress_level REAL,
            physical_activity TEXT,
            cramp_intensity REAL,
            pcos INTEGER,
            thyroid INTEGER,
            notes TEXT,
            custom_tags TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create reminders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            reminder_date TEXT NOT NULL,
            message TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # --- Schema Upgrade Section ---
    # Add notes and custom_tags columns if they don't exist (for users with old database)
    try:
        cursor.execute("ALTER TABLE logs ADD COLUMN notes TEXT")
    except sqlite3.OperationalError:
        pass # Column already exists
    try:
        cursor.execute("ALTER TABLE logs ADD COLUMN custom_tags TEXT")
    except sqlite3.OperationalError:
        pass # Column already exists

    conn.commit()
    conn.close()

def hash_password(password):
    """Hashes the password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    """Adds a new user to the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    password_hash = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    """Checks if a user exists and the password is correct."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    password_hash = hash_password(password)
    cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and user[1] == password_hash:
        return user[0]
    return None

def get_username(user_id):
    """Gets the username for a given user_id."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    username = cursor.fetchone()
    conn.close()
    return username[0] if username else "Unknown"

def add_log(user_id, log_data):
    """Adds a daily log for a specific user, including notes and tags."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO logs (user_id, date, breakfast, lunch, dinner, mood, sleep_hours, stress_level, physical_activity, cramp_intensity, pcos, thyroid, notes, custom_tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id, log_data.get('Date'), log_data.get('Breakfast'), log_data.get('Lunch'),
        log_data.get('Dinner'), log_data.get('Mood'), log_data.get('Sleep Hours'),
        log_data.get('Stress Level'), log_data.get('Physical Activity'),
        log_data.get('Cramp Intensity'), int(log_data.get('PCOS', 0)), int(log_data.get('Thyroid', 0)),
        log_data.get('Notes'), log_data.get('Custom Tags')
    ))
    conn.commit()
    conn.close()

def get_logs(user_id):
    """Retrieves all logs for a specific user as a pandas DataFrame."""
    conn = sqlite3.connect(DATABASE_NAME)
    df = pd.read_sql_query("SELECT * FROM logs WHERE user_id = ?", conn, params=(user_id,))
    conn.close()
    return df

def add_reminder(user_id, date, message):
    """Adds a new reminder to the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reminders (user_id, reminder_date, message) VALUES (?, ?, ?)", (user_id, date, message))
    conn.commit()
    conn.close()

def get_reminders_for_date(user_id, date):
    """Gets all reminders for a specific user and date."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT message FROM reminders WHERE user_id = ? AND reminder_date = ?", (user_id, date))
    reminders = cursor.fetchall()
    conn.close()
    return [r[0] for r in reminders]