from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from utils.balebot_utils import send_message_to_bale
from config import ELASTIC_URL, ELASTIC_INDEX, Playwright_MANAGEMENT_BALE_CHAT_ID

es = Elasticsearch([ELASTIC_URL])
ES_INDEX = ELASTIC_INDEX
TIME_ZONE = "+03:30"


def get_data_from_elasticsearch():
    body = {
        "query": {
            "range": {
                "submitted_at": {
                    "gte": "now-24h",
                    "lt": "now",
                    "time_zone": "+03:30"
                }
            }
        },
        "aggs": {
            "systems": {
                "terms": {"field": "system_name", "size": 10},
                "aggs": {
                    "fail_count": {
                        "filter": {"term": {"status": False}}
                    }
                }
            }
        },
        "size": 0,
        "track_total_hits": False
    }

    es.indices.refresh(index=ES_INDEX, ignore_unavailable=True)

    resp = es.search(index=ES_INDEX, body=body, request_timeout=30)
    return resp.get("aggregations", {}).get("systems", {}).get("buckets", [])

def generate_report(aggregations):
    if not aggregations:
        return "📊 در ۲۴ ساعت اخیر داده‌ای یافت نشد."
    msg = "📊 گزارش وضعیت سامانه‌ها در ۲۴ ساعت اخیر:\n\n"
    for system in aggregations:
        total = system["doc_count"]
        fails = system["fail_count"]["doc_count"]
        success = total - fails
        msg += (
            f"🖥️ {system['key']}\n"
            f"  کل تست‌ها: {total}\n"
            f"  موفق: {success}\n"
            f"  ناموفق: {fails}\n\n"
        )
    return msg

def main():
    aggregations = get_data_from_elasticsearch()
    message = generate_report(aggregations)
    print(message)
    send_message_to_bale(message , Playwright_MANAGEMENT_BALE_CHAT_ID)

if __name__ == "__main__":
    main()