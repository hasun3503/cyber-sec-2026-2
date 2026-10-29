# Flask 보안 실습 웹 껍데기

초보자가 Flask와 SQLite의 흐름을 이해하고, **약한 비밀번호를 대상으로 하는 브루트포스 실습**과 **HTTP 평문 통신 관찰 실습**을 할 수 있도록 만든 작은 예제입니다.

> 이 프로젝트는 격리된 로컬 또는 실습용 Docker 네트워크에서만 실행하세요. 실제 서비스에 사용하면 안 됩니다.

## 실행

### 로컬

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

브라우저에서 <http://localhost:5000>을 엽니다.

### Docker

```powershell
docker build -t flask-security-lab .
docker run --rm -p 5000:5000 flask-security-lab
```

컨테이너를 지우면 컨테이너 안의 `lab.db`도 함께 사라집니다. 데이터를 유지하려면 실습 범위 안에서 볼륨을 추가하세요.

## 실습 계정

- 아이디: `student`
- 비밀번호: `password123`

## 의도적으로 단순하게 둔 부분

- 비밀번호를 SQLite에 평문으로 저장합니다. 데이터베이스 파일을 직접 확인하는 실습을 위한 설정입니다.
- 로그인 시도 횟수 제한이나 계정 잠금이 없습니다. 따라서 약한 비밀번호를 대상으로 한 브루트포스 실습을 관찰할 수 있습니다.
- HTTPS를 설정하지 않고 Flask의 HTTP 서버로 실행합니다. 실습 네트워크에서 요청/응답의 평문을 관찰할 수 있습니다.

## 넣지 않은 취약점

사용자 입력은 SQLite 파라미터 바인딩으로 처리하고, 화면 출력은 Jinja 자동 이스케이프를 사용합니다. 따라서 이 예제의 목표와 관계없는 SQL 인젝션과 XSS 코드는 포함하지 않았습니다.

## 파일 구조

- `app.py`: Flask 라우트, SQLite 초기화, 로그인 세션
- `templates/`: 홈, 로그인, 구매 내역 화면
- `static/style.css`: 최소한의 화면 스타일
- `lab.db`: 최초 실행 시 자동 생성되는 SQLite 데이터베이스
