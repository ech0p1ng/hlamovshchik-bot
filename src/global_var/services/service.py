from sqlalchemy.ext.asyncio import AsyncSession

from base.service import BaseService
from global_var.models.model import GlobalVarModel
from global_var.repositories.repository import GlobalVarRepository
from global_var.schemas.schema import GlobalVarSimpleSchema


class GlobalVarService(BaseService[GlobalVarModel]):
    '''
    Бизнес-логика глобальных переменных и констант
    '''

    def __init__(self, db: AsyncSession):
        '''
        Бизнес-логика глобальных переменных и констант

        Args:
            db (AsyncSession): Асинхронная сессия БД
        '''
        super().__init__(
            GlobalVarRepository(db),
            GlobalVarModel,
            single_model_name="глобальная переменная или константа",
            multiple_models_name="глобальных переменных или констант"
        )

    async def get_value(self, name: str) -> str | None:
        filter = {'name': name}
        if not await self.exists(filter, raise_exc=False):
            return None
        model = await self.get(filter)
        return model.value

    async def set_value(self, name: str, value: str) -> None:
        filter = {'name': name}
        if await self.exists(filter, raise_exc=False):
            model = await self.get(filter)
            model.value = value
            await self.update(model, filter)
        else:
            model = GlobalVarModel.from_schema(GlobalVarSimpleSchema(
                name=name,
                value=value
            ))
            await self.create(model)
