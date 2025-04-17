from datetime import timedelta

from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.security import create_access_token
from exceptions import UserAlreadyExistsException
from repositories.auth_repository import UsersRepository
from schemas.users_schema import SUserBase, SUserRegister, SEmailModel, SUserAddDB, SToken


class UserService:
    def __init__(self, session: AsyncSession):
        """
        Инициализация UserService.

        :param session: Асинхронная сессия базы данных.
        """
        self.session = session
        self.users_repo = UsersRepository(session)

    async def create_user(self, user_data: SUserRegister):
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
        return user

    async def login(self, form_data: OAuth2PasswordRequestForm = Depends(),):

        user = await self.users_repo.find_one_or_none(filters=SEmailModel(email=form_data.username))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return SToken(access_token=access_token, token_type="Bearer")
