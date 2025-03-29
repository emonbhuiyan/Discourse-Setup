import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('discourse_automation.db')
    c = conn.cursor()
    
    # Create execution history table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS execution_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  script_name TEXT,
                  occupation TEXT,
                  status TEXT,
                  execution_time TIMESTAMP)''')
    
    conn.commit()
    conn.close()

def log_execution(script_name, occupation, status):
    conn = sqlite3.connect('discourse_automation.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO execution_history 
                 (script_name, occupation, status, execution_time)
                 VALUES (?, ?, ?, ?)''',
              (script_name, occupation or 'Unconfigured', status, datetime.now()))
    
    conn.commit()
    conn.close()

def get_execution_history():
    conn = sqlite3.connect('discourse_automation.db')
    c = conn.cursor()
    
    c.execute('''SELECT id, script_name, occupation, status, execution_time
                 FROM execution_history
                 ORDER BY execution_time DESC''')
    
    history = [{
        'id': row[0],
        'script_name': row[1],
        'occupation': row[2],
        'status': row[3],
        'execution_time': row[4]
    } for row in c.fetchall()]
    
    conn.close()
    return history