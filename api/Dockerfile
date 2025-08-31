# Python API용 slim 이미지
FROM python:3.10-slim

# 비대화형 모드 설정
ENV DEBIAN_FRONTEND=noninteractive

# 필수 패키지 설치
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        default-mysql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# 작업 디렉터리 설정
WORKDIR /app

# 의존성 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . /app

# 노출할 포트 명시
EXPOSE 8000

# 컨테이너 실행 명령
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "-b", "0.0.0.0:8000"]
