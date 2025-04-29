from firebase_admin import messaging, credentials, initialize_app, get_app
import os

def send_android_push(device_token, title, body, category=None, credentials_json=None):
    """
    Send a push notification to an Android device using Firebase Cloud Messaging.
    
    Args:
        device_token (str): The device's FCM token
        title (str): Notification title
        body (str): Notification body
        category (str, optional): Notification category
        credentials_json (dict, optional): FCM service account credentials as dict
    """
    try:
        if not credentials_json:
            return {'status': 'error', 'platform': 'android', 'error': "No credentials available"}

        # Use a unique app name per credentials to avoid duplicate initialization
        app_name = credentials_json.get('project_id', 'default')
        try:
            cred = credentials.Certificate(credentials_json)
            initialize_app(cred, name=app_name)
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
        response = messaging.send(message, app=get_app(app_name))
        
        return {'status': 'success', 'platform': 'android', 'message_id': response}
        
    except Exception as e:
        print(f"Error sending Android push: {str(e)}")
        return {'status': 'error', 'platform': 'android', 'error': str(e)} 