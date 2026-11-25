FROM node:20-alpine AS frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY etl ./etl
COPY sql ./sql
COPY data ./data
COPY --from=frontend /frontend/dist ./frontend/dist

EXPOSE 8000
CMD ["sh", "-c", "python -m etl.load_data && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
