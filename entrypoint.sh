#!/usr/bin/env bash

set -e

echo "🔄 Ожидание PostgreSQL..."
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
    echo "⏳ PostgreSQL недоступен - ожидание..."
    sleep 2
done
echo "✅ PostgreSQL готов"

# Add the current directory to the Python path
export PYTHONPATH=$PYTHONPATH:/app

if [ "$1" == 'api' ]; then
    echo "🚀 Запуск API сервера..."
    exec uvicorn asgi:application --host 0.0.0.0 --port 8000 --workers ${API_WORKERS:-4}
elif [ "$1" == 'worker' ]; then
    echo "🔧 Запуск Blockchain Worker..."
    exec python worker.py
elif [ "$1" == 'single' ]; then
    echo "🚀 Запуск Single Process (API + Worker)..."
    exec python main.py
else
    echo "❌ Неизвестная команда: $1"
    echo "Доступные команды: api, worker, single"
    exit 1
fi
