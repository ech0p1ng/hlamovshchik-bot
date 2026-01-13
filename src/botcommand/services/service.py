from base.service import BaseService
from botcommand.models.model import BotCommandModel
from botcommand.repositories.repository import EndpointRepository
from sqlalchemy.ext.asyncio import AsyncSession
from botcommand.schemas.botcommand import BotCommandSimpleSchema


class BotCommandService(BaseService[BotCommandModel]):
    '''
    Бизнес-логика команд бота
    '''

    def __init__(self, db: AsyncSession):
        '''
        Бизнес логика команд бота

        Args:
            db (AsyncSession): Асинхронная сессия БД
        '''
        super().__init__(
            EndpointRepository(db),
            BotCommandModel,
            single_model_name="команда бота",
            multiple_models_name="команды бота"
        )

    async def create(self, model: BotCommandModel) -> BotCommandModel:
        '''
        Создание команды бота

        Args:
            model (PermissionModel): SQLAlchemy-модель команды бота

        Returns:
            PermissionModel: SQLAlchemy-модель команды бота

        Raises:
            WasNotCreatedError: Ручка не была создана
        '''
        filter = {"name": model.name}
        if not await self.exists(filter, raise_exc=False):
            return await super().create(model)
        else:
            return await self.get(filter)

    async def create_with_name(self, endpoint_name: str) -> BotCommandModel:
        '''
        Создание команды бота

        Args:
            endpoint_name (str): Имя команды бота

        Returns:
            PermissionModel: SQLAlchemy-модель команды бота

        Raises:
            WasNotCreatedError: Ручка не была создана
        '''

        model = BotCommandModel.from_schema(
            BotCommandSimpleSchema(
                name=endpoint_name
            )
        )
        return await self.create(model)
