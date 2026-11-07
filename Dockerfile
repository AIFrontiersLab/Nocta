FROM python:3.12-slim

WORKDIR /app
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app
ENV PYTHONPATH=/app
EXPOSE 8787

CMD ["python", "-m", "uvicorn", "app.api.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8787"]
