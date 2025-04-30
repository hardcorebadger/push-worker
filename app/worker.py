import os
import json
import time
import redis
import traceback
from dotenv import load_dotenv
from app.push import send_ios_push, send_android_push, send_web_push
import asyncio
from cryptography.fernet import Fernet

load_dotenv()

# Initialize Redis and Fernet
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
print(f"Connecting to Redis at: {redis_url}")
redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
fernet = Fernet(ENCRYPTION_KEY) if ENCRYPTION_KEY else None

def decrypt_value(value):
    """Decrypt an encrypted value using Fernet"""
    if not value or not fernet:
        return value
    try:
        return fernet.decrypt(value.encode()).decode()
    except Exception as e:
        print(f"Error decrypting value: {e}")
        return None


async def process_push_notification(task_data):
    """Process a push notification task"""
    try:
        # Print push notification details
        print(f"Pushing to {task_data.get('platform')}...")

        # Decrypt sensitive credentials
        apns_private_key = decrypt_value(task_data.get('apns_private_key'))
        fcm_credentials_json = decrypt_value(task_data.get('fcm_credentials_json'))
        vapid_private_key = decrypt_value(task_data.get('vapid_private_key'))
        
        # Send push based on platform
        if task_data.get("platform") == 'ios':
            result = await send_ios_push(
                device_token=task_data.get('token'),
                title=task_data.get('title'),
                body=task_data.get('body'),
                action_url=task_data.get('action_url'),
                apns_key_id=task_data.get('apns_key_id'),
                apns_team_id=task_data.get('apns_team_id'),
                apns_bundle_id=task_data.get('apns_bundle_id'),
                apns_private_key=apns_private_key
            )
        elif task_data.get("platform") == 'android':
            credentials_json = None
            if fcm_credentials_json:
                try:
                    credentials_json = json.loads(fcm_credentials_json)
                except Exception as e:
                    print(f"Error parsing fcm_credentials_json: {e}")
            result = send_android_push(
                device_token=task_data.get("token"),
                title=task_data.get('title'),
                body=task_data.get('body'),
                action_url=task_data.get('action_url'),
                credentials_json=credentials_json
            )
        elif task_data.get("platform") == 'web':
            result = send_web_push(
                subscription_info=json.loads(task_data.get("token")),
                title=task_data.get('title'),
                body=task_data.get('body'),
                icon=task_data.get('icon'),
                action_url=task_data.get('action_url'),
                vapid_private_key=vapid_private_key,
                vapid_subject=task_data.get('vapid_subject'),
                device_id=task_data.get('device_id')
            )
        else:
            result = {'status': 'error', 'error': f'Unknown platform: {task_data.get("platform")}'}
        
        print(f"Push result: {result}")
        return result
        
    except Exception as e:
        print(f"Error processing push: {str(e)}")
        print("\nStack trace:")
        traceback.print_exc()
        return {'status': 'error', 'error': str(e)}

async def main():
    print("Starting worker...")
    while True:
        try:
            # Get task from Redis list
            task_json = redis_client.rpop('push_tasks')
            if task_json:
                task_data = json.loads(task_json)
                result = await process_push_notification(task_data)
                print(result)
            else:
                # No tasks, wait a bit before checking again
                time.sleep(1)
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            print("\nStack trace:")
            traceback.print_exc()
            time.sleep(1)
