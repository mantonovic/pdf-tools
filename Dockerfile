FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ghostscript \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pymupdf

COPY convert-to-a4.py ./convert-to-a4.py

CMD ["python", "convert-to-a4.py"]
