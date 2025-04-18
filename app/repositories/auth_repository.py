from app.models.users import User
from app.repositories.base_repository import BaseRepository


class UsersRepository(BaseRepository):
    model = User
