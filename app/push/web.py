from pywebpush import webpush, WebPushException
import os
import json

def send_web_push(subscription_info, title, body, category=None, vapid_private_key=None, vapid_subject=None):
    """
    Send a push notification to a web browser using Web Push API.
    
    Args:
        subscription_info (dict): The subscription info from the browser
        title (str): Notification title
        body (str): Notification body
        category (str, optional): Notification category
    """
    try:
        
        # Create notification payload
        payload = {
            'title': title,
            'body': body,
            'category': category
        }
        
        # Convert payload to JSON string
        payload_json = json.dumps(payload)
        
        # Get the endpoint from subscription info
        # endpoint = subscription_info.get('endpoint', '')
        
        # VAPID claims - use the endpoint's origin as the audience
        vapid_claims = {
            "sub": vapid_subject,  # TODO: Get from project settings
        }
        
        # print(f"Using VAPID claims: {vapid_claims}")

        print(f"subscription_info: {subscription_info}")
        print(f"payload_json: {payload_json}")
        print(f"vapid_private_key: {vapid_private_key}")
        print(f"vapid_claims: {vapid_claims}")
        
        # Send notification
        response = webpush(
            subscription_info=subscription_info,
            data=payload_json,
            vapid_private_key=vapid_private_key,
            vapid_claims=vapid_claims,
            content_encoding='aes128gcm'
        )

        print(f"Web push response: {response}")
        
        return {'status': 'success', 'platform': 'web', 'response': response.status_code}
        
    except WebPushException as e:
        print(f"Error sending web push: {str(e)}")
        return {'status': 'error', 'platform': 'web', 'error': str(e)} 