FROM python:3.12-slim AS build
RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc vim

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

FROM python:3.12-slim AS production
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY --from=build /app .

RUN mkdir -p /app/static /app/media && \
    chmod -R 755 /app/static /app/media

EXPOSE 8080
#CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8080"]
