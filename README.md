# payment-processing-service

## Структура проекта

```text
paymentProcessing/
├─ main.py
├─ consumer.py
├─ alembic.ini
├─ pyproject.toml
├─ Dockerfile.api
├─ Dockerfile.consumer
├─ docker-compose.yml
├─ .env.example
├─ src/
│  ├─ application.py
│  ├─ consumer.py
│  ├─ core/
│  │  ├─ config/
│  │  ├─ fastapi/
│  │  └─ containers.py
│  ├─ dependency/
│  │  ├─ container.py
│  │  ├─ uow_container.py
│  │  └─ use_case_container.py
│  ├─ modules/
│  │  ├─ __init__.py
│  │  └─ payment/
│  │     ├─ domain/
│  │     ├─ infrastructure/
│  │     └─ use_case/
│  │        ├─ create_payment/
│  │        └─ get_payment/
│  ├─ persistance/
│  ├─ adapters/
│  │  └─ rabbitmq/
│  └─ clients/
├─ migrations/
│  ├─ env.py
│  └─ versions/
└─ tests/
   ├─ conftest.py
   ├─ unit/
   ├─ integration/
   └─ e2e/
```

## Переменные окружения

Скопируйте `.env.example` в `.env`.

Важно:
- Если запускаете **на хосте**, используйте `localhost` в `DATABASE_URL`/`RABBITMQ_URL`.
- Если запускаете **в Docker Compose**, можно использовать имена сервисов (`postgres`, `rabbitmq`).

## Запуск

```bash
docker compose up --build
```

## Миграции

```bash
poetry run alembic upgrade head
```

## Тесты

```bash
poetry run pytest
```

## Swagger

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI: `http://localhost:8000/openapi.json`

Авторизация:
- Нажмите **Authorize** в Swagger UI и задайте `X-API-Key` один раз — после этого он будет подставляться во все запросы автоматически.

## API примеры

### Create payment

```bash
curl -X POST "http://localhost:8000/api/v1/payments" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: order-123" \
  -d '{
    "amount": "100.00",
    "currency": "USD",
    "description": "Order #123",
    "metadata": {"order_id": "123"},
    "webhook_url": "https://webhook.site/your-id"
  }'
```

Ответ:

```json
{"payment_id":"<uuid>"}
```

### Get payment

```bash
curl -X GET "http://localhost:8000/api/v1/payments/<payment_id>" \
  -H "X-API-Key: dev-secret-key"
```

## Проверка DLQ

1. Укажите недоступный `webhook_url`.
2. Создайте платеж.
3. Откройте RabbitMQ UI: `http://localhost:15672` (`guest/guest`).
4. Проверьте очередь `payments.dlq`.
