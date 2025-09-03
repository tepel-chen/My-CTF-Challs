from flask import Flask, render_template, request, redirect, url_for, session, g, flash
import sqlite3
import os

DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
SECRET_KEY = os.urandom(16).hex()
FLAG = os.environ.get('FLAG', 'fwectf{fake_flag}')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin_pass')
TEST_COUPON = os.environ.get('TEST_COUPON', 'test_coupon')

app = Flask(__name__)
app.secret_key = SECRET_KEY

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

db = sqlite3.connect(DATABASE)
c = db.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)''')
c.execute('''CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL
)''')
c.execute('''CREATE TABLE IF NOT EXISTS coupons (
    code TEXT PRIMARY KEY,
    used BOOLEAN NOT NULL
)''')
c.execute(f'''
    INSERT INTO users (username, password) VALUES ('admin', '{ADMIN_PASSWORD}')
''')
c.execute(f'''
    INSERT INTO coupons (code, used) VALUES ('{TEST_COUPON}', FALSE)
''')
items = [
    (1, "Baby Shark Plush", 1200),
    (2, "Shark Fin Hat", 900),
    (3, "Shark Tooth Necklace", 650),
    (4, "Mini Aquarium for Baby Sharks", 1500),
    (5, "Shark Food Pack (Seafood Mix)", 800),
    (6, "Shark Training Ball", 400),
    (7, "Shark Costume for Pets", 1100),
    (8, "Shark-Shaped Feeding Bowl", 500),
    (9, "Floating Shark Toy", 350),
    (10, "Shark-Safe Saltwater Conditioner", 700),
    (11, "Personalized Shark Collar", 650),
    (12, "Shark Patterned Towel", 600),
    (13, "Shark Tank Cleaning Kit", 950),
    (14, "Shark Birthday Party Set", 1300),
    (15, "Shark Health Check Guidebook", 550),
]
for item in items:
    c.execute("INSERT OR IGNORE INTO items (id, name, price) VALUES (?, ?, ?)", item)
db.commit()

@app.route("/")
def index():
    conn = get_db()
    items = conn.execute("SELECT * FROM items").fetchall()
    conn.close()
    return render_template("index.html", items=items)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        conn.close()
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/register")
def register():
    return "Under Construction"

@app.route("/item/<int:item_id>")
def item_detail(item_id):
    return "Under Construction"

@app.route("/coupon", methods=["GET", "POST"])
def coupon():
    result = None
    if request.method == "POST":
        code = request.form.get("coupon_code", "")
        conn = get_db()
        cur = conn.execute(f"SELECT * FROM coupons WHERE code = ?", (code,))
        coupon = cur.fetchone()
        conn.close()
        if coupon:
            result = "You can enter coupons after the official launch."
        else:
            result = "Invalid Coupon"
    return render_template("coupon.html", result=result)

@app.route("/admin")
def admin():
    if session.get("username") == "admin":
        import os
        flag = os.environ.get("FLAG", "fwectf{fake_flag}")
        return render_template("admin.html", flag=flag)
    else:
        from flask import abort
        abort(403)


if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)