from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

DB_PATH = 'card_data.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS card_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

@app.route('/card_data', methods=['POST'])
def receive_card_data():
    data = request.get_json()
    if not data or 'card_id' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    card_id = data['card_id']
    timestamp = datetime.now().isoformat()
    
    # Save to database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO card_entries (card_id, timestamp) VALUES (?, ?)", (card_id, timestamp))
    conn.commit()
    conn.close()
    
    print(f"Received and saved card data: {card_id} at {timestamp}")
    
    return jsonify({'status': 'success', 'card_id': card_id, 'timestamp': timestamp}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)