from pydantic import Extra, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """ Класс настроек для работы проекта. """
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=(".env", ".test.env"),
        extra='allow'
    )

    @computed_field
    def get_db_url_async(self) -> str:
        """
        Формирует строку подключения к базе данных PostgreSQL с использованием asyncpg.

        :return: Строка подключения к базе данных в формате
                 'postgresql+asyncpg://<user>:<password>@<host>:<port>/<dbname>'
        :rtype: str
        """
        return (
            f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
            f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )

    @computed_field
    def get_db_url(self) -> str:
        """
        Формирует строку подключения к базе данных PostgreSQL с использованием asyncpg.

        :return: Строка подключения к базе данных в формате
                 'postgresql+asyncpg://<user>:<password>@<host>:<port>/<dbname>'
        :rtype: str
        """
        return (
            f"postgresql://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field
    def get_auth_data(self) -> dict:
        """
        Получает данные аутентификации, включая секретный ключ и алгоритм.

        :return: Словарь с данными аутентификации, содержащий 'secret_key' и 'algorithm'.
        :rtype: dict
        """
        return {"secret_key": settings.SECRET_KEY, "algorithm": settings.ALGORITHM}


settings = Settings()
