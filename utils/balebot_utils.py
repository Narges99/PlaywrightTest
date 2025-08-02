import requests
from config import BALE_BOT_TOKEN, BALE_CHAT_ID

def send_message_to_bale(text: str , chatid:str = None):
    url = f"https://tapi.bale.ai/bot{BALE_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id":chatid or BALE_CHAT_ID,
        "text": text
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Bale response: {response.status_code}")
    except Exception as e:
        print(f"Error sending to Bale: {e}")