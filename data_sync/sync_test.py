import sqlite3
import time
import json

class DataSyncTest:
    def __init__(self):
        self.db_path = '../data_receiver/sensor_data.db'
        
    def get_unsynced_data(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sensor_data ORDER BY received_at ASC')
            rows = cursor.fetchall()
            conn.close()
            
            data = []
            for row in rows:
                data.append({
                    'id': row[0],
                    'device_id': row[1],
                    'temperature': row[2],
                    'humidity': row[3],
                    'analog_value': row[4],
                    'received_at': row[5]
                })
            return data
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
    
    def simulate_sync(self):
        print("🔄 TEST: Starting data synchronization...")
        
        data_to_sync = self.get_unsynced_data()
        
        if not data_to_sync:
            print("📭 No data to sync")
            return
        
        print(f"📦 Found {len(data_to_sync)} records to sync")
        
        for record in data_to_sync:
            print(f"✅ Would send to RabbitMQ: {record['device_id']} - Temp: {record['temperature']}")
        
        # Имитируем удаление данных
        if data_to_sync:
            data_ids = [record['id'] for record in data_to_sync]
            self.delete_synced_data(data_ids)
            print(f"🗑️ TEST: Deleted {len(data_ids)} records (simulation)")
    
    def delete_synced_data(self, data_ids):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(data_ids))
            cursor.execute(f'DELETE FROM sensor_data WHERE id IN ({placeholders})', data_ids)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Failed to delete data: {e}")
            return False

def main():
    sync = DataSyncTest()
    while True:
        sync.simulate_sync()
        print("⏰ Waiting 10 seconds...")
        time.sleep(10)

if __name__ == '__main__':
    main()