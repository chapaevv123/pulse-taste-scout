FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir .
ENV PORT=8000
CMD ["sh", "-c", "uvicorn pulse_taste_scout.app:app --host 0.0.0.0 --port ${PORT}"]
