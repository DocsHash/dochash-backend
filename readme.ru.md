# Document Hash Backend API

Бэкенд системы хеширования и верификации документов через блокчейн на Litestar + PostgreSQL + Web3.

## Технологии

**Стек:** Litestar, Msgspec, PostgreSQL, Web3.py, Docker  
**Архитектура:** API сервер + Blockchain worker + База событий

## Быстрый старт

```bash
docker-compose up --build
curl http://localhost:8000/
```

## Варианты запуска

### Продакшн (API + Worker раздельно)
```bash
docker-compose up postgres api worker
# API: 4 uvicorn воркера на :8000
# Worker: 1 процесс мониторинга блокчейна
```

### Разработка (все в одном)
```bash
docker-compose --profile single up postgres single
# Single процесс на :8001
```

### Только API (без worker)
```bash
docker-compose up postgres api
# Для тестирования API без блокчейна
```

### Локальная разработка
```bash
pip install -r requirements.txt
docker-compose up postgres
python3 -m app.main
```

## API Endpoints

| Метод | Путь | Описание | Вход | Выход |
|-------|------|----------|------|--------|
| GET | `/` | Health check | - | `{"status": "ok"}` |
| POST | `/api/process-document` | Обработка PDF | multipart file | verification_id + hash |
| POST | `/api/verify-document` | Верификация | JSON/file | verified + timestamp |

## Алгоритм хеширования

**Критически важно:** Система использует **SHA512** для совместимости с блокчейн контрактом

**Python (Backend):**
```python
hashlib.sha512(file_content).hexdigest()
```

**JavaScript (Контракт):**
```javascript
crypto.createHash('sha512').update(fileBuffer).digest('hex')
```

Любое изменение алгоритма хеширования нарушит совместимость между системами

## Конфигурация (.env)

### Localhost (Hardhat)
```bash
RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
BLOCKCHAIN_NETWORK=localhost
```

### Polygon Mumbai
```bash
RPC_URL=https://rpc-mumbai.maticvigil.com/
CONTRACT_ADDRESS=ваш_адрес_контракта
BLOCKCHAIN_NETWORK=mumbai
```

### Polygon Mainnet
```bash
RPC_URL=https://polygon-rpc.com/
CONTRACT_ADDRESS=ваш_адрес_контракта
BLOCKCHAIN_NETWORK=polygon
```

## Команды

### Основные
```bash
# Создание проекта
python setup_project.py

# Продакшн запуск
docker-compose up postgres api worker

# Разработка
docker-compose --profile single up postgres single

# Остановка
docker-compose down
```

### Тестирование API

#### Health check
```bash
curl http://localhost:8000/
```

#### Обработка документа
```bash
curl -X POST -F "file=@pdf-1.pdf" http://localhost:8000/api/process-document
```

#### Верификация документа тремя способами

**1. По verification_id:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"verification_id":"nf8IdRjm"}' \
  http://localhost:8000/api/verify-document
```

**2. По document_hash:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"document_hash":"f8ed1414e5044e0301dbd7128f0a9e845188283887b81b82fde63c55bd43f5b7f34b3dc61b8489e1cc1237ef4b431de50543b04068b61a2e2a93336543d3e558"}' \
  http://localhost:8000/api/verify-document
```

**3. По файлу:**
```bash
curl -X POST -F "file=@pdf-6.pdf" http://localhost:8000/api/verify-document
```

**Ожидаемый результат верификации:**
```json
{
  "verified": true,
  "message": "Документ найден в блокчейне",
  "timestamp": "2025-07-09T15:30:45",
  "creator": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
}
```

### Мониторинг
```bash
# Логи всех сервисов
docker-compose logs -f

# Логи только API
docker-compose logs -f api

# Логи только Worker
docker-compose logs -f worker

# Статус контейнеров
docker-compose ps

# База данных
docker-compose exec postgres psql -U postgres -d document_hash

# Последний обработанный блок
cat data/last_block.txt

# Количество документов
docker-compose exec postgres psql -U postgres -d document_hash \
  -c "SELECT COUNT(*) FROM document_records;"
```

## Полный цикл работы системы

### 1. Сохранение документа в блокчейн (внешний JavaScript)
```bash
node document-verifier.js store ./pdf-6.pdf
# Результат: verification_id = nf8IdRjm
```

### 2. Синхронизация через Worker
```
🔍 Сканирование блоков 16 - 16
🔍 Processing event from block 16
🔍 Creator: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
💾 Сохранен документ: nf8IdRjm
✅ Обработано 1 событий
```

### 3. Проверка через API
```bash
# Повторная обработка того же файла
curl -X POST -F "file=@pdf-6.pdf" http://localhost:8000/api/process-document
# Результат: "is_unique":false, "message":"Документ уже существует с ID: nf8IdRjm"
```

## Архитектура безопасности

### Проверка уникальности
- **document_hash** - проверяется на существование в БД
- **verification_id** - генерируется с проверкой на коллизии
- **файл** - валидация PDF формата

### Обработка коллизий
```python
# При коллизии verification_id система автоматически генерирует новый ID
existing_id = await database.get_by_verification_id(verification_id)
if existing_id:
    while existing_id:
        verification_id, _, _ = DocumentProcessor.process_document(file_content, filename)
        existing_id = await database.get_by_verification_id(verification_id)
```

## Структура файлов

```
backend/
├── docker-compose.yml       # Инфраструктура
├── Dockerfile              # Контейнер
├── entrypoint.sh           # Точки входа
├── requirements.txt        # Зависимости
├── .env                    # Конфигурация
└── app/
    ├── api_handlers.py     # API логика
    ├── app_factory.py      # Фабрика приложений
    ├── asgi.py            # Multi-worker API
    ├── worker.py          # Blockchain worker
    ├── main.py            # Single process
    ├── models.py          # База данных
    ├── schemas.py         # Msgspec схемы
    ├── config.py          # Настройки
    └── services/
        ├── document_processor.py
        ├── blockchain_service.py
        └── blockchain_worker.py
```

## Кейсы использования

### MVP/Демо
```bash
# Быстрый старт для демонстрации
docker-compose --profile single up postgres single
```

### Продакшн
```bash
# Масштабируемая архитектура
docker-compose up postgres api worker
# Можно добавить больше API инстансов
```

### Разработка
```bash
# Локальная разработка без Docker
pip install -r requirements.txt
docker-compose up postgres
python -m app.main
```

### Тестирование API
```bash
# Только API без blockchain worker
docker-compose up postgres api
```

### Отладка Worker
```bash
# Только worker для отладки блокчейна
docker-compose up postgres worker
```

## Устранение неполадок

| Проблема | Решение |
|----------|---------|
| API недоступен | `docker-compose ps`, проверить порты |
| Worker не работает | `docker-compose logs worker`, проверить RPC_URL |
| База недоступна | `docker-compose up postgres`, проверить здоровье |
| Блокчейн недоступен | `curl $RPC_URL`, проверить сеть |
| Нет прав на данные | `chmod -R 777 data/` |
| Разные хеши документов | Проверить алгоритм хеширования (должен быть SHA512) |
| Документ не найден | Убедиться что Worker синхронизировал данные из блокчейна |

## Переменные окружения

```bash
# Обязательные
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/document_hash
RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3

# Опциональные
BLOCKCHAIN_NETWORK=localhost
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
DEBUG=true
LOG_LEVEL=INFO
API_WORKERS=4
```

## Производительность

- **API:** Async Litestar + Msgspec = высокая производительность
- **Worker:** Батчинг событий блокчейна
- **База:** Индексы для быстрого поиска
- **Масштабирование:** Multiple API workers + Single worker
- **Хеширование:** SHA512 для совместимости с блокчейн контрактом
