import requests
from datetime import datetime
from config import ELASTIC_URL, ELASTIC_INDEX

def log_to_elasticsearch(data: dict):
    data["@timestamp"] = datetime.utcnow().isoformat()
    url = f"{ELASTIC_URL}/{ELASTIC_INDEX}/_doc"
    try:
        response = requests.post(url, json=data)
        print(f"Elasticsearch status: {response.status_code}")
    except Exception as e:
        print(f"Error sending to Elasticsearch: {e}")
