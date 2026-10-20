FROM python:3.12.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --requirement requirements.txt \
    && groupadd --system app && useradd --system --gid app --home-dir /app app
COPY --chown=app:app app.py .
USER app:app
EXPOSE 5000
CMD ["/usr/local/bin/python3.12", "app.py"]
