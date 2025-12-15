from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from sqlalchemy.orm import Mapped, mapped_column


class BaseModel(DeclarativeBase):
    '''
    Базовая sqlalchemy-модель сущности БД

    Args:
        id (int): Идентификатор
    '''
    metadata = MetaData()

    model_config = {
        'from_attributes': True
    }

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )

    def __eq__(self, value) -> bool:
        if isinstance(value, self.__class__):
            return self.id == value.id
        return NotImplemented
