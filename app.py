from flask import Flask, render_template, request, redirect, url_for, session
import os
import sqlite3
from datetime import datetime
import qrcode
import random

app = Flask(__name__)
app.secret_key = "secret_key_here"

# Ensure folders exist
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("static/qr", exist_ok=True)

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cert_id TEXT,
                    image_path TEXT,
                    centering INTEGER,
                    corners INTEGER,
                    edges INTEGER,
                    surface INTEGER,
                    final_grade REAL,
                    label TEXT,
                    qr_path TEXT,
                    timestamp TEXT
                )""")
    conn.commit()
    conn.close()

def calculate_grade(c, co, e, s):
    return round((c + co + e + s) / 4, 1)

def label_from_grade(g):
    if g == 10:
        return "GEM MINT 10"
    elif g >= 9.5:
        return "MINT+"
    elif g >= 9:
        return "MINT"
    elif g >= 8:
        return "NM-MT"
    else:
        return "RAW"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["card_image"]
        centering = int(request.form["centering"])
        corners = int(request.form["corners"])
        edges = int(request.form["edges"])
        surface = int(request.form["surface"])
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"static/uploads/{timestamp}_{file.filename}"
        file.save(filename)

        final = calculate_grade(centering, corners, edges, surface)
        label = label_from_grade(final)
        cert_id = f"R2R{random.randint(100000,999999)}"

        qr_link = f"http://localhost:5000/verify/{cert_id}"
        qr_path = f"static/qr/{cert_id}.png"
        qrcode.make(qr_link).save(qr_path)

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO submissions (cert_id, image_path, centering, corners, edges, surface, final_grade, label, qr_path, timestamp) VALUES (?,?,?,?,?,?,?,?,?,?)",
                  (cert_id, filename, centering, corners, edges, surface, final, label, qr_path, timestamp))
        conn.commit()
        conn.close()
        return redirect(url_for("verify", cert_id=cert_id))
    return render_template("index.html")

@app.route("/verify/<cert_id>")
def verify(cert_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM submissions WHERE cert_id=?", (cert_id,))
    card = c.fetchone()
    conn.close()
    return render_template("verify.html", card=card)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "5037Shannon!":
            session["admin"] = True
            return redirect(url_for("history"))
    return render_template("login.html")

@app.route("/history")
def history():
    if not session.get("admin"):
        return redirect(url_for("login"))
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM submissions ORDER BY id DESC")
    cards = c.fetchall()
    conn.close()
    return render_template("history.html", cards=cards)

@@
- if __name__ == "__main__":
-     app.run(debug=True)
+ if __name__ == "__main__":
+     import os
+     # Get the PORT Render provides (default to 5000 locally)
+     port = int(os.environ.get("PORT", 5000))
+     # Listen on all interfaces so Render can route traffic in
+     app.run(host="0.0.0.0", port=port, debug=True)

    
