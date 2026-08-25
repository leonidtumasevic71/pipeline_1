import json
import logging as log
import requests as rq
from io import BytesIO
from datetime import datetime
from extract.extract import minio_client


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

