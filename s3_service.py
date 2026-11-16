import boto3
import uuid
from botocore.exceptions import ClientError


AWS_REGION = "ap-southeast-2"

S3_BUCKET = "anushka-lostfound-983269768701-983269768701-ap-southeast-2-an"


s3 = boto3.client(
    "s3",
    region_name=AWS_REGION
)


def upload_image(file):
    """
    Upload an image to the private S3 bucket.
    Returns the S3 object key if successful.
    """

    if not file or not file.filename:
        return None

    filename = file.filename

    if "." not in filename:
        raise ValueError("Invalid image file.")

    extension = filename.rsplit(".", 1)[-1].lower()

    allowed_extensions = {
        "jpg",
        "jpeg",
        "png",
        "webp"
    }

    if extension not in allowed_extensions:
        raise ValueError(
            "Only JPG, JPEG, PNG and WEBP images are allowed."
        )

    object_key = f"item-images/{uuid.uuid4()}.{extension}"

    try:

        s3.upload_fileobj(
            file,
            S3_BUCKET,
            object_key,
            ExtraArgs={
                "ContentType": file.content_type
                or "application/octet-stream"
            }
        )

        return object_key

    except ClientError as error:

        print("S3 upload error:", error)

        raise


def generate_image_url(image_key):
    """
    Generate a temporary secure URL for a private S3 image.
    The URL expires after 1 hour.
    """

    if not image_key:
        return None

    try:

        url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": S3_BUCKET,
                "Key": image_key
            },
            ExpiresIn=3600
        )

        return url

    except ClientError as error:

        print("S3 URL generation error:", error)

        return None