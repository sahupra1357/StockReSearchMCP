# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . /app

ENV CHROMA_PERSIST_DIR=/app/db

# create db dir
RUN mkdir -p /app/db /app/sec_filings

EXPOSE 8000
CMD ["uvicorn", "search_api:app", "--host", "0.0.0.0", "--port", "8000"]