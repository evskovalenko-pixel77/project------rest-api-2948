FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn sqlalchemy PyJWT passlib bcrypt python-multipart email-validator --no-cache-dir
EXPOSE 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
