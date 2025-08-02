from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from utils.balebot_utils import send_message_to_bale
from config import ELASTIC_URL, ELASTIC_INDEX

es = Elasticsearch([ELASTIC_URL])
ES_INDEX = ELASTIC_INDEX

def get_data_from_elasticsearch():
    # زمان ۲۴ ساعت قبل
    twenty_four_hours_ago = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

    query = {
        "query": {
            "range": {
                "submitted_at": {
                    "gte": twenty_four_hours_ago,
                    "format": "yyyy-MM-dd HH:mm:ss"  # چون فیلد date نیست، باید فرمت مشخص کنیم
                }
            }
        },
        "aggs": {
            "systems": {
                "terms": {
                    "field": "system_name.keyword",  # گروه‌بندی بر اساس نام سامانه
                    "size": 10
                },
                "aggs": {
                    "fail_count": {
                        "filter": {
                            "term": {
                                "status": False  # چون status بولی است
                            }
                        }
                    }
                }
            }
        },
        "size": 0
    }

    response = es.search(index=ES_INDEX, body=query)
    return response['aggregations']['systems']['buckets']

def generate_report(aggregations):
    message = "📊 گزارش وضعیت سامانه‌ها در ۲۴ ساعت اخیر:\n\n"
    for system in aggregations:
        system_name = system['key']
        total_count = system['doc_count']
        fail_count = system['fail_count']['doc_count']
        success_count = total_count - fail_count

        message += f"🖥️ سامانه {system_name}\n"
        message += f"  کل تست‌ها: {total_count}\n"
        message += f"  موفق: {success_count}\n"
        message += f"  ناموفق: {fail_count}\n\n"

    return message

def main():
    aggregations = get_data_from_elasticsearch()
    message = generate_report(aggregations)
    print(message)
    send_message_to_bale(message)

if __name__ == "__main__":
    main()
