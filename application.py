from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import boto3
import uuid

from s3_service import upload_image, generate_image_url
from matching import find_matches
from claims import create_claim


app = Flask(__name__)


# ============================================================
# Flask session security
# ============================================================

app.config["SECRET_KEY"] = "change-this-later"


# ============================================================
# AWS configuration
# ============================================================

AWS_REGION = "ap-southeast-2"

USERS_TABLE = "lostfound-users"
ITEMS_TABLE = "lostfound-items"
CLAIMS_TABLE = "lostfound-claims"


# ============================================================
# Connect to DynamoDB
# ============================================================

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION
)

users_table = dynamodb.Table(USERS_TABLE)
items_table = dynamodb.Table(ITEMS_TABLE)
claims_table = dynamodb.Table(CLAIMS_TABLE)


# ============================================================
# Home
# ============================================================

@app.route("/")
def home():

    return render_template("index.html")


# ============================================================
# Register
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if not name or not email or not password:
            return "All fields are required."

        if len(password) < 6:
            return "Password must be at least 6 characters."

        response = users_table.get_item(
            Key={
                "email": email
            }
        )

        if "Item" in response:
            return "An account with this email already exists."

        password_hash = generate_password_hash(password)

        users_table.put_item(
            Item={
                "email": email,
                "name": name,
                "password_hash": password_hash,
                "role": "user",
                "created_at": datetime.now(
                    timezone.utc
                ).isoformat()
            }
        )

        return redirect(
            url_for("login")
        )

    return render_template("register.html")


# ============================================================
# Login
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        response = users_table.get_item(
            Key={
                "email": email
            }
        )

        user = response.get("Item")

        if user and check_password_hash(
            user["password_hash"],
            password
        ):

            session["email"] = user["email"]

            session["name"] = user["name"]

            session["role"] = user.get(
                "role",
                "user"
            )

            return redirect(
                url_for("home")
            )

        return "Invalid email or password."

    return render_template("login.html")


# ============================================================
# Report Lost / Found Item
# ============================================================

@app.route("/report", methods=["GET", "POST"])
def report_item():

    if "email" not in session:
        return redirect(
            url_for("login")
        )

    default_type = request.args.get(
        "type",
        "LOST"
    ).upper()

    if default_type not in ["LOST", "FOUND"]:
        default_type = "LOST"

    if request.method == "POST":

        image = request.files.get("image")

        image_key = None

        if image and image.filename:

            try:

                image_key = upload_image(
                    image
                )

            except ValueError as error:

                return str(error)

            except Exception as error:

                print(
                    "Image upload error:",
                    error
                )

                return (
                    "There was a problem "
                    "uploading the image."
                )

        item_type = request.form["item_type"]

        name = request.form["name"].strip()

        category = request.form["category"].strip()

        description = request.form["description"].strip()

        location = request.form["location"].strip()

        date = request.form["date"]

        if not name or not category or not location or not date:

            return (
                "Please fill in all required fields."
            )

        if item_type not in ["LOST", "FOUND"]:

            return "Invalid item type."

        item_id = str(
            uuid.uuid4()
        )

        items_table.put_item(
            Item={

                "item_id": item_id,

                "reported_by": session["email"],

                "item_type": item_type,

                "name": name,

                "category": category,

                "description": description,

                "location": location,

                "date": date,

                "status": "Open",

                "image_key": image_key,

                "created_at": datetime.now(
                    timezone.utc
                ).isoformat()
            }
        )

        return redirect(
            url_for("home")
        )

    return render_template(
        "report.html",
        default_type=default_type
    )


# ============================================================
# Search Lost & Found Items
# ============================================================

@app.route("/search")
def search():

    keyword = request.args.get(
        "keyword",
        ""
    ).strip().lower()

    category = request.args.get(
        "category",
        ""
    ).strip()

    location = request.args.get(
        "location",
        ""
    ).strip().lower()

    item_type = request.args.get(
        "item_type",
        ""
    ).strip().upper()

    has_search = (
        bool(keyword)
        or bool(category)
        or bool(location)
        or bool(item_type)
    )

    if not has_search:

        return render_template(
            "search.html",
            items=[],
            keyword=keyword,
            category=category,
            location=location,
            item_type=item_type,
            has_search=False
        )

    response = items_table.scan()

    items = response.get(
        "Items",
        []
    )

    while "LastEvaluatedKey" in response:

        response = items_table.scan(
            ExclusiveStartKey=response[
                "LastEvaluatedKey"
            ]
        )

        items.extend(
            response.get(
                "Items",
                []
            )
        )

    filtered_items = []

    for item in items:

        item_name = item.get(
            "name",
            ""
        ).lower()

        item_category = item.get(
            "category",
            ""
        )

        item_location = item.get(
            "location",
            ""
        ).lower()

        item_item_type = item.get(
            "item_type",
            ""
        ).upper()

        if keyword:

            searchable_text = (
                item_name
                + " "
                + item.get(
                    "description",
                    ""
                ).lower()
            )

            if keyword not in searchable_text:
                continue

        if category and item_category != category:
            continue

        if location and location not in item_location:
            continue

        if item_type and item_item_type != item_type:
            continue

        filtered_items.append(item)

    filtered_items.sort(
        key=lambda item: item.get(
            "created_at",
            ""
        ),
        reverse=True
    )

    return render_template(
        "search.html",
        items=filtered_items,
        keyword=keyword,
        category=category,
        location=location,
        item_type=item_type,
        has_search=True
    )


# ============================================================
# Item Details + Possible Matches
# ============================================================

@app.route("/item/<item_id>")
def item_detail(item_id):

    response = items_table.get_item(
        Key={
            "item_id": item_id
        }
    )

    item = response.get(
        "Item"
    )

    if not item:

        return (
            "Item not found.",
            404
        )

    image_url = generate_image_url(
        item.get("image_key")
    )

    response = items_table.scan()

    all_items = response.get(
        "Items",
        []
    )

    while "LastEvaluatedKey" in response:

        response = items_table.scan(
            ExclusiveStartKey=response[
                "LastEvaluatedKey"
            ]
        )

        all_items.extend(
            response.get(
                "Items",
                []
            )
        )

    matches = find_matches(
        item,
        all_items,
        minimum_score=40
    )

    return render_template(
        "item_detail.html",
        item=item,
        image_url=image_url,
        matches=matches
    )


# ============================================================
# Submit Claim
# ============================================================

@app.route(
    "/claim/<item_id>",
    methods=["GET", "POST"]
)
def submit_claim(item_id):

    if "email" not in session:
        return redirect(
            url_for("login")
        )

    response = items_table.get_item(
        Key={
            "item_id": item_id
        }
    )

    item = response.get(
        "Item"
    )

    if not item:

        return (
            "Item not found.",
            404
        )

    if item.get("status") != "Open":

        return (
            "This item is not currently "
            "available for claims."
        )

    if request.method == "POST":

        message = request.form[
            "message"
        ].strip()

        if not message:

            return (
                "Please explain why you believe "
                "this item belongs to you."
            )

        if item.get("reported_by") == session["email"]:

            return (
                "You cannot submit a claim "
                "for your own report."
            )

        create_claim(
            item_id=item_id,
            claimant_email=session["email"],
            message=message
        )

        items_table.update_item(
            Key={
                "item_id": item_id
            },
            UpdateExpression=(
                "SET #status = :status"
            ),
            ExpressionAttributeNames={
                "#status": "status"
            },
            ExpressionAttributeValues={
                ":status": "Claim Pending"
            }
        )

        return redirect(
            url_for(
                "item_detail",
                item_id=item_id
            )
        )

    return render_template(
        "claim.html",
        item=item
    )


# ============================================================
# Admin Dashboard
# ============================================================

@app.route("/admin")
def admin_dashboard():

    if "email" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("role") != "admin":

        return (
            "Access denied. "
            "Administrator privileges are required.",
            403
        )

    response = claims_table.scan()

    claims = response.get(
        "Items",
        []
    )

    while "LastEvaluatedKey" in response:

        response = claims_table.scan(
            ExclusiveStartKey=response[
                "LastEvaluatedKey"
            ]
        )

        claims.extend(
            response.get(
                "Items",
                []
            )
        )

    for claim in claims:

        item_response = items_table.get_item(
            Key={
                "item_id": claim["item_id"]
            }
        )

        item = item_response.get(
            "Item"
        )

        if item:

            claim["item_name"] = item.get(
                "name",
                "Unknown"
            )

            claim["item_type"] = item.get(
                "item_type",
                "Unknown"
            )

            claim["category"] = item.get(
                "category",
                "Unknown"
            )

            claim["location"] = item.get(
                "location",
                "Unknown"
            )

            claim["date"] = item.get(
                "date",
                "Unknown"
            )

        else:

            claim["item_name"] = "Item not found"

            claim["item_type"] = "Unknown"

            claim["category"] = "Unknown"

            claim["location"] = "Unknown"

            claim["date"] = "Unknown"

    claims.sort(
        key=lambda claim: claim.get(
            "created_at",
            ""
        ),
        reverse=True
    )

    return render_template(
        "admin.html",
        claims=claims
    )


# ============================================================
# Approve Claim
# ============================================================

@app.route(
    "/admin/claim/<claim_id>/approve",
    methods=["POST"]
)
def approve_claim(claim_id):

    # User must be logged in
    if "email" not in session:
        return redirect(
            url_for("login")
        )

    # Only administrators can approve claims
    if session.get("role") != "admin":
        return (
            "Access denied. "
            "Administrator privileges are required.",
            403
        )

    # Get claim
    response = claims_table.get_item(
        Key={
            "claim_id": claim_id
        }
    )

    claim = response.get(
        "Item"
    )

    if not claim:
        return "Claim not found.", 404

    # Only pending claims can be approved
    if claim.get("status") != "Pending":
        return "This claim has already been processed."

    # Update claim status
    claims_table.update_item(
        Key={
            "claim_id": claim_id
        },
        UpdateExpression=(
            "SET #status = :status"
        ),
        ExpressionAttributeNames={
            "#status": "status"
        },
        ExpressionAttributeValues={
            ":status": "Approved"
        }
    )

    # Mark item as recovered
    items_table.update_item(
        Key={
            "item_id": claim["item_id"]
        },
        UpdateExpression=(
            "SET #status = :status"
        ),
        ExpressionAttributeNames={
            "#status": "status"
        },
        ExpressionAttributeValues={
            ":status": "Recovered"
        }
    )

    return redirect(
        url_for("admin_dashboard")
    )


# ============================================================
# Reject Claim
# ============================================================

@app.route(
    "/admin/claim/<claim_id>/reject",
    methods=["POST"]
)
def reject_claim(claim_id):

    # User must be logged in
    if "email" not in session:
        return redirect(
            url_for("login")
        )

    # Only administrators can reject claims
    if session.get("role") != "admin":
        return (
            "Access denied. "
            "Administrator privileges are required.",
            403
        )

    # Get claim
    response = claims_table.get_item(
        Key={
            "claim_id": claim_id
        }
    )

    claim = response.get(
        "Item"
    )

    if not claim:
        return "Claim not found.", 404

    # Only pending claims can be rejected
    if claim.get("status") != "Pending":
        return "This claim has already been processed."

    # Update claim status
    claims_table.update_item(
        Key={
            "claim_id": claim_id
        },
        UpdateExpression=(
            "SET #status = :status"
        ),
        ExpressionAttributeNames={
            "#status": "status"
        },
        ExpressionAttributeValues={
            ":status": "Rejected"
        }
    )

    # Return item to Open status
    items_table.update_item(
        Key={
            "item_id": claim["item_id"]
        },
        UpdateExpression=(
            "SET #status = :status"
        ),
        ExpressionAttributeNames={
            "#status": "status"
        },
        ExpressionAttributeValues={
            ":status": "Open"
        }
    )

    return redirect(
        url_for("admin_dashboard")
    )


# ============================================================
# Logout
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# ============================================================
# Run Flask application
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )