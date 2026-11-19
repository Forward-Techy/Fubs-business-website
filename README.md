# FUBS Professional Website

Responsive 10-page website and Flask product-management backend for Forward Universal Biz Solutions.

## Features
- 10 public pages: Home, About, Rentals, Trade, Financial Services, Contracts, Merchandise, Product Details, Contact and Admin Login.
- Responsive navigation and mobile layout.
- Animated scrolling announcement marquee with reduced-motion support.
- Product catalogue with search and category filtering.
- Flask + SQLite database.
- Admin dashboard to add, edit, feature, activate/deactivate and delete products.
- Product image upload (PNG/JPG/JPEG/WEBP/GIF, maximum 5 MB).
- Customer enquiry form and enquiry status management.

## Windows + VS Code quick start (important)

**Do not use VS Code Live Server or open a template HTML file directly.** This project is a Flask website: its templates contain Jinja expressions such as `{{ url_for(...) }}` and must be served by Flask. The stylesheet and JavaScript are linked in `templates/base.html`, which the other page templates inherit.

### Easiest method
1. Extract the entire ZIP into one folder, for example `C:\FUBS`. Do not move `templates` or `static` out of that folder.
2. Open that folder in VS Code using **File → Open Folder**.
3. Make sure Python 3.10+ is installed. In VS Code, install the Microsoft **Python** extension if needed.
4. In the VS Code Explorer, double-click `run_windows.bat` (or right-click it and choose **Open in File Explorer**, then double-click it). It creates a virtual environment, installs Flask dependencies, and starts the app.
5. Keep the black terminal window open and visit `http://127.0.0.1:5000` in Chrome or Edge.

### Run from the VS Code terminal instead
Open **Terminal → New Terminal** in the project folder, then run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py
```

If PowerShell blocks activation, use Command Prompt in VS Code and run `.venv\Scripts\activate.bat`, then install requirements and run `python run.py`.

### If CSS is still missing
- Confirm the file exists at `static\css\style.css` (not `templates\static` or `static\style.css`).
- Confirm `templates\base.html` contains `<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">`.
- Open `http://127.0.0.1:5000/static/css/style.css` in the browser. You should see CSS text, not a 404 page.
- Hard-refresh the site with `Ctrl+F5`.
- Make sure you opened `http://127.0.0.1:5000`, not a `file:///...` address or VS Code Live Server address.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create a virtual environment:
   - Windows: `py -m venv .venv` then `.venv\Scripts\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set a strong secret and admin password before running:
   - Windows PowerShell:
     `$env:FUBS_SECRET_KEY="replace-with-a-long-random-secret"`
     `$env:FUBS_ADMIN_USER="your-admin-name"`
     `$env:FUBS_ADMIN_PASSWORD="your-strong-password"`
   - macOS/Linux:
     `export FUBS_SECRET_KEY='replace-with-a-long-random-secret'`
     `export FUBS_ADMIN_USER='your-admin-name'`
     `export FUBS_ADMIN_PASSWORD='your-strong-password'`
6. Run: `python run.py`
7. Visit `http://127.0.0.1:5000`.
8. Admin login: `http://127.0.0.1:5000/admin/login`.

If environment variables are not set, development defaults are `admin` / `ChangeMe123!`. **Change these immediately. Do not deploy with defaults.**

## Database
SQLite database is created automatically at `instance/fubs.db`. It stores admins, products and enquiries. Back up this file regularly. For higher traffic or multi-user hosting, migrate to MySQL/PostgreSQL.

## Before public launch
- Add HTTPS and a production WSGI server (e.g. Gunicorn or Waitress); do not use Flask debug server in production.
- Set `FUBS_SECRET_KEY`, `FUBS_ADMIN_USER`, and `FUBS_ADMIN_PASSWORD` securely in hosting environment variables.
- Add CSRF protection (e.g. Flask-WTF), rate limiting, login throttling and admin password-change functionality before production.
- Configure backups, upload scanning and privacy/data-retention notices.
- Confirm all regulated activities and product claims are properly authorized. POS services must be through an approved principal. Do not advertise export certification unless obtained.
- Replace any sample products and confirm all public contact details.
- Choose/register a domain and point it to the hosting provider.

## Structure
- `app.py` — Flask routes, database and product CRUD.
- `run.py` — development entry point.
- `templates/` — 10 public/admin templates.
- `static/css/style.css` — responsive FUBS styling.
- `static/js/main.js` — interactions.
- `static/uploads/` — uploaded product images.
- `instance/fubs.db` — auto-created database.
