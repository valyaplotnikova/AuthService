
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.auth_dep import get_current_user, oauth2_scheme
from dependencies.repository_dep import get_session_with_commit
from models.users import User
from schemas.users_schema import SUserRegister, SUserBase
from services.users_service import UserService


router = APIRouter()


@router.post("/register")
async def register(user_data: SUserRegister, session: AsyncSession = Depends(get_session_with_commit)) -> SUserBase:
    user_service = UserService(session)
    return await user_service.create_user(user_data)


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                session: AsyncSession = Depends(get_session_with_commit)):
    user_service = UserService(session)
    token_data = await user_service.login(form_data)
    return token_data


@router.get("/me")
async def get_me(session: AsyncSession = Depends(get_session_with_commit)):
    return await get_current_user(session)
