from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from sqlalchemy.orm import Mapped, mapped_column


class BaseSimpleModel(DeclarativeBase):
    '''
    Базовая sqlalchemy-модель сущности БД без столбца id. \
        Используется в основном для разрыва связи многие-ко-многим
    '''
    __abstract__ = True
    metadata = MetaData()

    model_config = {
        'from_attributes': True
    }


class BaseModel(BaseSimpleModel):
    '''
    Базовая sqlalchemy-модель сущности БД

    Args:
        id (int): Идентификатор
    '''
    __abstract__ = True
    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )

    def __eq__(self, value) -> bool:
        if isinstance(value, self.__class__):
            return self.id == value.id
        return NotImplemented
