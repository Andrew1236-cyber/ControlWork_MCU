import sqlite3
import pika
import json
import time
import os

class DataSync:
    def __init__(self):
        self.db_path = '../data_receiver/sensor_data.db'
        self.rabbitmq_host = 'fly.rmq.cloudamqp.com'
        
    def connect_rabbitmq(self):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.rabbitmq_host)
            )
            channel = connection.channel()
            channel.queue_declare(queue='sensor_data')
            print("✅ Connected to RabbitMQ")
            return connection, channel
        except Exception as e:
            print(f"❌ RabbitMQ connection failed: {e}")
            return None, None
    
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
    
    def send_to_rabbitmq(self, channel, data):
        try:
            message = json.dumps(data, ensure_ascii=False, default=str)
            channel.basic_publish(
                exchange='',
                routing_key='sensor_data',
                body=message
            )
            print(f"📤 Sent to RabbitMQ: {data['device_id']}")
            return True
        except Exception as e:
            print(f"❌ Failed to send to RabbitMQ: {e}")
            return False
    
    def delete_synced_data(self, data_ids):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            placeholders = ','.join('?' * len(data_ids))
            cursor.execute(f'DELETE FROM sensor_data WHERE id IN ({placeholders})', data_ids)
            
            conn.commit()
            conn.close()
            print(f"🗑️ Deleted {len(data_ids)} synced records")
            return True
        except Exception as e:
            print(f"❌ Failed to delete data: {e}")
            return False
    
    def sync_data(self):
        print("🔄 Starting data synchronization...")
        
        connection, channel = self.connect_rabbitmq()
        if not connection:
            return
        
        data_to_sync = self.get_unsynced_data()
        
        if not data_to_sync:
            print("📭 No data to sync")
            connection.close()
            return
        
        print(f"📦 Found {len(data_to_sync)} records to sync")
        
        successful_ids = []
        failed_ids = []
        
        for record in data_to_sync:
            if self.send_to_rabbitmq(channel, record):
                successful_ids.append(record['id'])
            else:
                failed_ids.append(record['id'])
        
        if successful_ids:
            self.delete_synced_data(successful_ids)
        
        print(f"✅ Sync completed: {len(successful_ids)} successful, {len(failed_ids)} failed")
        connection.close()

def main():
    sync = DataSync()
    while True:
        sync.sync_data()
        print("⏰ Waiting 10 seconds...")
        time.sleep(10)

if __name__ == '__main__':
    main()