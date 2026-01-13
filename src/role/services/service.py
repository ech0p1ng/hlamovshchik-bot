from sqlalchemy.ext.asyncio import AsyncSession
from base.service import BaseService
from role.repositories.repository import RoleRepository
from role.models.model import RoleModel


class RoleService(BaseService[RoleModel]):
    '''
    Бизнес-логика ролей
    '''
    ADMIN_ID: int = 1
    TEACHER_ID: int = 2
    STUDENT_ID: int = 3

    def __init__(self, db: AsyncSession):
        '''
        Бизнес-логика ролей

        Args:
            repository (RoleRepository): Класс обработки данных о ролях в БД
        '''
        super().__init__(
            RoleRepository(db),
            RoleModel,
            single_model_name="роль",
            multiple_models_name="роли"
        )

    async def create(self, model: RoleModel) -> RoleModel:
        '''
        Создание роли

        Args:
            model (PermissionModel): SQLAlchemy-модель роли

        Returns:
            PermissionModel: SQLAlchemy-модель роли

        Raises:
            WasNotCreatedError: Роль не была создана
        '''
        filter = {
            "id": model.id,
            "name": model.name
        }
        if not await self.exists(filter, raise_exc=False):
            return await super().create(model)
        else:
            return await super().get(filter)

    async def get_admin_role(self) -> RoleModel:
        '''
        Поиск роли администратора по идентификатору

        Returns:
            RoleModel: SQLAlchemy-модель роли администратора

        Raises:
            NotFoundError: Не удалось найти роль
        '''
        return await self.get({"id": self.ADMIN_ID})

    async def get_teacher_role(self) -> RoleModel:
        '''
        Поиск роли преподавателя по идентификатору

        Returns:
            RoleModel: SQLAlchemy-модель роли преподавателя

        Raises:
            NotFoundError: Не удалось найти роль
        '''
        return await self.get({"id": self.TEACHER_ID})

    async def get_student_role(self) -> RoleModel:
        '''
        Поиск роли ученика по идентификатору

        Returns:
            RoleModel: SQLAlchemy-модель роли ученика

        Raises:
            NotFoundError: Не удалось найти роль
        '''
        return await self.get({"id": self.STUDENT_ID})
