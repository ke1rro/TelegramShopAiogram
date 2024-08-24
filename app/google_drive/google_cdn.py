import io
import os

from google.cloud import storage

from app.logger.log_maker import logger

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'storage-key.json'


storage_client = storage.Client()
bucket_name = 'hokagedatabucket'
bucket = storage_client.bucket(bucket_name)


async def upload_photo(photo_bytes, photo_name):
    try:
        bucket = storage_client.bucket('hokagedatabucket')
        blob = bucket.blob(photo_name)
        blob.upload_from_file(io.BytesIO(photo_bytes), content_type='image/jpeg')
        return blob.name
    except Exception as e:
        print(e)
        return None


async def get_file_url(photo_name: str) -> str:
    try:
        bucket = storage_client.bucket('hokagedatabucket')
        blob = bucket.blob(photo_name)
        blob.make_public()
        url = blob.public_url
        return url
    except Exception as e:
        logger.error(e)
        return None


async def delete_file(photo_name: str) -> bool:
    try:
        bucket = storage_client.bucket('hokagedatabucket')
        blob = bucket.blob(photo_name)
        blob.delete()
        return True
    except Exception as e:
        logger.error(e)
        return False


async def delete_files(photo_names: list[str]) -> bool:
    try:
        bucket = storage_client.bucket('hokagedatabucket')
        for photo_name in photo_names:
            blob = bucket.blob(photo_name)
            blob.delete()
            logger.info(f'Deleted {photo_name}')
        return True
    except Exception as e:
        logger.error(e)
        return False