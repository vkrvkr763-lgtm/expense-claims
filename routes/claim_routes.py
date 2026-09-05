from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify
)

from datetime import datetime

from services.supabase_service import db_supabase
from services.ai_service import extract_receipt
from services.duplicate_service import calculate_duplicate_score


claim = Blueprint("claim", __name__, url_prefix="/claims")


def employee_only():

    return (
        "user_id" in session
        and session.get("role") in ["employee", "manager"]
    )


@claim.route("/create", methods=["GET", "POST"])
def create_claim():

    if not employee_only():
        return redirect(url_for("auth.login"))

    if request.method == "GET":

        return render_template(
            "employee/create_claim.html",
            name=session.get("name")
        )

    try:

        amount = request.form.get("amount")
        expense_date = request.form.get("expense_date")
        merchant = request.form.get("merchant")
        category = request.form.get("category")
        description = request.form.get("description")

        if not amount or not expense_date or not merchant:

            return render_template(
                "employee/create_claim.html",
                error="Amount, date and merchant are required.",
                form=request.form
            )

        claim_data = {
            "user_id": session["user_id"],
            "amount": float(amount),
            "currency": "INR",
            "expense_date": expense_date,
            "merchant": merchant,
            "category": category,
            "description": description,
            "status": "pending"
        }

        # Get previous claims for duplicate detection
        previous = (
            db_supabase
            .table("claims")
            .select("*")
            .eq("user_id", session["user_id"])
            .execute()
        )

        highest_score = 0

        for old_claim in previous.data:

            score = calculate_duplicate_score(
                claim_data,
                old_claim
            )

            highest_score = max(highest_score, score)

        claim_data["duplicate_score"] = highest_score
        claim_data["duplicate_warning"] = highest_score >= 70

        # Upload receipt if supplied
        receipt = request.files.get("receipt")

        if receipt and receipt.filename:

            file_bytes = receipt.read()

            file_path = (
                f"{session['user_id']}/"
                f"{int(datetime.now().timestamp())}_"
                f"{receipt.filename}"
            )

            db_supabase.storage.from_("receipts").upload(
                file_path,
                file_bytes,
                {
                    "content-type": receipt.content_type,
                    "upsert": "false"
                }
            )

            claim_data["receipt_image_url"] = file_path

        response = (
            db_supabase
            .table("claims")
            .insert(claim_data)
            .execute()
        )

        return redirect(url_for("claim.my_claims"))

    except Exception as e:

        print("CREATE CLAIM ERROR:", repr(e))

        return render_template(
            "employee/create_claim.html",
            error=str(e),
            form=request.form
        )


@claim.route("/extract", methods=["POST"])
def extract():

    if not employee_only():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    text = data.get("text", "")

    result = extract_receipt(text)

    return jsonify(result)


@claim.route("/my")
def my_claims():

    if not employee_only():
        return redirect(url_for("auth.login"))

    try:

        response = (
            db_supabase
            .table("claims")
            .select("*")
            .eq("user_id", session["user_id"])
            .order("id", desc=True)
            .execute()
        )

        claims = response.data or []

        print("MY CLAIMS:", claims)

        return render_template(
            "employee/claims.html",
            claims=claims,
            name=session.get("name")
        )

    except Exception as e:

        print("MY CLAIMS ERROR:", repr(e))

        return render_template(
            "employee/claims.html",
            claims=[],
            name=session.get("name"),
            error=str(e)
        )