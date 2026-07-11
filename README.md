# Wallet — приложение для учёта личных финансов

Pet-проект: REST API на FastAPI для управления кошельками, доходами и расходами. Есть веб-интерфейс, JWT-авторизация, история операций и уведомления в Telegram.

## Возможности

- Регистрация и вход (JWT)
- Несколько кошельков на пользователя
- Доход / расход с изменением баланса
- История операций с фильтрами и пагинацией
- Запись в историю при создании кошелька с начальным балансом
- Веб-интерфейс (светлая / тёмная тема)
- Уведомления админу в Telegram (опционально)
- Автотесты и CI на GitHub Actions

## Стек

| Слой     | Технологии |
|----------|------------|
| Backend  | Python 3.12, FastAPI, SQLAlchemy 
| БД       | PostgreSQL 16, Alembic 
| Auth     | JWT (python-jose), passlib 
| Frontend | HTML / CSS / JS (nginx) 
| Инфра    | Docker Compose 
| Тесты    | pytest, TestClient 
| CI       | GitHub Actions 

## Быстрый старт

### Требования

- Docker и Docker Compose
- Git

### 1. Клонировать и настроить окружение

```bash
git clone <url-репозитория>
cd fast_api_app
cp .env_example .env
```

Отредактируй `.env`:

- `SECRET_KEY` — случайная строка для JWT
- `POSTGRES_PASSWORD` — пароль PostgreSQL
- `TELEGRAM_TOKEN` и `ADMIN_TELEGRAM_CHAT_ID` — по желанию (без них уведомления просто не отправляются)

### 2. Запустить проект

```bash
docker compose up -d --build
```

| Сервис | URL |
|--------|-----|
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| Frontend | http://localhost:8080 |
| PostgreSQL (с хоста) | `localhost:5433`, БД `wallet` |

При старте `app` автоматически накатывает миграции (`alembic upgrade head`).

### 3. Остановить

```bash
docker compose down
```

Данные БД сохраняются в volume `pg_data_wallet`.

## API

Все защищённые эндпоинты требуют заголовок:

```
Authorization: Bearer <access_token>
```

### Auth

| Метод    | Путь             | Описание |
|----------|------------------|----------|
| `POST`   | `/auth/register` | Регистрация → JWT |
| `POST`   | `/auth/login`    | Вход → JWT |
| `DELETE` | `/auth/delete`   | Удалить аккаунт |

### Кошельки

| Метод    | Путь                              | Описание |
|----------|-----------------------------------|----------|
| `GET`    | `/api/v1`                         | Список кошельков |
| `GET`    | `/api/v1/balance`                 | Общий баланс |
| `GET`    | `/api/v1/balance?wallet_name=...` | Баланс кошелька |
| `POST`   | `/api/v1/wallets`                 | Создать кошелёк |
| `PATCH`  | `/api/v1/{wallet_name}`           | Переименовать |
| `DELETE` | `/api/v1/{wallet_name}`           | Удалить |

**Создание кошелька:**

```json
{
  "name": "Основной",
  "initial_balance": 100
}
```

### Операции

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/api/v1/operations` | История операций |
| `POST` | `/api/v1/operations/income` | Доход |
| `POST` | `/api/v1/operations/expense` | Расход |

**Query-параметры для истории:**

- `wallet_name` — фильтр по кошельку
- `type` — `income` или `expense`
- `limit` — 1–100 (по умолчанию 50)
- `offset` — пагинация

**Доход / расход:**

```json
{
  "wallet_name": "Основной",
  "amount": 25.5,
  "description": "Зарплата"
}
```

## Тесты

Поднять тестовую БД и прогнать тесты в контейнере:

```bash
docker compose up -d test_db
docker compose exec app pytest app/tests/ -v
```

Локально (нужен `TEST_DATABASE_URL` на `localhost:5434`):

```bash
export TEST_DATABASE_URL=postgresql+psycopg://postgres:change-me@localhost:5434/test_db
export DATABASE_URL=postgresql+psycopg://postgres:change-me@localhost:5434/test_db
export SECRET_KEY=test-secret
export ALGORITHM=HS256
pytest app/tests/ -v
```

## CI

На каждый `push` и `pull_request` GitHub Actions:

1. Поднимает PostgreSQL
2. Устанавливает зависимости
3. Запускает `pytest app/tests/`

Конфиг: `.github/workflows/ci.yml`

## Структура проекта

```
fast_api_app/
├── app/
│   ├── api/v1/          # Роуты (auth, wallets, operations)
│   ├── core/            # Настройки
│   ├── repository/      # Работа с БД
│   ├── service/         # Бизнес-логика
│   ├── models.py        # SQLAlchemy ORM
│   ├── schemas.py       # Pydantic-схемы
│   └── tests/           # pytest
├── alembic/             # Миграции
├── bot/                 # Telegram-бот (опционально)
├── frontend/            # Веб-интерфейс
├── docker-compose.yml
└── Dockerfile
```

## Миграции (Alembic)

Внутри контейнера:

```bash
docker compose exec app alembic revision --autogenerate -m "описание"
docker compose exec app alembic upgrade head
```

С хоста (если настроен `ALEMBIC_DATABASE_URL` в `.env` на `localhost:5433`).

## Скриншоты

<!-- Добавь сюда скриншоты дашборда и истории операций -->

## Лицензия

Учебный pet-проект. Используй свободно в портфолио.
