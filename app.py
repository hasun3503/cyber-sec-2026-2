# 운영체제의 경로 기능을 사용하기 위한 모듈입니다.
import os
# SQLite 데이터베이스를 파이썬에서 사용하기 위한 기본 모듈입니다.
import sqlite3
# 로그인 보호 데코레이터가 원래 함수의 이름과 설명을 유지하도록 하는 도구입니다.
from functools import wraps

# Flask 앱과 화면 출력, 이동, 폼 데이터, 세션에 필요한 기능을 가져옵니다.
from flask import Flask, flash, redirect, render_template, request, session, url_for


# 현재 app.py 파일이 있는 폴더의 절대 경로를 구합니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# SQLite 파일을 프로젝트 폴더의 lab.db로 저장하도록 경로를 만듭니다.
DATABASE_PATH = os.path.join(BASE_DIR, "lab.db")

# Flask 애플리케이션 객체를 생성합니다.
app = Flask(__name__)
# 세션 쿠키를 서명할 때 사용할 키를 설정합니다.
# 환경 변수에 키가 있으면 그것을 사용하고, 없으면 실습용 기본 키를 사용합니다.
app.config["SECRET_KEY"] = os.environ.get(
    "FLASK_SECRET_KEY", "change-this-key-for-a-real-application"
)


def get_db():
    # SQLite 데이터베이스 파일에 연결합니다.
    database = sqlite3.connect(DATABASE_PATH)
    # 조회 결과를 튜플 대신 열 이름으로 읽을 수 있게 설정합니다.
    database.row_factory = sqlite3.Row
    # 연결 객체를 호출한 코드로 반환합니다.
    return database


def initialize_database():
    # 데이터베이스 연결을 엽니다.
    database = get_db()
    # users 테이블이 없을 때만 계정 정보를 저장할 테이블을 만듭니다.
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
    # purchases 테이블이 없을 때만 구매 내역 테이블을 만듭니다.
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

    # 프로그램을 여러 번 실행해도 샘플 계정이 중복 생성되지 않도록 확인합니다.
    sample_user = database.execute(
        "SELECT id FROM users WHERE username = ?", ("student",)
    ).fetchone()
    # student 계정이 아직 없을 때만 샘플 계정과 구매 내역을 만듭니다.
    if sample_user is None:
        # 실습용 계정을 users 테이블에 추가합니다.
        # 비밀번호는 의도적으로 평문으로 저장되어 있습니다.
        cursor = database.execute(
            "INSERT INTO users (username, password, display_name) VALUES (?, ?, ?)",
            ("student", "password123", "실습생"),
        )
        # 방금 추가한 계정의 자동 증가 id를 가져옵니다.
        user_id = cursor.lastrowid
        # 샘플 계정에 연결할 구매 내역 두 건을 추가합니다.
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
    # 지금까지의 INSERT 작업을 실제 파일에 저장합니다.
    database.commit()
    # 데이터베이스 연결을 닫습니다.
    database.close()


def login_required(view):
    # 로그인 여부를 확인하는 데코레이터를 정의합니다.
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        # 세션에 user_id가 없으면 로그인하지 않은 상태로 판단합니다.
        if "user_id" not in session:
            # 다음 화면에서 보여줄 안내 메시지를 저장합니다.
            flash("로그인이 필요합니다.")
            # 로그인 화면으로 이동시킵니다.
            return redirect(url_for("login"))
        # 로그인 상태라면 원래 요청한 화면 함수를 실행합니다.
        return view(*args, **kwargs)

    # 검사를 추가한 함수를 반환합니다.
    return wrapped_view


# "/" 주소로 접속했을 때 실행되는 라우트입니다.
@app.route("/")
def index():
    # templates/index.html 파일을 화면으로 보여줍니다.
    return render_template("index.html")


# "/login" 주소를 GET과 POST 방식으로 모두 처리합니다.
@app.route("/login", methods=("GET", "POST"))
def login():
    # 폼을 제출하는 POST 요청인지 확인합니다.
    if request.method == "POST":
        # 사용자가 입력한 아이디를 가져오고 앞뒤 공백을 제거합니다.
        username = request.form.get("username", "").strip()
        # 사용자가 입력한 비밀번호를 가져옵니다.
        password = request.form.get("password", "")

        # 데이터베이스 연결을 엽니다.
        database = get_db()
        # 입력값을 ? 자리에 전달하는 파라미터 바인딩 방식으로 계정을 조회합니다.
        # 이 방식은 이 실습의 범위에 SQL 인젝션을 포함하지 않기 위해 사용합니다.
        user = database.execute(
            "SELECT id, username, password, display_name FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        # 계정 조회가 끝났으므로 연결을 닫습니다.
        database.close()

        # 조회된 계정이 있고 입력 비밀번호가 저장된 비밀번호와 같은지 확인합니다.
        if user is not None and user["password"] == password:
            # 기존 세션 값을 비워 이전 로그인 정보가 남지 않게 합니다.
            session.clear()
            # 로그인한 사용자의 id를 세션에 저장합니다.
            session["user_id"] = user["id"]
            # 화면에 표시할 이름도 세션에 저장합니다.
            session["display_name"] = user["display_name"]
            # 로그인 성공 후 대시보드로 이동합니다.
            return redirect(url_for("dashboard"))

        # 로그인 실패 메시지를 다음 화면에 표시하도록 저장합니다.
        flash("아이디 또는 비밀번호가 올바르지 않습니다.")

    # GET 요청이거나 로그인에 실패한 경우 로그인 화면을 보여줍니다.
    return render_template("login.html")


# "/dashboard" 주소를 처리합니다.
@app.route("/dashboard")
# 이 라우트가 실행되기 전에 로그인 여부를 검사합니다.
@login_required
def dashboard():
    # 데이터베이스 연결을 엽니다.
    database = get_db()
    # 현재 세션 사용자의 구매 내역만 조회합니다.
    purchases = database.execute(
        """
        SELECT item_name, purchased_at
        FROM purchases
        WHERE user_id = ?
        ORDER BY purchased_at DESC
        """,
        (session["user_id"],),
    ).fetchall()
    # 조회가 끝났으므로 데이터베이스 연결을 닫습니다.
    database.close()
    # 구매 내역을 dashboard.html 템플릿에 전달합니다.
    return render_template("dashboard.html", purchases=purchases)


# "/logout" 주소로 접속하면 로그아웃 처리합니다.
@app.route("/logout")
def logout():
    # 세션에 저장된 로그인 정보를 모두 삭제합니다.
    session.clear()
    # 로그아웃 후 첫 화면으로 이동합니다.
    return redirect(url_for("index"))


# 이 파일을 직접 실행했을 때만 아래 초기화와 서버 실행을 수행합니다.
if __name__ == "__main__":
    # 테이블과 실습용 샘플 데이터를 준비합니다.
    initialize_database()
    # 모든 네트워크 인터페이스에서 5000번 포트로 HTTP 서버를 실행합니다.
    # 0.0.0.0은 Docker 컨테이너 외부에서도 접속할 수 있게 하기 위한 설정입니다.
    app.run(host="0.0.0.0", port=5000, debug=False)
