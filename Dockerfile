FROM python:3.11-slim

WORKDIR /app

COPY fastapi_app/requirements.txt /app/fastapi_app/requirements.txt
RUN pip install --no-cache-dir -r /app/fastapi_app/requirements.txt

COPY . /app

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["uvicorn", "fastapi_app.api:app", "--host", "0.0.0.0", "--port", "8080"]