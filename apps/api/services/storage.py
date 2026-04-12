import os
from pathlib import Path

from config import settings

# Local storage directory (used when MinIO is not available)
LOCAL_STORAGE_DIR = Path(settings.local_storage_path)


def _use_local() -> bool:
    """Use local filesystem when MinIO endpoint is not reachable."""
    return settings.storage_backend == "local"


async def upload_to_minio(object_key: str, content: bytes):
    """Upload file content to storage."""
    if _use_local():
        file_path = LOCAL_STORAGE_DIR / object_key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(content)
        return

    import io
    import boto3
    from botocore.config import Config as BotoConfig

    client = boto3.client(
        "s3",
        endpoint_url=f"{'https' if settings.minio_use_ssl else 'http'}://{settings.minio_endpoint}",
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        config=BotoConfig(signature_version="s3v4"),
        region_name="us-east-1",
    )
    client.put_object(
        Bucket=settings.minio_bucket,
        Key=object_key,
        Body=io.BytesIO(content),
        ContentLength=len(content),
    )


async def get_download_url(prefix: str) -> str:
    """Get a download URL for model files."""
    if _use_local():
        # Find first file under the prefix
        base = LOCAL_STORAGE_DIR / prefix
        if base.is_dir():
            for f in base.iterdir():
                if f.is_file():
                    return f"/api/v1/files/{prefix}{f.name}"
        return ""

    import boto3
    from botocore.config import Config as BotoConfig

    client = boto3.client(
        "s3",
        endpoint_url=f"{'https' if settings.minio_use_ssl else 'http'}://{settings.minio_endpoint}",
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        config=BotoConfig(signature_version="s3v4"),
        region_name="us-east-1",
    )
    response = client.list_objects_v2(Bucket=settings.minio_bucket, Prefix=prefix, MaxKeys=1)
    contents = response.get("Contents", [])
    if not contents:
        return ""
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.minio_bucket, "Key": contents[0]["Key"]},
        ExpiresIn=3600,
    )


async def delete_from_minio(prefix: str):
    """Delete all objects under a prefix."""
    if _use_local():
        import shutil
        path = LOCAL_STORAGE_DIR / prefix
        if path.exists():
            shutil.rmtree(path)
        return

    import boto3
    from botocore.config import Config as BotoConfig

    client = boto3.client(
        "s3",
        endpoint_url=f"{'https' if settings.minio_use_ssl else 'http'}://{settings.minio_endpoint}",
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        config=BotoConfig(signature_version="s3v4"),
        region_name="us-east-1",
    )
    response = client.list_objects_v2(Bucket=settings.minio_bucket, Prefix=prefix)
    for obj in response.get("Contents", []):
        client.delete_object(Bucket=settings.minio_bucket, Key=obj["Key"])
