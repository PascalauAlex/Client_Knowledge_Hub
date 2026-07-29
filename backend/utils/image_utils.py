import uuid
from io import BytesIO

from PIL import Image, ImageOps

from pathlib import Path
import boto3
from  boto3 import client
from starlette.concurrency import run_in_threadpool
from botocore.exceptions import ClientError
from botocore.config import Config
from config import settings
import logging

BASE_DIR = Path(__file__).resolve().parent.parent
PROFILE_PICS_DIR = BASE_DIR / "static" / "profile_pics"


def _get_s3_client():
    return boto3.client(
        "s3",
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

def create_presigned_url(
        object_name, bucket_name = settings.s3_bucket_name, region_name = settings.s3_region, expiration =3600, response_type : str = "image/jpeg"
)->str | None:
    """Generate a presigned URL to share an S3 object

    :param response_type:
    :param bucket_name: string
    :param object_name: string
    :param region_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    s3_client = boto3.client(
        's3',
        region_name=region_name,
        aws_secret_access_key=(settings.s3_secret_access_key.get_secret_value()
                                   if settings.s3_secret_access_key
                                   else None),
        aws_access_key_id=(settings.s3_access_key_id.get_secret_value()
                           if settings.s3_secret_access_key
                           else None),
        config=Config(
            signature_version='s3v4',
            s3={'addressing_style': 'virtual'},
        ),
    )

    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name,
                    'Key': object_name,
                    'ResponseContentType':response_type
                    },
            ExpiresIn=expiration,
        )
    except ClientError as e:
        logging.error(e)
        return None

        # The response contains the presigned URL
    return response






def process_profile_image(content: bytes) -> tuple[bytes, str]:
    with Image.open(BytesIO(content)) as original:
        img = ImageOps.exif_transpose(original)

        img = ImageOps.fit(img, (300, 300), method=Image.Resampling.LANCZOS)

        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")

        filename = f"{uuid.uuid4().hex}.jpg"

        output = BytesIO()
        img.save(output, "JPEG", quality=85, optimize=True)
        output.seek(0)

    return output.read(), filename

def _upload_to_s3(file_bytes: bytes, key: str) -> None:
    s3 = _get_s3_client()
    s3.upload_fileobj(
        BytesIO(file_bytes),
        settings.s3_bucket_name,
        key,
        ExtraArgs={"ContentType": "image/jpeg"},
    )

def _delete_from_s3(key:str)->None:
    s3 = _get_s3_client()
    s3.delete_object(Bucket=settings.s3_bucket_name,Key=key)

#Wrappers for synchron functions to run async
async def upload_file_s3(file_bytes : bytes, filename:str)->None:
    key = f"files/{filename}"
    await run_in_threadpool(_upload_to_s3,file_bytes,key)


async def delete_document_s3(filename: str | None) -> None:
    if filename is None:
        return
    key = f"files/{filename}"
    await run_in_threadpool(_delete_from_s3,key)



