import os
import sqlite3
import secrets
from functools import wraps
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
INSTANCE_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FUBS_SECRET_KEY", "CHANGE-THIS-TO-A-LONG-RANDOM-SECRET")
app.config["DATABASE"] = str(INSTANCE_DIR / "fubs.db")
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "webp", "gif"}

BUSINESS = {
    "name": "Forward Universal Biz Solutions",
    "short": "FUBS",
    "phone": "+2349030877219",
    "phone_display": "+234 903 087 7219",
    "email": "forwardcopy@hotmail.com",
    "address": "10 Faith Avenue, Iju Ota, Ogun State, Nigeria",
    "cac": "8369912",
}

def get_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price TEXT DEFAULT '',
            description TEXT DEFAULT '',
            image TEXT DEFAULT '',
            featured INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT DEFAULT '',
            subject TEXT DEFAULT '',
            message TEXT NOT NULL,
            status TEXT DEFAULT 'New',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        admin_count = db.execute("SELECT COUNT(*) FROM admins").fetchone()[0]
        if admin_count == 0:
            username = os.environ.get("FUBS_ADMIN_USER", "admin")
            password = os.environ.get("FUBS_ADMIN_PASSWORD", "ChangeMe123!")
            db.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)",
                       (username, generate_password_hash(password)))
        product_count = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if product_count == 0:
            samples = [
                ("Solar & Electrical Accessories", "Electronics", "Request a quote", "Selected solar and electrical accessories sourced against customer specifications.", "", 1),
                ("Office & School Supplies", "Office Supplies", "Request a quote", "Stationery, office consumables and selected institutional supplies.", "", 1),
                ("Generator & Equipment Rentals", "Rentals", "Request availability", "Rental coordination for generators and selected work equipment through asset partners.", "", 1),
            ]
            db.executemany("INSERT INTO products (name, category, price, description, image, featured) VALUES (?, ?, ?, ?, ?, ?)", samples)

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin_id"):
            flash("Please sign in to access the management area.", "warning")
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

def save_upload(file):
    if not file or not file.filename:
        return ""
    if not allowed_file(file.filename):
        raise ValueError("Unsupported image format. Use PNG, JPG, JPEG, WEBP or GIF.")
    safe_name = secure_filename(file.filename)
    ext = safe_name.rsplit(".", 1)[1].lower()
    filename = f"{secrets.token_hex(12)}.{ext}"
    file.save(UPLOAD_DIR / filename)
    return filename

@app.context_processor
def inject_globals():
    return {"business": BUSINESS, "current_year": 2026}

@app.route("/")
def home():
    with get_db() as db:
        products = db.execute("SELECT * FROM products WHERE active=1 AND featured=1 ORDER BY created_at DESC LIMIT 6").fetchall()
    return render_template("index.html", products=products, page_title="Home")

@app.route("/about")
def about():
    return render_template("about.html", page_title="About FUBS")

@app.route("/rentals")
def rentals():
    return render_template("rentals.html", page_title="Rentals")

@app.route("/trade")
def trade():
    return render_template("trade.html", page_title="Import & Export")

@app.route("/financial-services")
def financial_services():
    return render_template("financial.html", page_title="Financial Services")

@app.route("/contracts")
def contracts():
    return render_template("contracts.html", page_title="General Contracts")

@app.route("/merchandise")
def merchandise():
    category = request.args.get("category", "").strip()
    search = request.args.get("q", "").strip()
    query = "SELECT * FROM products WHERE active=1"
    params = []
    if category:
        query += " AND category = ?"
        params.append(category)
    if search:
        query += " AND (name LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    query += " ORDER BY featured DESC, created_at DESC"
    with get_db() as db:
        products = db.execute(query, params).fetchall()
        categories = db.execute("SELECT DISTINCT category FROM products WHERE active=1 ORDER BY category").fetchall()
    return render_template("merchandise.html", products=products, categories=categories,
                           selected_category=category, search=search, page_title="Merchandise")

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    with get_db() as db:
        product = db.execute("SELECT * FROM products WHERE id=? AND active=1", (product_id,)).fetchone()
    if not product:
        abort(404)
    return render_template("product.html", product=product, page_title=product["name"])

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()
        if not name or not email or not message:
            flash("Please complete your name, email and message.", "danger")
        else:
            with get_db() as db:
                db.execute("""INSERT INTO enquiries (name,email,phone,subject,message)
                              VALUES (?,?,?,?,?)""", (name,email,phone,subject,message))
            flash("Thank you. Your enquiry has been received.", "success")
            return redirect(url_for("contact"))
    return render_template("contact.html", page_title="Contact")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with get_db() as db:
            admin = db.execute("SELECT * FROM admins WHERE username=?", (username,)).fetchone()
        if admin and check_password_hash(admin["password_hash"], password):
            session.clear()
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            return redirect(url_for("admin_dashboard"))
        flash("Incorrect username or password.", "danger")
    return render_template("admin_login.html", page_title="Admin Login")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("admin_login"))

@app.route("/admin")
@admin_required
def admin_dashboard():
    with get_db() as db:
        products = db.execute("SELECT * FROM products ORDER BY created_at DESC").fetchall()
        enquiries = db.execute("SELECT * FROM enquiries ORDER BY created_at DESC LIMIT 20").fetchall()
        total_products = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        total_enquiries = db.execute("SELECT COUNT(*) FROM enquiries").fetchone()[0]
    return render_template("admin_dashboard.html", products=products, enquiries=enquiries,
                           total_products=total_products, total_enquiries=total_enquiries,
                           page_title="Admin Dashboard")

@app.route("/admin/products/add", methods=["GET", "POST"])
@admin_required
def add_product():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        price = request.form.get("price", "").strip()
        description = request.form.get("description", "").strip()
        featured = 1 if request.form.get("featured") else 0
        if not name or not category:
            flash("Product name and category are required.", "danger")
            return render_template("product_form.html", product=None, page_title="Add Product")
        try:
            image = save_upload(request.files.get("image"))
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("product_form.html", product=None, page_title="Add Product")
        with get_db() as db:
            db.execute("""INSERT INTO products (name,category,price,description,image,featured)
                          VALUES (?,?,?,?,?,?)""", (name,category,price,description,image,featured))
        flash("Product added successfully.", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("product_form.html", product=None, page_title="Add Product")

@app.route("/admin/products/<int:product_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_product(product_id):
    with get_db() as db:
        product = db.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
    if not product:
        abort(404)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        price = request.form.get("price", "").strip()
        description = request.form.get("description", "").strip()
        featured = 1 if request.form.get("featured") else 0
        active = 1 if request.form.get("active") else 0
        image_name = product["image"]
        try:
            new_image = save_upload(request.files.get("image"))
            if new_image:
                image_name = new_image
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("product_form.html", product=product, page_title="Edit Product")
        with get_db() as db:
            db.execute("""UPDATE products SET name=?,category=?,price=?,description=?,image=?,featured=?,active=?
                          WHERE id=?""", (name,category,price,description,image_name,featured,active,product_id))
        flash("Product updated.", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("product_form.html", product=product, page_title="Edit Product")

@app.route("/admin/products/<int:product_id>/delete", methods=["POST"])
@admin_required
def delete_product(product_id):
    with get_db() as db:
        product = db.execute("SELECT image FROM products WHERE id=?", (product_id,)).fetchone()
        db.execute("DELETE FROM products WHERE id=?", (product_id,))
    if product and product["image"]:
        try:
            (UPLOAD_DIR / product["image"]).unlink(missing_ok=True)
        except OSError:
            pass
    flash("Product deleted.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/enquiries/<int:enquiry_id>/status", methods=["POST"])
@admin_required
def update_enquiry(enquiry_id):
    status = request.form.get("status", "New")
    if status not in {"New", "In progress", "Closed"}:
        abort(400)
    with get_db() as db:
        db.execute("UPDATE enquiries SET status=? WHERE id=?", (status,enquiry_id))
    flash("Enquiry status updated.", "success")
    return redirect(url_for("admin_dashboard"))

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html", page_title="Page Not Found"), 404

@app.errorhandler(413)
def too_large(error):
    flash("Image is too large. Maximum upload size is 5 MB.", "danger")
    return redirect(request.referrer or url_for("admin_dashboard"))

init_db()

if __name__ == "__main__":
    app.run(debug=True)
