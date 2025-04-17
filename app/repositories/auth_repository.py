from models.users import User
from repositories.base_repository import BaseRepository


class UsersRepository(BaseRepository):
    model = User
