from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from services.supabase_service import db_supabase


manager = Blueprint(
    "manager",
    __name__,
    url_prefix="/manager"
)


def manager_only():
    return session.get("role") == "manager"


@manager.route("/review/<int:claim_id>", methods=["GET", "POST"])
def review(claim_id):

    if not manager_only():
        return "Access denied", 403

    try:

        # Get claim
        claim_response = (
            db_supabase
            .table("claims")
            .select("*")
            .eq("id", claim_id)
            .execute()
        )

        if not claim_response.data:
            return "Claim not found", 404

        expense_claim = claim_response.data[0]

        # Get employee
        profile_response = (
            db_supabase
            .table("profiles")
            .select("*")
            .eq("id", expense_claim["user_id"])
            .execute()
        )

        if not profile_response.data:
            return "Employee profile not found", 404

        employee = profile_response.data[0]

        # Manager can only review their team
        if employee.get("manager_id") != session["user_id"]:

            return """
            <h3>Access denied</h3>
            <a href="/manager/dashboard">← Back</a>
            """, 403

        # POST = approve/reject
        if request.method == "POST":

            action = request.form.get("action")

            print(
                "REVIEW:",
                claim_id,
                "ACTION:",
                action,
                "STATUS:",
                expense_claim["status"]
            )

            # Cannot process own claim
            if expense_claim["user_id"] == session["user_id"]:

                return render_template(
                    "manager/review.html",
                    claim=expense_claim,
                    employee=employee,
                    error="You cannot approve your own claim."
                )

            # Only pending claims can be processed
            if expense_claim["status"] != "pending":

                return render_template(
                    "manager/review.html",
                    claim=expense_claim,
                    employee=employee,
                    error=(
                        "This claim has already been "
                        + expense_claim["status"]
                        + "."
                    )
                )

            # APPROVE
            if action == "approve":

                update_response = (
                    db_supabase
                    .table("claims")
                    .update({
                        "status": "approved",
                        "approved_by": session["user_id"]
                    })
                    .eq("id", claim_id)
                    .eq("status", "pending")
                    .execute()
                )

                print(
                    "APPROVE RESULT:",
                    update_response.data
                )

            # REJECT
            elif action == "reject":

                update_response = (
                    db_supabase
                    .table("claims")
                    .update({
                        "status": "rejected"
                    })
                    .eq("id", claim_id)
                    .eq("status", "pending")
                    .execute()
                )

                print(
                    "REJECT RESULT:",
                    update_response.data
                )

            else:

                return render_template(
                    "manager/review.html",
                    claim=expense_claim,
                    employee=employee,
                    error="Invalid action."
                )

            # Go back to Manager Dashboard
            return redirect(
                url_for("manager_dashboard")
            )

        # GET
        return render_template(
            "manager/review.html",
            claim=expense_claim,
            employee=employee
        )

    except Exception as e:

        print("MANAGER REVIEW ERROR:", repr(e))

        return render_template(
            "manager/review.html",
            claim=expense_claim if "expense_claim" in locals() else {},
            employee=employee if "employee" in locals() else {},
            error=str(e)
        )