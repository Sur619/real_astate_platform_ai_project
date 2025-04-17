import boto3
from uuid import uuid4
from botocore.exceptions import NoCredentialsError
from configs.settings import Settings
from users.models import User


def is_in_group(user: User, group_name: str) -> bool:
    """
    Check if a user belongs to a specific group.

    Args:
        user: The user object to check
        group_name: The name of the group to check for

    Returns:
        bool: True if the user belongs to the group, False otherwise
    """
    return any(group.name == group_name for group in user.groups)


def is_admin(user: User) -> bool:
    """
    Check if a user has admin privileges.

    Args:
        user: The user object to check

    Returns:
        bool: True if the user is an admin, False otherwise
    """
    return is_in_group(user, "admin")


s3 = boto3.client(
    "s3",
    aws_access_key_id=Settings.aws_access_key,
    aws_secret_access_key=Settings.aws_secret_key,
    region_name=Settings.aws_region,
)


def upload_avatar_to_s3(file, filename: str) -> str:
    unique_name = f"{uuid4()}_{filename}"
    try:
        s3.upload_fileobj(file, Settings.aws_bucket_name, unique_name, ExtraArgs={"ACL": "public-read"})
        return f"https://{Settings.aws_bucket_name}.s3.amazonaws.com/{unique_name}"
    except NoCredentialsError:
        raise Exception("S3 credentials not found.")
