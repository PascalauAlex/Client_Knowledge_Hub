import io
import boto3
from boto3 import client
from botocore.exceptions import ClientError
from config import settings




def _get_s3_client():
    return boto3.client(
        service_name="s3",
        region_name=settings.s3_region,
        aws_access_key_id=(
            settings.s3_access_key_id.get_secret_value()
            if settings.s3_access_key_id
            else None
        ),
        aws_secret_access_key=(
            settings.s3_secret_access_key.get_secret_value()
            if settings.s3_secret_access_key
            else None
        ),
    )




def get_object(object_name : str):
    aws_client = _get_s3_client()
    bucket_object_name = f"files/{object_name}"
    try:
        response = aws_client.get_object(Bucket=settings.s3_bucket_name, Key=bucket_object_name)
        binary_data = response['Body'].read()


    except ClientError as err:
        error_code = err.response['Error']['Code']
        if error_code == 'NoSuchKey':
            print(f"File {bucket_object_name} was not found in the bucket {settings.s3_bucket_name}.")
        elif error_code == 'AccessDenied':
            print("Nu ai permisiuni suficiente pentru a citi acest fișier.")
            print("Not enought permissions to read this file")
        else:
            print(f"Unexpected error from AWS: {err}")
        return None
    return binary_data

