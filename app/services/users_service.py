from datetime import timedelta

from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.config import settings
from app.core.security import create_access_token
from app.repositories.auth_repository import UsersRepository
from app.schemas.users_schema import SUserRegister, SEmailModel, SUserAddDB, SToken
from app.utils import verify_password
from app.exceptions import UserAlreadyExistsException


class UserService:
    def __init__(self, session: AsyncSession):
        """
        Инициализация UserService.

        :param session: Асинхронная сессия базы данных.
        """
        self.session = session
        self.users_repo = UsersRepository(session)

    async def create_user(self, user_data: SUserRegister):
        """
        Создание пользователя и запись его в БД
        :param user_data: данные при регистрации
        :return: Данные пользователя.
        :raises UserAlreadyExistsException: Если пользователь уже существует.
        """
        existing_user = await self.users_repo.find_one_or_none(filters=SEmailModel(email=user_data.email))
        if existing_user:
            raise UserAlreadyExistsException

        # Подготовка данных для добавления
        user_data_dict = user_data.model_dump()
        user_data_dict.pop('confirm_password', None)

        # Добавление пользователя
        user = await self.users_repo.add(values=SUserAddDB(**user_data_dict))
        return user

    async def get_user_by_email(self, email: str):
        """
        Получение пользователя по его идентификатору.

        :param email: почта пользователя.
        :return: Данные пользователя.
        :raises UserNotFoundException: Если пользователь не найден.
        """
        user = await self.users_repo.find_one_or_none(filters=SEmailModel(email=email))
        if not user:
            logger.error(f"User not found for email: {email}")
        return user

    async def login(self, form_data: OAuth2PasswordRequestForm = Depends(),):
        """Аутентификация пользователя и выдача JWT токена.

            Проверяет учетные данные пользователя (email/пароль) и генерирует JWT токен
            при успешной аутентификации. Токен содержит email пользователя в payload.

            Args:
                form_data (OAuth2PasswordRequestForm): Форма с данными для входа:
                    - username: Email пользователя (OAuth2 спецификация использует 'username' для email)
                    - password: Пароль пользователя

            Returns:
                SToken: Объект с JWT токеном в формате:
                    {
                        "access_token": "eyJhbGciOi...",
                        "token_type": "Bearer"
                    }

            Raises:
                HTTPException: 401 UNAUTHORIZED если:
                    - пользователь с таким email не найден
                    - неверный пароль (если добавите проверку пароля)
                    - учетная запись неактивна"""

        user = await self.users_repo.find_one_or_none(filters=SEmailModel(email=form_data.username))
        if not user:
            logger.warning(f"Login attempt for non-existent user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not verify_password(form_data.password, user.password):
            logger.warning(f"Invalid password attempt for user: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user.email,
                "role": user.role.value
            },
            expires_delta=access_token_expires
        )

        logger.info(f"Successful login for {user.role} {user.email}")
        return SToken(access_token=access_token, token_type="Bearer")
