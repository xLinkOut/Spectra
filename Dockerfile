FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && pip install -e .

RUN mkdir -p /app/data /app/inbox /app/processed

EXPOSE 8080

CMD ["uvicorn", "spectra.web.server:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "warning"]
