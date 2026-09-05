from flask import Flask, render_template, session, redirect, url_for
from datetime import timedelta

from config import SECRET_KEY
from routes.auth_routes import auth
from routes.claim_routes import claim
from routes.manager_routes import manager
from routes.finance_routes import finance
from services.supabase_service import db_supabase


app = Flask(__name__)

# Flask session configuration
app.secret_key = SECRET_KEY

app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Local development uses HTTP
app.config["SESSION_COOKIE_SECURE"] = False


# Register routes
app.register_blueprint(auth)
app.register_blueprint(claim)
app.register_blueprint(manager)
app.register_blueprint(finance)


@app.route("/")
def home():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    role = session.get("role")

    if role == "employee":
        return redirect(url_for("employee_dashboard"))

    elif role == "manager":
        return redirect(url_for("manager_dashboard"))

    elif role == "finance":
        return redirect(url_for("finance_dashboard"))

    return redirect(url_for("auth.login"))


# =========================
# EMPLOYEE DASHBOARD
# =========================

@app.route("/employee/dashboard")
def employee_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") not in ["employee", "manager"]:
        return "Access denied", 403

    response = (
        db_supabase
        .table("claims")
        .select("*")
        .eq("user_id", session["user_id"])
        .execute()
    )

    claims = response.data or []

    stats = {
        "total": len(claims),

        "pending": len([
            c for c in claims
            if c["status"] == "pending"
        ]),

        "approved": len([
            c for c in claims
            if c["status"] == "approved"
        ]),

        "paid": len([
            c for c in claims
            if c["status"] == "paid"
        ])
    }

    return render_template(
        "employee/dashboard.html",
        name=session.get("name"),
        stats=stats
    )


# =========================
# MANAGER DASHBOARD
# =========================

@app.route("/manager/dashboard")
def manager_dashboard():

    if session.get("role") != "manager":
        return redirect(url_for("auth.login"))

    manager_id = session["user_id"]

    # Get manager's team
    team_response = (
        db_supabase
        .table("profiles")
        .select("id,name,email")
        .eq("manager_id", manager_id)
        .execute()
    )

    team = team_response.data or []

    team_ids = [
        person["id"]
        for person in team
    ]

    claims = []

    if team_ids:

        claims_response = (
            db_supabase
            .table("claims")
            .select("*")
            .in_("user_id", team_ids)
            .order("id", desc=True)
            .execute()
        )

        claims = claims_response.data or []

    employee_map = {
        person["id"]: person["name"]
        for person in team
    }

    for c in claims:

        c["employee_name"] = employee_map.get(
            c["user_id"],
            "Unknown"
        )

    return render_template(
        "manager/dashboard.html",
        claims=claims,
        team=team,
        name=session.get("name")
    )


# =========================
# FINANCE DASHBOARD
# =========================

@app.route("/finance/dashboard")
def finance_dashboard():

    if session.get("role") != "finance":
        return redirect(url_for("auth.login"))

    response = (
        db_supabase
        .table("claims")
        .select("*")
        .eq("status", "approved")
        .order("created_at", desc=True)
        .execute()
    )

    claims = response.data or []

    # Get profile names
    profiles_response = (
        db_supabase
        .table("profiles")
        .select("id,name,email")
        .execute()
    )

    profiles = profiles_response.data or []

    profile_map = {
        p["id"]: p
        for p in profiles
    }

    for claim in claims:

        person = profile_map.get(
            claim["user_id"]
        )

        claim["employee_name"] = (
            person["name"]
            if person
            else "Unknown"
        )

    return render_template(
        "finance/dashboard.html",
        claims=claims,
        name=session.get("name")
    )


# =========================
# DATABASE TEST
# =========================

@app.route("/test-db")
def test_db():

    response = (
        db_supabase
        .table("profiles")
        .select("*")
        .execute()
    )

    return {
        "success": True,
        "profiles": response.data
    }


if __name__ == "__main__":
    app.run(debug=True)