# aws_service.py
import boto3
from botocore.exceptions import NoCredentialsError, ClientError, BotoCoreError
from uuid import uuid4
from configs.settings import settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region,
)


def upload_avatar_to_s3(file_data: bytes, content_type: str, filename: str = None) -> str:
    if not filename:
        filename = f"{uuid4()}.jpg"

    s3_key = f"{settings.aws_avatar_folder}/{filename}"

    try:
        s3_client.put_object(
            Bucket=settings.aws_bucket_name,
            Key=s3_key,
            Body=file_data,
            ContentType=content_type,
            ACL="public-read"
        )
    except NoCredentialsError:
        raise RuntimeError("AWS credentials not found")

    return f"https://fake-bucket.s3.amazonaws.com/{filename}"


class AWSS3Service:
    @staticmethod
    async def upload_file(key: str, content: bytes) -> str:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )

        try:
            s3.put_object(
                Bucket=settings.aws_bucket_name,
                Key=key,
                Body=content,
                ContentType="image/jpeg",
            )
            url = f"https://{settings.aws_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{key}"
            return url
        except (BotoCoreError, ClientError) as e:
            raise Exception(f"Failed to upload file: {e}")
