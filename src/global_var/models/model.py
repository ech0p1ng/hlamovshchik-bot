from sqlalchemy.orm import Mapped, mapped_column
from base.model import BaseModel
from global_var.schemas.schema import GlobalVarSchema, GlobalVarSimpleSchema


class GlobalVarModel(BaseModel):
    '''
    SQL Alchemy модель глобальных переменных и констант

    Args:
        id (int): Идентификатор

    '''
    __tablename__ = 'global_var'

    name: Mapped[str] = mapped_column(nullable=False)
    value: Mapped[str] = mapped_column(nullable=False)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, GlobalVarModel):
            self_stats = (
                self.name,
                self.value,
            )
            value_stats = (
                value.name,
                value.value,
            )
            return self_stats == value_stats
        else:
            return False

    @classmethod
    def from_schema(
        cls,
        schema: GlobalVarSimpleSchema | GlobalVarSchema,
    ) -> 'GlobalVarModel':
        '''
        Получение модели из Pydantic-схем

        Args:
            schema (GlobalVarSimpleSchema | GlobalVarSchema): Pydantic-схема

        Returns:
            GlobalVarModel: SQL Alchemy модель глобальной переменной или константы
        '''
        if type(schema) is GlobalVarSimpleSchema:
            return cls(
                name=schema.name,
                value=schema.value,
            )
        elif type(schema) is GlobalVarSchema:
            return cls(
                id=schema.id,
                name=schema.name,
                value=schema.value,
            )
        else:
            return cls(
                name=schema.name,
                value=schema.value,
            )
