FROM python:3.10 AS build

WORKDIR /usr/src/app/backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY backend/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

FROM python:3.10

WORKDIR /usr/src/app/backend

COPY --from=build /opt/venv /opt/venv
COPY --from=build /usr/src/app .

ENV PATH="/opt/venv/bin:$PATH"

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /usr/src/app
USER appuser

EXPOSE 8080

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
