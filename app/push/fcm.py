from firebase_admin import messaging, credentials, initialize_app
import os

def send_android_push(device_token, title, body, category=None):
    """
    Send a push notification to an Android device using Firebase Cloud Messaging.
    
    Args:
        device_token (str): The device's FCM token
        title (str): Notification title
        body (str): Notification body
        category (str, optional): Notification category
    """
    try:
        # TODO: Get these from project settings in database
        cred_path = os.getenv('FCM_CRED_PATH', 'path/to/firebase-credentials.json')
        
        # Initialize Firebase if not already initialized
        try:
            cred = credentials.Certificate(cred_path)
            initialize_app(cred)
        except ValueError:
            # App already initialized
            pass
        
        # Create notification message
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data={
                'category': category or '',
                'click_action': 'FLUTTER_NOTIFICATION_CLICK'
            },
            token=device_token
        )
        
        # Send notification
        response = messaging.send(message)
        
        return {'status': 'success', 'platform': 'android', 'message_id': response}
        
    except Exception as e:
        print(f"Error sending Android push: {str(e)}")
        return {'status': 'error', 'platform': 'android', 'error': str(e)} 