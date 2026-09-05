from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from services.supabase_service import (
    supabase,
    db_supabase
)


auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():

    # Already logged in
    if request.method == "GET" and "user_id" in session:

        role = session.get("role")

        if role == "employee":
            return redirect(
                url_for("employee_dashboard")
            )

        elif role == "manager":
            return redirect(
                url_for("manager_dashboard")
            )

        elif role == "finance":
            return redirect(
                url_for("finance_dashboard")
            )


    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        try:

            print("===== LOGIN =====")
            print("EMAIL:", email)

            # Authenticate with Supabase
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            user = response.user

            print("AUTH SUCCESS")
            print("USER ID:", user.id)


            # Get application profile
            profile_response = (
                db_supabase
                .table("profiles")
                .select("*")
                .eq("id", user.id)
                .execute()
            )

            print(
                "PROFILE:",
                profile_response.data
            )


            if not profile_response.data:

                return render_template(
                    "login.html",
                    error="Profile not found for this account."
                )


            profile = profile_response.data[0]


            # IMPORTANT:
            # Make Flask session permanent
            session.permanent = True

            # Store user information
            session["user_id"] = user.id
            session["email"] = user.email
            session["role"] = profile["role"]
            session["name"] = profile["name"]


            print(
                "SESSION CREATED:",
                dict(session)
            )


            # Redirect based on role

            if profile["role"] == "employee":

                return redirect(
                    url_for("employee_dashboard")
                )


            elif profile["role"] == "manager":

                return redirect(
                    url_for("manager_dashboard")
                )


            elif profile["role"] == "finance":

                return redirect(
                    url_for("finance_dashboard")
                )


            return render_template(
                "login.html",
                error="Invalid user role."
            )


        except Exception as e:

            print(
                "===== LOGIN ERROR ====="
            )

            print(
                repr(e)
            )

            return render_template(
                "login.html",
                error="Invalid email or password."
            )


    return render_template(
        "login.html"
    )


@auth.route("/logout")
def logout():

    print("LOGOUT")

    # Clear Flask session
    session.clear()

    return redirect(
        url_for("auth.login")
    )