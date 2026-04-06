# PaymentProcessingService

Асинхронный микросервис обработки платежей: REST API на FastAPI, PostgreSQL (SQLAlchemy 2 + asyncpg), публикация событий через RabbitMQ (FastStream), паттерн **transactional outbox**, доставка вебхуков и отдельный **consumer** для outbox и обработки очереди.

## Автор
Беляев Дмитрий Андреевич

## Стек

- Python 3.12+
- FastAPI, Pydantic v2, Uvicorn
- SQLAlchemy 2.0, Alembic, asyncpg
- RabbitMQ: FastStream
- DI: dependency-injector
- Тесты: pytest, pytest-asyncio, httpx (ASGI)

## Структура проекта

```text
paymentProcessing/
├─ main.py                 # точка входа API (uvicorn)
├─ consumer.py             # точка входа consumer
├─ alembic.ini
├─ pyproject.toml
├─ Dockerfile.api
├─ Dockerfile.consumer
├─ docker-compose.yml
├─ .env.example
├─ src/
│  ├─ application.py       # FastAPI app, lifespan, роутеры
│  ├─ consumer.py          # outbox poll, RabbitMQ, вебхуки
│  ├─ core/
│  │  ├─ config/           # настройки (БД, RabbitMQ, API key, …)
│  │  ├─ fastapi/          # auth, ошибки, подключение роутов
│  │  └─ containers.py
│  ├─ dependency/          # DI-контейнеры (use case, UoW)
│  ├─ modules/payment/     # domain, infrastructure, use cases
│  ├─ persistance/         # сущности и репозитории (payment, outbox)
│  ├─ adapters/            # rabbitmq, webhook
│  └─ clients/             # эмуляция платёжного шлюза
├─ migrations/
│  ├─ env.py
│  └─ versions/
└─ tests/
   ├─ conftest.py
   ├─ unit/
   ├─ integration/
   └─ smoke/
```

## Переменные окружения

Скопируйте `.env.example` в `.env` и при необходимости поправьте значения.

| Переменная | Назначение |
|------------|------------|
| `APP_NAME`, `APP_VERSION` | Метаданные сервиса |
| `APP_ENV` | Окружение: `local`, `dev`, `prod` |
| `APP_TYPE` | Префикс URL API и Swagger (см. ниже). Пример: `internal/api` |
| `DATABASE_URL` | Async SQLAlchemy URL, например `postgresql+asyncpg://…` |
| `SERVER_HOST`, `SERVER_PORT` | Хост и порт HTTP API |
| `API_KEY` | Ключ для заголовка `X-API-Key` |
| `RABBITMQ_URL` | AMQP, например `amqp://guest:guest@rabbitmq:5672/` |
| `OUTBOX_POLL_INTERVAL_SECONDS` | Интервал опроса outbox в consumer |
| `WEBHOOK_TIMEOUT_SECONDS` | Таймаут HTTP при вызове вебхука |
| `LOG_LEVEL` | Уровень логирования |

**Хост vs Docker:** на машине разработчика в `DATABASE_URL` / `RABBITMQ_URL` обычно указывают `localhost`. В Compose — имена сервисов (`postgres`, `rabbitmq`). PostgreSQL наружу проброшен как **5433 → 5432** (см. `docker-compose.yml`).

## Установка и запуск

### Зависимости

```bash
poetry install
```

### Docker Compose (API + consumer + Postgres + RabbitMQ)

```bash
docker compose up --build
```

После старта примените миграции (из хоста с установленным Poetry, при необходимости подставьте `localhost:5433` в `DATABASE_URL`):

```bash
poetry run alembic upgrade head
```

### Локально без Docker

Поднимите PostgreSQL и RabbitMQ, задайте в `.env` URL с `localhost`, затем:

```bash
poetry run alembic upgrade head
# в одном терминале
poetry run api
# в другом — consumer
poetry run consumer
```

Эквивалентно скриптам из `pyproject.toml`: `api` → `main:main`, `consumer` → `consumer:main`.

## Миграции

```bash
poetry run alembic upgrade head
```

## Тесты и линтер

```bash
poetry run pytest
poetry run ruff check .
```

## Префикс API и Swagger

Базовый путь к платежам задаётся через `APP_TYPE` (значение enum `AppType`, например `internal/api` из `.env.example`):

- **Платежи:** `/{APP_TYPE}/payment/v1/payments`
- **Swagger UI:** `/{APP_TYPE}/payment/docs`
- **OpenAPI JSON:** `/{APP_TYPE}/payment/openapi.json`

Пример для `APP_TYPE=internal/api`:

- Swagger: `http://localhost:8000/internal/api/payment/docs`
- Создание платежа: `POST http://localhost:8000/internal/api/payment/v1/payments`

Авторизация в Swagger: **Authorize** → заголовок `X-API-Key` (совпадает с `API_KEY` в `.env`).

## Примеры API

Подставьте свой префикс вместо `internal/api`, если изменили `APP_TYPE`.

### Создать платеж

Обязательны заголовки `X-API-Key` и `Idempotency-Key`. Ответ при успехе — **201 Created**.

```bash
curl -X POST "http://localhost:8000/internal/api/payment/v1/payments" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-secret-key" \
  -H "Idempotency-Key: order-123" \
  -d '{
    "amount": "100.00",
    "currency": "USD",
    "description": "Order #123",
    "metadata": {"order_id": "123"},
    "webhook_url": "https://webhook.site/your-id"
  }'
```

Пример тела ответа:

```json
{"payment_id":"<uuid>"}
```

### Получить платеж

```bash
curl -X GET "http://localhost:8000/internal/api/payment/v1/payments/<payment_id>" \
  -H "X-API-Key: dev-secret-key"
```

## Проверка DLQ

1. Укажите недоступный `webhook_url` при создании платежа.
2. Дождитесь обработки consumer’ом (outbox → очередь → вебхук).
3. Откройте RabbitMQ Management: `http://localhost:15672` (по умолчанию `guest` / `guest`).
4. Проверьте очередь `payments.dlq` (`DLQ_QUEUE` в `src/utils/constants.py`).
