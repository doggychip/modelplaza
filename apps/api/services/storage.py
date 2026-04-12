import io

import boto3
from botocore.config import Config as BotoConfig

from config import settings


def _get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=f"{'https' if settings.minio_use_ssl else 'http'}://{settings.minio_endpoint}",
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        config=BotoConfig(signature_version="s3v4"),
        region_name="us-east-1",
    )


async def upload_to_minio(object_key: str, content: bytes):
    """Upload file content to MinIO."""
    client = _get_s3_client()
    client.put_object(
        Bucket=settings.minio_bucket,
        Key=object_key,
        Body=io.BytesIO(content),
        ContentLength=len(content),
    )


async def get_download_url(prefix: str) -> str:
    """Generate a presigned download URL for model files."""
    client = _get_s3_client()

    # List objects under the prefix and return URL for the first one
    response = client.list_objects_v2(Bucket=settings.minio_bucket, Prefix=prefix, MaxKeys=1)
    contents = response.get("Contents", [])
    if not contents:
        return ""

    url = client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.minio_bucket, "Key": contents[0]["Key"]},
        ExpiresIn=3600,
    )
    return url


async def delete_from_minio(prefix: str):
    """Delete all objects under a prefix."""
    client = _get_s3_client()
    response = client.list_objects_v2(Bucket=settings.minio_bucket, Prefix=prefix)
    for obj in response.get("Contents", []):
        client.delete_object(Bucket=settings.minio_bucket, Key=obj["Key"])
