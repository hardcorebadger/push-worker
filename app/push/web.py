from pywebpush import webpush, WebPushException
import os
import json
from sqlalchemy import delete
from dotenv import load_dotenv
from app.db.models import Device, Base
from app.database import engine

# Device deletion function
def delete_device(device_id):
    with engine.connect() as conn:
        conn.execute(
            delete(Device).where(
                Device.device_id == device_id
            )
        )
        conn.commit()

def send_web_push(subscription_info, title, body, icon=None, action_url=None, vapid_private_key=None, vapid_subject=None, device_id=None):
    """
    Send a push notification to a web browser using Web Push API.
    
    Args:
        subscription_info (dict): The subscription info from the browser
        title (str): Notification title
        body (str): Notification body
        category (str, optional): Notification category
        icon (str, optional): URL for the notification icon
        action_url (str, optional): URL to open when notification is clicked
        vapid_private_key (str, optional): VAPID private key
        vapid_subject (str, optional): VAPID subject (mailto or URL)
        device_id (str, optional): Device ID
        user_id (str, optional): User ID
        project_id (str, optional): Project ID
    """
    try:
        
        # Create notification payload
        payload = {
            'title': title,
            'body': body,
            'icon': icon,
            'action_url': action_url
        }
        
        # Convert payload to JSON string
        payload_json = json.dumps(payload)
        
        # VAPID claims - use the endpoint's origin as the audience
        vapid_claims = {
            "sub": vapid_subject,  # TODO: Get from project settings
        }
        
   
        # Send notification
        response = webpush(
            subscription_info=subscription_info,
            data=payload_json,
            vapid_private_key=vapid_private_key,
            vapid_claims=vapid_claims,
            content_encoding='aes128gcm'
        )
        
        return {'status': 'success', 'platform': 'web', 'response': response.status_code}
        
    except WebPushException as e:
        print(f"Error sending web push: {str(e)}")
        print(e.response.status_code)
        
        if e.response.status_code == 410 or e.response.status_code == 404:
            try:
                delete_device(device_id)
            except Exception as e:
                print(f"Error deleting device: device_id: {device_id}, user_id: {user_id}, project_id: {project_id}")

        return {'status': 'error', 'platform': 'web', 'error': str(e)} 