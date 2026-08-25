import logging as log
import requests as rq
from minio import Minio
from config import MINIO_ACCESS_KEY, MINIO_SECRET_KEY


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




