from base.schema import BaseSimpleSchema, BaseSchema


class BotCommandSimpleSchema(BaseSimpleSchema):
    '''
    Pydantic-схема команды бота

    Args:
        name (str): Внутреннее имя команды бота (например theme_post)
    '''
    name: str


class BotCommandSchema(BaseSchema, BotCommandSimpleSchema):
    '''
    Pydantic-схема команды бота

    Args:
        id (int): Идентификатор
        name (str): Внутреннее имя команды бота (например theme_post)
    '''
