FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY app.py MODEL_CARD.md ./
COPY results ./results
RUN python -m pip install --upgrade pip && python -m pip install .

RUN useradd --create-home --uid 10001 trustlens
USER trustlens

EXPOSE 8501
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/health')"
CMD ["uvicorn", "trustlens.api:app", "--host=0.0.0.0", "--port=8501"]
