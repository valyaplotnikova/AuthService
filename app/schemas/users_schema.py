from typing import Self, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from sqlalchemy import Enum

from utils import get_password_hash


class SEmailModel(BaseModel):
    email: EmailStr = Field(description="Электронная почта")
    model_config = ConfigDict(from_attributes=True)


class SUserBase(SEmailModel):
    first_name: str = Field(min_length=3, max_length=50, description="Имя, от 3 до 50 символов")
    last_name: str = Field(min_length=3, max_length=50, description="Фамилия, от 3 до 50 символов")
    role: str


class SUserRegister(SUserBase):
    password: str = Field(min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")
    confirm_password: str = Field(min_length=5, max_length=50, description="Повторите пароль")

    @model_validator(mode="after")
    def check_password(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Пароли не совпадают")
        self.password = get_password_hash(self.password)  # хешируем пароль до сохранения в базе данных
        return self


class SUserAddDB(SUserBase):
    password: str = Field(min_length=5, description="Пароль в формате HASH-строки")


class SUserAuth(SEmailModel):
    password: str = Field(min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")


class SUserSearch(BaseModel):
    id: int = Field(description="Идентификатор пользователя")


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None


class SToken(BaseModel):
    access_token: str
    token_type: str
