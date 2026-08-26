import json
import pandas as pd
import logging as log
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

def bucket_check(minio_bucket_name: str) -> None:
    """функция проверяет наличие bucket, проверяет наличие файлов внутри bucket"""

    try:
        if not minio_client.bucket_exists(minio_bucket_name):
            minio_client.make_bucket(minio_bucket_name)
            logger.info(f"Bucket создан: {minio_bucket_name}")
        else:
            logger.info(f"Bucket уже существует: {minio_bucket_name}")
    except Exception as e:
        logger.error(f"Ошибка создания {minio_bucket_name}: {e}")

    try:
        is_empty = not any(minio_client.list_objects(minio_bucket_name, recursive=True, max_keys=1))
        if is_empty:
            log.warning(f"minio bucket {minio_bucket_name} пуст")
        else:
            logger.info(f"minio bucket {minio_bucket_name} не пуст")
    except Exception as e:
        logger.error(f"ошибка minio bucket {minio_bucket_name}: {e}")


def get_json_files_from_minio(
        bucket_name: str,
        batch_size: int = 10
):
    """Получение JSON-файлов из MinIO батчами."""

    batch = []

    objects = minio_client.list_objects(
        bucket_name,
        recursive=True
    )

    for obj in objects:

        if not obj.object_name.endswith(".json"):
            continue

        try:
            response = minio_client.get_object(
                bucket_name,
                obj.object_name
            )

            data = json.loads(
                response.read().decode("utf-8")
            )

            batch.append(data)

            # Батч заполнен
            if len(batch) == batch_size:
                yield batch
                batch = []

        except Exception as e:
            log.error(
                f"ошибка чтения {obj.object_name}: {e}"
            )

    # Отдать последний неполный батч
    if batch:
        yield batch

# def validate_data(data: list[dict]) -> list[dict]:
#     """Валидация структуры и содержимого данных."""
#
#     validated_data = []
#
#     for record in data:
#
#         # Проверяем обязательные поля
#         # if "id" not in record:
#         #     continue
#
#         # Проверяем типы
#         # if not isinstance(record["id"], int):
#         #     continue
#
#         validated_data.append(record)
#
#     return validated_data
# def remove_nulls(data: list[dict]) -> list[dict]:
#     """Удаление записей/полей с NULL."""
#
#     cleaned_data = []
#
#     for record in data:
#
#         # Твоя логика обработки NULL
#         # например:
#         # if any(value is None for value in record.values()):
#         #     continue
#
#         cleaned_data.append(record)
#
#     return cleaned_data
# def remove_duplicates(data: list[dict]) -> list[dict]:
#     """Удаление дубликатов."""
#
#     # Временный вариант
#     unique_data = []
#
#     for record in data:
#         if record not in unique_data:
#             unique_data.append(record)
#
#     return unique_data
# def convert_types(data: list[dict]) -> list[dict]:
#     """Приведение данных к необходимым типам."""
#
#     for record in data:
#
#         # Пример:
#         # record["id"] = int(record["id"])
#         # record["price"] = float(record["price"])
#         # record["title"] = str(record["title"])
#
#         pass
#
#     return data
# def transform_data(data: list[dict]) -> pd.DataFrame:
#     """Основная функция трансформации."""
#
#     data = validate_data(data)
#
#     data = remove_nulls(data)
#
#     data = remove_duplicates(data)
#
#     data = convert_types(data)
#
#     df = pd.DataFrame(data)
#
#     return df

def transform_from_minio(bucket_name: str) -> pd.DataFrame:
    """Полный Transform pipeline."""

    for batch in get_json_files_from_minio(bucket_name):

        products =[]
        for response in batch:
            products.extend(response["products"])

        # # 2. Transform
        # transformed_data = transform_data(raw_data)

        # log.info(
        #     f"Transform completed. "
        #     f"Rows: {len(transformed_data)}"
        # )
        # вместо raw_data transformed_data
        df = pd.DataFrame(products)

        yield df



## TODO дописать функцию, которая сможет разворачивать вложенный JSON!!!!!!!!!!!!!!!!!!!!!!
## TODO дописать логику функций, которые занимаются фильтрацией и валидацией данных
## TODO обернуть всё в airflow, написать pytest, написать dockerfile