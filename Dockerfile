FROM python:3.12-slim

WORKDIR /code

COPY app/recuirements.txt .
RUN pip install --no-cache-dir -r recuirements.txt

COPY app/ .

RUN useradd -m appuser && chown -R appuser /code
USER appuser

EXPOSE 8000

CMD  ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
