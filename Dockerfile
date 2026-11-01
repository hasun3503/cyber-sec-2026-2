# Python 실행 환경이 들어 있는 가벼운 이미지에서 시작합니다.
FROM python:3.12-slim

# 컨테이너 안에서 사용할 작업 폴더를 지정합니다.
WORKDIR /app
# 의존성 목록 파일을 먼저 복사합니다.
COPY requirements.txt .
# requirements.txt에 적힌 Python 패키지를 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 나머지 프로젝트 파일을 컨테이너의 /app에 복사합니다.
COPY . .
# 애플리케이션이 사용할 포트를 문서로 표시합니다.
EXPOSE 5000
# 컨테이너가 시작될 때 Flask 앱을 실행합니다.
CMD ["python", "app.py"]
