# RAG Chat Application

## Описание

Это современное приложение на основе RAG (Retrieval-Augmented Generation) для поддержки пользовательского чата и поиска по документам. Проект включает:
- backend на FastAPI для API, аутентификации, управления чатами и интеграции с векторным хранилищем Qdrant;
- frontend на React + Vite с маршрутизацией, авторизацией и адаптивным интерфейсом;
- PostgreSQL для хранения пользователей, чатов и сообщений;
- Qdrant для поиска по векторным и sparse embedding-индексам на основе загруженных документов;
- Adminer для удобного управления базой данных.

## Используемые технологии

- FastAPI
- Uvicorn
- SQLAlchemy
- PostgreSQL
- Qdrant
- LangChain + LangChain Community
- FastEmbed embeddings
- React
- Vite
- Nginx
- Docker / Docker Compose
- Adminer

## Запуск через Docker Compose

### Шаг 1. Подготовка

В корне проекта должен находиться файл `.env` с параметрами окружения. В `docker-compose.yml` используется `env_file: .env` для сервисов `qdrant`, `db`, `backend` и `frontend`.

Пример необходимых переменных представлен в файле .env.example

### Шаг 2. Запуск

В корневой папке проекта выполните:

```bash
docker compose up --build
```

### Шаг 3. Доступ к сервисам

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Qdrant HTTP: `http://localhost:6333`
- Админка PostgreSQL (Adminer): `http://localhost:8080`

### Шаг 4. Остановка

Чтобы остановить и удалить контейнеры:

```bash
docker compose down
```

## Структура проекта

- `backend/` — FastAPI backend
- `frontend/` — React frontend
- `docker-compose.yml` — описание сервисов и сетей