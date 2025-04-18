import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import InvalidTokenError
from loguru import logger

from app.core.config import settings
from app.dependencies.repository_dep import get_session_without_commit
from app.models.users import User
from app.services.users_service import UserService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_session_without_commit),
) -> User:
    """Получает текущего аутентифицированного пользователя по JWT токену.

    Проверяет валидность JWT токена, декодирует email из payload и ищет пользователя в БД.
    Если токен невалиден или пользователь не найден, возвращает HTTP 401.

    Args:
        token (str): JWT токен из заголовка Authorization (Bearer token).
        session (AsyncSession): Асинхронная сессия SQLAlchemy.

    Returns:
        User: Объект пользователя из БД.

    Raises:
        HTTPException: 401 UNAUTHORIZED если:
            - токен невалиден/просрочен
            - email не найден в payload
            - пользователь не существует в БД

    Examples:
        >>> # В зависимостях эндпоинта:
        >>> @app.get("/me")
        >>> async def read_current_user(user: User = Depends(get_current_user)):
        >>>     return user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.info(f"Decoded payload: {payload}")
        email: str = payload.get("sub")
        if email is None:
            logger.error("Email not found in token payload")
            raise credentials_exception
    except InvalidTokenError as err:
        logger.error(f"Invalid token")
        raise credentials_exception from err

    user_service = UserService(session)
    user = await user_service.get_user_by_email(email)
    if not user:
        logger.error(f"User with email {email} not found")
        raise credentials_exception

    return user
