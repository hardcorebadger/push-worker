import asyncio
from uuid import uuid4
from aioapns import APNs, NotificationRequest, PushType


async def send_ios_push(device_token, title, body, action_url=None, category=None, apns_key_id=None, apns_team_id=None, apns_bundle_id=None, apns_private_key=None):
    """
    Send a push notification to an iOS device using APNS.
    Args:
        device_token (str): The device's push token
        title (str): Notification title
        body (str): Notification body
        category (str, optional): Notification category
        apns_key_id (str): APNs Key ID
        apns_team_id (str): APNs Team ID
        apns_bundle_id (str): App bundle ID (topic)
        apns_private_key (str): APNs .p8 private key contents
    """
    try:
        if not (apns_key_id and apns_team_id and apns_bundle_id and apns_private_key):
            return {'status': 'error', 'platform': 'ios', 'error': 'Missing APNs credentials'}


        apns_key_client = APNs(
            key=apns_private_key,
            key_id=apns_key_id,
            team_id=apns_team_id,
            topic=apns_bundle_id,  # Bundle ID
            use_sandbox=True,
        )

        request = NotificationRequest(
            device_token=device_token,
            message = {
                "aps": {
                    "alert": {
                        "title": title,
                        "body": body
                    },
                    "badge": "1",
                }, 
                "action_url": action_url
            },
            notification_id=str(uuid4()),  # optional
            time_to_live=3,                # optional
            push_type=PushType.ALERT,      # optional
        )

        result = await apns_key_client.send_notification(request)

        return {'status': 'success', 'result': result}

    except Exception as e:
        print(f"Error sending iOS push: {str(e)}")
        return {'status': 'error', 'platform': 'ios', 'error': str(e)} 