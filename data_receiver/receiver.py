from flask import Flask, request, jsonify
import sqlite3
import datetime
import json

app = Flask(__name__)

def init_database():
    conn = sqlite3.connect('sensor_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            temperature REAL,
            humidity REAL,
            analog_value INTEGER,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized!")

def save_to_database(data):
    try:
        conn = sqlite3.connect('sensor_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sensor_data 
            (device_id, temperature, humidity, analog_value, received_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['device_id'],
            data['temperature'],
            data['humidity'],
            data['analog_value'],
            datetime.datetime.now()
        ))
        
        conn.commit()
        conn.close()
        print(f"✅ Data saved from device: {data['device_id']}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving to database: {e}")
        return False

@app.route('/data', methods=['POST'])
def receive_data():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        print(f"📨 Received data: {data}")
        
        if save_to_database(data):
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "database_error"}), 500
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_database()
    print("🚀 Starting Data Receiver on http://0.0.0.0:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)