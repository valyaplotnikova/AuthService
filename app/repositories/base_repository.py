from abc import abstractmethod, ABC
from typing import List, TypeVar, Type

from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete, insert
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import Base

T = TypeVar("T", bound=Base)


class AbstractRepository(ABC):

    @abstractmethod
    async def add(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get(self, *args, **kwargs):
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):

    model = None

    def __init__(self, session: AsyncSession):
        self._session = session
        if self.model is None:
            raise ValueError("Модель должна быть указана в дочернем классе")

    async def add(self, **kwargs) -> None:
        query = insert(self.model).values(**kwargs)
        await self._session.execute(query)

    async def get(self, reference):
        return self._session.query(self.model).filter_by(reference=reference).one()


class BaseRepository(SqlAlchemyRepository):
    model: Type[T] = None

    async def find_one_or_none_by_id(self, data_id: int):
        """
        Ищет запись в базе данных по заданному идентификатору.

        :param data_id: Идентификатор записи для поиска.
        :return: Найденная запись или None, если запись не найдена.
        :raises SQLAlchemyError: Если возникает ошибка при выполнении запроса.
        """
        try:
            query = select(self.model).filter_by(id=data_id)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Запись {self.model.__name__} с ID {data_id} {'найдена' if record else 'не найдена'}."
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с ID {data_id}: {e}")
            raise

    async def find_one_or_none(self, filters: BaseModel):
        """
        Ищет одну запись в базе данных по заданным фильтрам.

        :param filters: Фильтры для поиска записи.
        :return: Найденная запись или None, если запись не найдена.
        :raises SQLAlchemyError: Если возникает ошибка при выполнении запроса.
        """
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(f"Поиск одной записи {self.model.__name__} по фильтрам: {filter_dict}")
        try:
            query = select(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Запись {'найдена' if record else 'не найдена'} по фильтрам: {filter_dict}"
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи по фильтрам {filter_dict}: {e}")
            raise

    async def find_all(self, filters: BaseModel | None = None):
        """
        Ищет все записи в базе данных, соответствующие заданным фильтрам.

        :param filters: Фильтры для поиска записей (по умолчанию None).
        :return: Список найденных записей.
        :raises SQLAlchemyError: Если возникает ошибка при выполнении запроса.
        """
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        logger.info(f"Поиск всех записей {self.model.__name__} по фильтрам: {filter_dict}")
        try:
            query = select(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            records = result.scalars().all()
            logger.info(f"Найдено {len(records)} записей.")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске всех записей по фильтрам {filter_dict}: {e}")
            raise

    async def add(self, values: BaseModel):
        """
        Добавляет новую запись в базу данных.

        :param values: Данные для добавления, представленные в виде Pydantic-модели.
        :return: Добавленная запись.
        :raises SQLAlchemyError: Если возникает ошибка при добавлении записи.
        """
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(f"Добавление записи {self.model.__name__} с параметрами: {values_dict}")
        try:
            new_instance = self.model(**values_dict)
            self._session.add(new_instance)
            logger.info(f"Запись {self.model.__name__} успешно добавлена.")
            await self._session.flush()
            return new_instance
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении записи: {e}")
            raise

    async def add_many(self, instances: List[BaseModel]):
        """
        Добавляет несколько записей в базу данных.

        :param instances: Список данных для добавления, представленных в виде Pydantic-моделей.
        :return: Список добавленных записей.
        :raises SQLAlchemyError: Если возникает ошибка при добавлении записей.
        """
        values_list = [item.model_dump(exclude_unset=True) for item in instances]
        logger.info(f"Добавление нескольких записей {self.model.__name__}. Количество: {len(values_list)}")
        try:
            new_instances = [self.model(**values) for values in values_list]
            self._session.add_all(new_instances)
            logger.info(f"Успешно добавлено {len(new_instances)} записей.")
            await self._session.flush()
            return new_instances
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении нескольких записей: {e}")
            raise

    async def update(self, filters: BaseModel, values: BaseModel):
        """
        Обновляет записи в базе данных по заданным фильтрам.

        :param filters: Фильтры для поиска записей, которые нужно обновить.
        :param values: Новые значения для обновления, представленные в виде Pydantic-модели.
        :return: Количество обновленных записей.
        :raises SQLAlchemyError: Если возникает ошибка при обновлении записей.
        """
        filter_dict = filters.model_dump(exclude_unset=True)
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(
            f"Обновление записей {self.model.__name__} по фильтру: {filter_dict} с параметрами: {values_dict}")
        try:
            query = (
                sqlalchemy_update(self.model)
                .where(*[getattr(self.model, k) == v for k, v in filter_dict.items()])
                .values(**values_dict)
                .execution_options(synchronize_session="fetch")
            )
            result = await self._session.execute(query)
            logger.info(f"Обновлено {result.rowcount} записей.")
            await self._session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении записей: {e}")
            raise

    async def delete(self, filters: BaseModel):
        """
        Удаляет записи из базы данных по заданным фильтрам.

        :param filters: Фильтры для поиска записей, которые нужно удалить.
        :return: Количество удаленных записей.
        :raises ValueError: Если не указаны фильтры для удаления.
        :raises SQLAlchemyError: Если возникает ошибка при удалении записей.
        """
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(f"Удаление записей {self.model.__name__} по фильтру: {filter_dict}")
        if not filter_dict:
            logger.error("Нужен хотя бы один фильтр для удаления.")
            raise ValueError("Нужен хотя бы один фильтр для удаления.")
        try:
            query = sqlalchemy_delete(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            logger.info(f"Удалено {result.rowcount} записей.")
            await self._session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при удалении записей: {e}")
            raise
