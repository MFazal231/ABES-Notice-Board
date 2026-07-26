import os
import uuid
import cloudinary
import cloudinary.uploader
import humanize

from datetime import datetime, timezone
from dotenv import load_dotenv
from cloudinary.utils import cloudinary_url
from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from config import DEPARTMENTS, YEARS, CATEGORIES
from helpers import admin_required, login_required

load_dotenv()

# Cloudinary Credentials

cloudinary._config.update(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

# Admin Credentials

DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD")

# -----------------------------
# Flask App Configuration
# -----------------------------

app = Flask(__name__)

import os

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "development-secret")
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

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

db = SQL(DATABASE_URL)


# -----------------------------
# Default Admin
# -----------------------------

def create_default_admin():
    rows = db.execute(
        "SELECT * FROM users WHERE username = :username",
        username=DEFAULT_ADMIN_USERNAME
    )

    if len(rows) == 0:
        db.execute(
            """
            INSERT INTO users (username, hash, role)
            VALUES (:username, :hash, :role)
            """,
            username=DEFAULT_ADMIN_USERNAME,
            hash=generate_password_hash(DEFAULT_ADMIN_PASSWORD),
            role="admin"
        )

        print("✅ Default admin created.")
    else:
        print("ℹ️ Default admin already exists.")



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

    params = {}

    if search:
        query += """
            AND (
                title ILIKE :search
                OR description ILIKE :search
                OR department ILIKE :search
                OR year ILIKE :search
                OR category ILIKE :search
            )
        """

        params["search"] = f"%{search}%"

    if department:
        query += " AND department = :department"
        params["department"] = department

    if year:
        query += " AND year = :year"
        params["year"] = year

    if category:
        query += " AND category = :category"
        params["category"] = category

    query += " ORDER BY pinned DESC, created_at DESC"

    notices = db.execute(query, **params)

    formatted_notices = []

    for notice in notices:
        new_notice = dict(notice)

        new_notice["time_ago"] = humanize.naturaltime(
            datetime.now() - new_notice["created_at"]
        )

        formatted_notices.append(new_notice)

    return render_template(
        "index.html",
        notices=formatted_notices,
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

    if request.method == "POST":

        session.clear()

        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Please provide username and password.", "danger")
            return redirect("/login")

        rows = db.execute(
            "SELECT * FROM users WHERE username = :username",
            username=username
        )

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Invalid username or password.", "danger")
            return redirect("/login")

        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        session["role"] = rows[0]["role"]

        flash("Welcome back!", "success")
        return redirect("/dashboard")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    # Get form data
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    # Validate username
    if not username:
        flash("Username is required.", "danger")
        return redirect("/register")

    # Validate password
    if not password:
        flash("Password is required.", "danger")
        return redirect("/register")

    # Validate confirmation
    if not confirmation:
        flash("Please confirm your password.", "danger")
        return redirect("/register")

    # Check passwords match
    if password != confirmation:
        flash("Passwords do not match.", "danger")
        return redirect("/register")

    # Check if username already exists
    existing_user = db.execute(
        "SELECT * FROM users WHERE username = :username",
        username=username
    )

    if existing_user:
        flash("Username already exists.", "danger")
        return redirect("/register")

    # Hash password
    hash = generate_password_hash(password)

    # Insert user
    db.execute(
        """
        INSERT INTO users (username, hash, role)
        VALUES (:username, :hash, :role)
        """,
        username=username,
        hash=hash,
        role="student"
    )

    flash("Registration successful! Please log in.", "success")

    return redirect("/login")


@app.route("/dashboard")
@login_required
@admin_required
def dashboard():

    per_page = 10

    page = request.args.get("page", 1, type=int)

    offset = (page - 1) * per_page

    notices = db.execute("""
        SELECT *
        FROM notices
        ORDER BY pinned DESC, created_at DESC
        LIMIT :limit OFFSET :offset
    """,
    limit=per_page,
    offset=offset
    )

    for notice in notices:
        notice["time_ago"] = humanize.naturaltime(
            datetime.now() - notice["created_at"]
    )

    total = db.execute(
        "SELECT COUNT(*) AS total FROM notices"
    )[0]["total"]

    total_pages = (total + per_page - 1) // per_page

    total_notices = db.execute(
        "SELECT COUNT(*) AS total FROM notices"
    )[0]["total"]

    departments = db.execute(
        "SELECT COUNT(DISTINCT department) AS total FROM notices"
    )[0]["total"]

    categories = db.execute(
        "SELECT COUNT(DISTINCT category) AS total FROM notices"
    )[0]["total"]

    category_stats = db.execute("""
        SELECT category, COUNT(*) AS total
        FROM notices
        GROUP BY category
    """)

    department_stats = db.execute("""
        SELECT department, COUNT(*) AS total
        FROM notices
        GROUP BY department
    """)

    # Pinned notices
    pinned_notices = db.execute(
        "SELECT COUNT(*) AS total FROM notices WHERE pinned = TRUE"
    )[0]["total"]

    # Notices with attachments
    attachment_notices = db.execute(
        "SELECT COUNT(*) AS total FROM notices WHERE attachment IS NOT NULL AND attachment != ''"
    )[0]["total"]

    # Notices added today
    today_notices = db.execute("""
        SELECT COUNT(*) AS total
        FROM notices
        WHERE DATE(created_at) = CURRENT_DATE
    """)[0]["total"]

    return render_template(
        "dashboard.html",
        notices=notices,
        total_notices=total_notices,
        departments=departments,
        categories=categories,
        category_stats=category_stats,
        department_stats=department_stats,
        page=page,
        total_pages=total_pages,
        pinned_notices=pinned_notices,
        attachment_notices=attachment_notices,
        today_notices=today_notices
    )


@app.route("/logout")
def logout():

    session.clear()
    flash("You have been logged out.", "info")
    return redirect("/login")


# -----------------------------
# Add Notice
# -----------------------------

@app.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add():

    if request.method == "POST":

        title = request.form.get("title")
        description = request.form.get("description")
        department = request.form.get("department")
        year = request.form.get("year")
        category = request.form.get("category")
        pinned = bool(request.form.get("pinned"))

        attachment = request.files.get("attachment")
        filename = None

        if not title or not description or not department or not year or not category:
            flash("Please fill in all required fields.", "danger")
            return redirect("/add")

        if attachment and attachment.filename != "":

            if not allowed_file(attachment.filename):
                flash("Only PDF, PNG, JPG and JPEG files are allowed.", "danger")
                return redirect("/add")          

            result = cloudinary.uploader.upload(
                attachment,
                resource_type="auto",
                folder="abes_notice_board",
            )

            filename = result["secure_url"]

        db.execute(
            """
            INSERT INTO notices
            (title, description, department, year, category, attachment, pinned, created_by)
            VALUES (
            :title,
            :description,
            :department,
            :year,
            :category,
            :attachment,
            :pinned,
            :created_by
            )
            """,
            title=title,
            description=description,
            department=department,
            year=year,
            category=category,
            attachment=filename,
            pinned=pinned,
            created_by=session["user_id"]
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
@admin_required
def edit(notice_id):

    notice = db.execute(
        "SELECT * FROM notices WHERE id = :id",
        id=notice_id
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

            result = cloudinary.uploader.upload(
                attachment,
                resource_type="auto",
                folder="abes_notice_board"
            )

            filename = result["secure_url"]

        db.execute("""
            UPDATE notices
            SET
                title = :title,
                description = :description,
                department = :department,
                year = :year,
                category = :category,
                attachment = :attachment
            WHERE id = :id
        """,
        title=title,
        description=description,
        department=department,
        year=year,
        category=category,
        attachment=filename,
        id=notice_id
        )

        flash("Notice updated successfully!", "info")
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
@admin_required
def delete(notice_id):

    notice = db.execute(
        "SELECT * FROM notices WHERE id = :id",
        id=notice_id
    )

    if len(notice) != 1:
        return "Notice not found.", 404

    notice = notice[0]

    db.execute(
        "DELETE FROM notices WHERE id = :id",
        id=notice_id
    )

    flash("Notice deleted successfully!", "warning")
    return redirect("/dashboard")


@app.route("/notice/<int:notice_id>")
def notice(notice_id):

    notice = db.execute(
        "SELECT * FROM notices WHERE id = :id",
        id=notice_id
    )

    if len(notice) != 1:
        return "Notice not found.", 404

    return render_template(
        "notice.html",
        notice=notice[0]
    )

@app.route("/toggle-pin/<int:notice_id>", methods=["POST"])
@login_required
@admin_required
def toggle_pin(notice_id):

    notice = db.execute(
        "SELECT pinned FROM notices WHERE id = :id",
        id=notice_id
    )

    if len(notice) != 1:
        flash("Notice not found.", "danger")
        return redirect("/dashboard")

    new_status = 0 if notice[0]["pinned"] else 1

    db.execute(
        "UPDATE notices SET pinned = :pinned WHERE id = :id",
        pinned=bool(new_status),
        id=notice_id
    )

    flash("Pin status updated!", "success")

    return redirect("/dashboard")


# -----------------------------
# Error Handlers
# -----------------------------

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

# -----------------------------
# Run Application
# -----------------------------

if __name__ == "__main__":
    app.run()