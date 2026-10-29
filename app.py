import os
import sqlite3
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "lab.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "FLASK_SECRET_KEY", "change-this-key-for-a-real-application"
)


def get_db():
    database = sqlite3.connect(DATABASE_PATH)
    database.row_factory = sqlite3.Row
    return database


def initialize_database():
    database = get_db()
    database.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            display_name TEXT NOT NULL
        )
        """
    )
    database.execute(
        """
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            purchased_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )

    sample_user = database.execute(
        "SELECT id FROM users WHERE username = ?", ("student",)
    ).fetchone()
    if sample_user is None:
        cursor = database.execute(
            "INSERT INTO users (username, password, display_name) VALUES (?, ?, ?)",
            ("student", "password123", "실습생"),
        )
        user_id = cursor.lastrowid
        database.executemany(
            """
            INSERT INTO purchases (user_id, item_name, purchased_at)
            VALUES (?, ?, ?)
            """,
            [
                (user_id, "네트워크 기초 강의", "2026-10-01"),
                (user_id, "보안 실습 노트", "2026-10-15"),
            ],
        )
    database.commit()
    database.close()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("로그인이 필요합니다.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        database = get_db()
        user = database.execute(
            "SELECT id, username, password, display_name FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        database.close()

        if user is not None and user["password"] == password:
            session.clear()
            session["user_id"] = user["id"]
            session["display_name"] = user["display_name"]
            return redirect(url_for("dashboard"))

        flash("아이디 또는 비밀번호가 올바르지 않습니다.")

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    database = get_db()
    purchases = database.execute(
        """
        SELECT item_name, purchased_at
        FROM purchases
        WHERE user_id = ?
        ORDER BY purchased_at DESC
        """,
        (session["user_id"],),
    ).fetchall()
    database.close()
    return render_template("dashboard.html", purchases=purchases)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000, debug=False)
