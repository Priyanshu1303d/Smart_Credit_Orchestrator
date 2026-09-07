FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt setup.py README.md ./
COPY src/ ./src/

RUN pip install -e .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p data
# EXPOSE 8000
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
