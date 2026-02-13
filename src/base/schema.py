from pydantic import BaseModel, Field, ConfigDict


class BaseSimpleSchema(BaseModel):
    '''Базовая pydantic-схема'''

    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True)


class BaseSchema(BaseSimpleSchema):
    '''
    Базовая pydantic-схема

    Args:
        id (int): Идентификатор
    '''
    id: int = Field(gt=0, description="Идентификатор")
