# Auth-Service API

## Описание сервиса

Auth-Service предоставляет REST API для аутентификации и авторизации пользователей с использованием JWT-токенов. Сервис поддерживает ролевую модель доступа (patient, doctor, admin).

## Функциональные возможности

### Основные эндпоинты

- **Регистрация пользователей** (`POST /register`)
- **Аутентификация** (`POST /login`)
- **Получение информации о текущем пользователе** (`GET /me`)

### Ролевая модель

- **Patient** - базовые права доступа
- **Doctor** - расширенные медицинские права
- **Admin** - полные административные права

## Технологический стек

- **FastAPI** - веб-фреймворк для построения API
- **PostgreSQL** - реляционная база данных
- **Alembic** - система миграций базы данных
- **Pydantic** - валидация данных и сериализация
- **JWT** (PyJWT) - JSON Web Tokens для аутентификации
- **SQLAlchemy** - ORM для работы с базой данных
- **AsyncPG** - асинхронный драйвер для PostgreSQL

## Установка и запуск
Клонируйте данный репозиторий к себе на локальную машину: git clone https://github.com/valyaplotnikova/AuthService.git
### Запуск в Docker

1. Создайте файл `.env` в корне проекта на основе `.env.example`:
   ```bash
   cp .env.example .env
   ```

2. Заполните необходимые переменные окружения в `.env` файле

3. Запустите сервисы:
   ```bash
   docker-compose up -d --build
   ```

### Локальная разработка

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

2. Запустите сервис:
   ```bash
   uvicorn app.main:app --reload
   ```

## Использование API

### Регистрация пользователя

```http
POST /register
Content-Type: application/json

{
  "email": "user@example.com",
  "first_name": "string",
  "last_name": "string",
  "role": "string",
  "password": "string",
  "confirm_password": "string"
}
```

### Аутентификация

```http
POST /login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword123
```

### Получение информации о пользователе

```http
GET /me
Authorization: Bearer <your_jwt_token>
```

## Миграции базы данных

Для создания новой миграции:
```bash
alembic revision --autogenerate -m "description of changes"
```

Для применения миграций:
```bash
alembic upgrade head
```

## Тестирование

Запуск тестов:
```bash
pytest
```