import logging
from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from jwt.exceptions import InvalidTokenError


from core import config
from core.config import settings
from dependencies.repository_dep import get_session_without_commit, get_session_with_commit
from models.users import User
from services.users_service import UserService
from loguru import logger


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme),
                           session: AsyncSession = Depends(get_session_without_commit)
                           ):
    logger.info('Begin')
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    logger.info(f"{token}")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.info(f"{payload}")
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except InvalidTokenError as err:
        logger.info(f"{token}")
        raise credentials_exception from err
    user_service = UserService(session)
    user = await user_service.get_user_by_email(email)
    return user
