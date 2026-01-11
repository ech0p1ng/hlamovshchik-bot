from sqlalchemy.ext.asyncio import AsyncSession

from base.service import BaseService
from global_var.models.model import GlobalVarModel
from global_var.repositories.repository import GlobalVarRepository


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

    async def get_value_by_name(self, name: str) -> str | None:
        filter = {'name': name}
        if not self.exists(filter, raise_exc=False):
            return None
        model = await self.get(filter)
        return model.value
