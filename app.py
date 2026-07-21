import os
import uuid

from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from config import DEPARTMENTS, YEARS, CATEGORIES

from helpers import login_required


# -----------------------------
# Flask App Configuration
# -----------------------------

app = Flask(__name__)

app.config["SECRET_KEY"] = "c0a8542471f4e513321481d2b238ce878d4a062707eca28435ad7729dccbf933"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)


# -----------------------------
# Upload Configuration
# -----------------------------

UPLOAD_FOLDER = "static/uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {
    "pdf",
    "png",
    "jpg",
    "jpeg"
}


# -----------------------------
# Database
# -----------------------------

db = SQL("sqlite:///database/notice.db")


# -----------------------------
# Default Admin
# -----------------------------

def create_default_admin():
    rows = db.execute(
        "SELECT * FROM users WHERE username = ?",
        "admin"
    )

    if len(rows) == 0:
        db.execute(
            """
            INSERT INTO users (username, hash, role)
            VALUES (?, ?, ?)
            """,
            "admin",
            generate_password_hash("admin123"),
            "admin"
        )


create_default_admin()


# -----------------------------
# Helper Functions
# -----------------------------

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# -----------------------------
# Routes
# -----------------------------

@app.route("/")
def index():

    search = request.args.get("search", "").strip()
    department = request.args.get("department", "")
    year = request.args.get("year", "")
    category = request.args.get("category", "")

    query = """
        SELECT *
        FROM notices
        WHERE 1=1
    """

    params = []

    if search:
        query += """
            AND (
                title LIKE ?
                OR description LIKE ?
                OR department LIKE ?
                OR year LIKE ?
                OR category LIKE ?
            )
        """

        params.extend([
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ])

    if department:
        query += " AND department = ?"
        params.append(department)

    if year:
        query += " AND year = ?"
        params.append(year)

    if category:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY created_at DESC"

    notices = db.execute(query, *params)

    print(notices)

    return render_template(
        "index.html",
        notices=notices,
        search=search,
        departments=DEPARTMENTS,
        years=YEARS,
        categories=CATEGORIES,
        selected_department=department,
        selected_year=year,
        selected_category=category
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Please provide username and password.", "danger")
            return redirect("/login")

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?",
            username
        )

    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
        flash("Invalid username or password.", "danger")
        return redirect("/login")

        session["user_id"] = rows[0]["id"]
        session["role"] = rows[0]["role"]

        return redirect("/dashboard")

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():

    notices = db.execute("""
        SELECT *
        FROM notices
        ORDER BY created_at DESC
    """)

    total_notices = len(notices)

    total_notices = db.execute(
        "SELECT COUNT(*) AS total FROM notices"
    )[0]["total"]

    departments = db.execute(
        "SELECT COUNT(DISTINCT department) AS total FROM notices"
    )[0]["total"]

    categories = db.execute(
        "SELECT COUNT(DISTINCT category) AS total FROM notices"
    )[0]["total"]

    return render_template(
        "dashboard.html",
        notices=notices,
        total_notices=total_notices,
        departments=departments,
        categories=categories
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# -----------------------------
# Add Notice
# -----------------------------

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():

    if request.method == "POST":

        title = request.form.get("title")
        description = request.form.get("description")
        department = request.form.get("department")
        year = request.form.get("year")
        category = request.form.get("category")

        attachment = request.files.get("attachment")
        filename = None

        if not title or not description or not department or not year or not category:
            flash("Please fill in all required fields.", "danger")
            return redirect("/add")

        if attachment and attachment.filename != "":

            if not allowed_file(attachment.filename):
                flash("Only PDF, PNG, JPG and JPEG files are allowed.", "danger")
                return redirect("/add")

            extension = attachment.filename.rsplit(".", 1)[1].lower()

            filename = f"{uuid.uuid4()}.{extension}"

            attachment.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        db.execute(
            """
            INSERT INTO notices
            (title, description, department, year, category, attachment, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            title,
            description,
            department,
            year,
            category,
            filename,
            session["user_id"]
        )

        flash("Notice added successfully!", "success")
        return redirect("/dashboard")

    return render_template(
        "add_notice.html",
        departments=DEPARTMENTS,
        years=YEARS,
        categories=CATEGORIES
)

@app.route("/edit/<int:notice_id>", methods=["GET", "POST"])
@login_required
def edit(notice_id):

    notice = db.execute(
        "SELECT * FROM notices WHERE id = ?",
        notice_id
    )

    if len(notice) != 1:
        return "Notice not found.", 404

    notice = notice[0]

    if request.method == "POST":

        title = request.form.get("title")
        description = request.form.get("description")
        department = request.form.get("department")
        year = request.form.get("year")
        category = request.form.get("category")

        attachment = request.files.get("attachment")

        filename = notice["attachment"]

        if not title or not description or not department or not year or not category:
            flash("Please fill in all required fields.", "danger")
            return redirect(f"/edit/{notice_id}")

        if attachment and attachment.filename != "":

            if not allowed_file(attachment.filename):
                flash("Only PDF, PNG, JPG and JPEG files are allowed.", "danger")
                return redirect(f"/edit/{notice_id}")

            if notice["attachment"]:

                old_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    notice["attachment"]
                )

                if os.path.exists(old_path):
                    os.remove(old_path)

            extension = attachment.filename.rsplit(".", 1)[1].lower()

            filename = f"{uuid.uuid4()}.{extension}"

            attachment.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        db.execute("""
            UPDATE notices
            SET
                title = ?,
                description = ?,
                department = ?,
                year = ?,
                category = ?,
                attachment = ?
            WHERE id = ?
        """,
        title,
        description,
        department,
        year,
        category,
        filename,
        notice_id
        )

        flash("Notice updated successfully!", "success")
        return redirect("/dashboard")

    return render_template(
        "edit_notice.html",
        notice=notice,
        departments=DEPARTMENTS,
        years=YEARS,
        categories=CATEGORIES
)


@app.route("/delete/<int:notice_id>", methods=["POST"])
@login_required
def delete(notice_id):

    notice = db.execute(
        "SELECT * FROM notices WHERE id = ?",
        notice_id
    )

    if len(notice) != 1:
        return "Notice not found.", 404

    notice = notice[0]

    if notice["attachment"]:

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            notice["attachment"]
        )

        if os.path.exists(filepath):
            os.remove(filepath)

    db.execute(
        "DELETE FROM notices WHERE id = ?",
        notice_id
    )

    flash("Notice deleted successfully!", "success")
    return redirect("/dashboard")


# -----------------------------
# Run Application
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)