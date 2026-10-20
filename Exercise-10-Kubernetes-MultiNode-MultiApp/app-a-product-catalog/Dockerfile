FROM python:3.12.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt \
    && groupadd --gid 10001 app \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin app

COPY app.py ./app.py
USER 10001:10001

EXPOSE 8080
HEALTHCHECK --interval=20s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:8080/health', timeout=2)"

CMD ["gunicorn", "--bind=0.0.0.0:8080", "--workers=1", "--access-logfile=-", "--error-logfile=-", "app:app"]
