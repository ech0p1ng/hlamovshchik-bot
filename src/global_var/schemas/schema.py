from base.schema import BaseSchema, BaseSimpleSchema


class GlobalVarSimpleSchema(BaseSimpleSchema):
    '''
    Упрощенная Pydantic-схема глобальных переменных и констант

    Args:
        name (str): Имя переменной или константы
        value (str): Значение
    '''
    name: str
    value: str


class GlobalVarSchema(BaseSchema, GlobalVarSimpleSchema):
    '''
    Упрощенная Pydantic-схема глобальных переменных и констант

    Args:
        id (str): Идентификатор
        name (str): Имя переменной или константы
        value (str): Значение
    '''
