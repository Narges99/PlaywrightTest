import os
from datetime import datetime
from elasticsearch import Elasticsearch
from config import ELASTIC_URL, ELASTIC_INDEX, SYSTEMS

es = Elasticsearch([ELASTIC_URL])
ES_INDEX = ELASTIC_INDEX

def log_to_elasticsearch(doc: dict):

    doc["submitted_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    system_code = doc.get("system_code")
    doc["system_name"] = SYSTEMS.get(system_code, "unknown")
    try:
        es.index(index=ES_INDEX, document=doc)
    except Exception as e:
        print(f"❌ خطا در ارسال لاگ به Elasticsearch: {e}")


def _report(system_code: int, scenario: str, message: str, success: bool, step: str):
    print(message)
    log_to_elasticsearch({
        "system_code": system_code,
        "senario": scenario,
        "Description": message if success else f"{message} | Failed step: {step}",
        "status": success
    })
