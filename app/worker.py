import os
import json
import time
import redis
from dotenv import load_dotenv

load_dotenv()

# Initialize Redis
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
print(f"Connecting to Redis at: {redis_url}")
redis_client = redis.Redis.from_url(redis_url, decode_responses=True)

def process_push_notification(task_data):
    """Process a push notification task"""
    try:
        # Print push notification details
        print("\n=== Processing Push Notification ===")
        print(f"Message ID: {task_data.get('message_id')}")
        print(f"Device ID: {task_data.get('device_id')}")
        print(f"Platform: {task_data.get('platform')}")
        print(f"Title: {task_data.get('title')}")
        print(f"Body: {task_data.get('body')}")
        print(f"Category: {task_data.get('category')}")
        print("===================================\n")
        
        return {'status': 'success', 'task': task_data}
        
    except Exception as e:
        print(f"Error processing push: {str(e)}")
        return {'status': 'error', 'error': str(e)}

def main():
    print("Starting worker...")
    while True:
        try:
            # Get task from Redis list
            task_json = redis_client.rpop('push_tasks')
            if task_json:
                task_data = json.loads(task_json)
                process_push_notification(task_data)
            else:
                # No tasks, wait a bit before checking again
                time.sleep(1)
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            time.sleep(1)

if __name__ == '__main__':
    main() 