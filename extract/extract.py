import json
import logging as log
import requests as rq
from io import BytesIO
from datetime import datetime
from minio import Minio
from config import API_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY


logger = log.getLogger(__name__)
log.basicConfig(filename='/home/leonid/Рабочий стол/pipeline_1/logs/.log', level=log.INFO)

minio_client = Minio(
    'localhost:9000',
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

def init_minio_buckets(minio_client: str, buckets: list) -> None:
    """Create buckets"""
    for bucket in buckets:
        try:
            if not minio_client.bucket_exists(bucket):
                minio_client.make_bucket(bucket)
                logger.info(f"Bucket создан: {bucket}")
            else:
                logger.info(f"Bucket уже существует: {bucket}")
        except Exception as e:
            logger.error(f"Ошибка создания {bucket}: {e}")


def api_accessibility_check(api_url: str) -> rq.Response:
    """function that check API response status code"""

    response = rq.get(api_url)
    status_code = response.status_code

    if status_code >= 200 and status_code < 300:
        log.info(f"api accessibility check succeeded, code {status_code}")
    elif status_code >= 300 and status_code < 400:
        log.error(f"api accessibility check failed, code {status_code}")
    elif status_code >= 400 and status_code < 500:
        log.error(f"api accessibility check failed, code {status_code}")
    elif status_code >= 500 and status_code < 600:
        log.error(f"api accessibility check failed, code {status_code}")
    else:
        log.error(f"undefined code {status_code}")
    return response


def minio_export(minio_bucket_name: str, response: rq.Response) -> dict:
    """export JSON files into Mino Bucket"""

    try:
        if response.headers.get('Content-Type') == 'application/json':
            data = json.dumps(response.json()).encode('utf-8')
        else:
            data = response.text.encode('utf-8')

        object_name = f"response_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        minio_client.put_object(
            minio_bucket_name,
            object_name,
            BytesIO(data),
            len(data)
        )
        log.info(f"minio export succeeded, code {response.status_code}")
        return True
    except Exception as e:
        log.error(f"minio export failed, error: {e}")
        return False


init_minio_buckets(minio_client, ["products"])
response = api_accessibility_check(API_URL)
minio_export('products', response)
