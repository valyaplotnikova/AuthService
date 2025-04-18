from enum import Enum
from sqlalchemy import String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class RoleEnum(str, Enum):
    """
    Перечисление для ролей пользователей.
    """
    patient = "patient"
    doctor = "doctor"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    role: Mapped[RoleEnum] = mapped_column(SQLEnum(RoleEnum), default=RoleEnum.patient)
