from minio import Minio
import urllib3
import os
import logging

BUCKET_NAME = "dummybucket"
LOGGER = logging.Logger(__name__)

def _get_client() -> Minio:
    client = Minio(os.getenv("MINIO_ENDPOINT"), os.getenv("MINIO_ACCESS_KEY"), os.getenv("MINIO_SECRET_KEY"), secure=False)
    found = client.bucket_exists(BUCKET_NAME)
    if not found:
        client.make_bucket(BUCKET_NAME)
    return client


def list_objects() -> list[str]:
    client = _get_client()
    return [obj.object_name for obj in client.list_objects(BUCKET_NAME)]


def upload_object(file: object) -> None:
    client = _get_client()
    client.put_object(BUCKET_NAME, file.name, file, file.size)
    LOGGER.warning(f"Uploaded file {file.name}.")


def download_object(filename: str) -> object:
    try:
        client = _get_client()
        response = urllib3.response.HTTPResponse()
        response = client.get_object(BUCKET_NAME, filename)
        LOGGER.warning(f"Downloaded file {filename}.")
        return response.read()
    except Exception as e:
        LOGGER.error(f"Downloading object {filename} failed!")
    finally:
        response.close()
        response.release_conn()


def delete_object(filename: str) -> None:
    client = _get_client()
    client.remove_object(BUCKET_NAME,  filename)
