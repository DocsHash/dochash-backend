FROM python:3.12

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . /app
COPY entrypoint.sh /app/entrypoint.sh
RUN mkdir -p /app/data

RUN addgroup --gid 1000 unprivileged && \
    adduser --uid 1000 --gid 1000 unprivileged && \
    chown -R unprivileged:unprivileged /app && \
    chmod +x /app/entrypoint.sh

USER unprivileged:unprivileged

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["api"]

EXPOSE 8000