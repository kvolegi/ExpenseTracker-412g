FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt || true

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PORT=3000
ENV BACKEND_URL=http://expensetracker-backend:8000

EXPOSE 3000

CMD ["python", "server.py"]
