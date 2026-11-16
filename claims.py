import boto3
import uuid
from datetime import datetime, timezone


# ============================================================
# AWS configuration
# ============================================================

AWS_REGION = "ap-southeast-2"

CLAIMS_TABLE = "lostfound-claims"


# ============================================================
# Connect to DynamoDB
# ============================================================

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION
)

claims_table = dynamodb.Table(
    CLAIMS_TABLE
)


# ============================================================
# Create a new claim
# ============================================================

def create_claim(
    item_id,
    claimant_email,
    message
):
    """
    Create a new claim for an item.

    New claims start with the status:
    Pending
    """

    claim_id = str(
        uuid.uuid4()
    )

    claims_table.put_item(
        Item={

            "claim_id": claim_id,

            "item_id": item_id,

            "claimant_email": claimant_email,

            "message": message,

            "status": "Pending",

            "created_at": datetime.now(
                timezone.utc
            ).isoformat()
        }
    )

    return claim_id