from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from datetime import datetime, date

from services.supabase_service import db_supabase


finance = Blueprint(
    "finance",
    __name__,
    url_prefix="/finance"
)


def finance_only():

    return session.get("role") == "finance"


@finance.route("/pay/<int:claim_id>", methods=["POST"])
def pay(claim_id):

    if not finance_only():
        return "Access denied", 403

    response = (
        db_supabase
        .table("claims")
        .select("*")
        .eq("id", claim_id)
        .execute()
    )

    if not response.data:
        return "Claim not found", 404

    expense_claim = response.data[0]

    # Only approved claims can be paid
    if expense_claim["status"] != "approved":

        return (
            "Only approved claims can be paid.",
            400
        )

    (
        db_supabase
        .table("claims")
        .update({
            "status": "paid",
            "paid_by": session["user_id"],
            "paid_at": datetime.utcnow().isoformat()
        })
        .eq("id", claim_id)
        .execute()
    )

    return redirect(
        url_for("finance_dashboard")
    )


@finance.route("/analytics")
def analytics():

    if not finance_only():
        return "Access denied", 403

    # Current month
    today = date.today()

    month_start = date(
        today.year,
        today.month,
        1
    ).isoformat()

    # Get claims from current month
    response = (
        db_supabase
        .table("claims")
        .select("*")
        .gte("expense_date", month_start)
        .in_("status", ["approved", "paid"])
        .execute()
    )

    claims = response.data

    # Get profiles
    profiles_response = (
        db_supabase
        .table("profiles")
        .select("*")
        .execute()
    )

    profiles = profiles_response.data

    profile_map = {
        p["id"]: p
        for p in profiles
    }

    by_person = {}
    by_category = {}

    for claim in claims:

        amount = float(claim["amount"])

        user_id = claim["user_id"]

        profile = profile_map.get(user_id)

        if profile:

            name = profile["name"]

        else:

            name = "Unknown"

        by_person[name] = (
            by_person.get(name, 0)
            + amount
        )

        category = claim.get(
            "category",
            "Other"
        )

        by_category[category] = (
            by_category.get(category, 0)
            + amount
        )

    # Limit analysis
    limit_analysis = []

    for profile in profiles:

        if profile["role"] not in [
            "employee",
            "manager"
        ]:
            continue

        name = profile["name"]

        spent = by_person.get(
            name,
            0
        )

        monthly_limit = profile.get(
            "monthly_limit"
        )

        if monthly_limit is not None:

            monthly_limit = float(
                monthly_limit
            )

            remaining = (
                monthly_limit - spent
            )

            over_limit = (
                spent > monthly_limit
            )

        else:

            remaining = None
            over_limit = False

        limit_analysis.append({
            "name": name,
            "spent": spent,
            "monthly_limit": monthly_limit,
            "remaining": remaining,
            "over_limit": over_limit
        })

    total_spend = sum(by_person.values())

    return render_template(
        "finance/analytics.html",
        by_person=by_person,
        by_category=by_category,
        limit_analysis=limit_analysis,
        total_spend=total_spend
    )