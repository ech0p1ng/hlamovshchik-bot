from sqlalchemy.ext.asyncio import AsyncSession
from permission.repositories.repository import PermissionRepository
from base.service import BaseService
from permission.models.model import PermissionModel
from permission.schemas.schema import PermissionSimpleSchema
from botcommand.services.service import BotCommandService
from role.services.service import RoleService
from role.models.model import RoleModel
from botcommand.models.model import BotCommandModel
from exceptions.exception import (
    ForbiddenError, NotFoundError, UnauthorizedError
)
from user.models.model import UserModel


class PermissionService(BaseService[PermissionModel]):
    '''
    Бизнес-логика ограничения доступа к ручкам по ролям
    '''

    def __init__(
        self, db: AsyncSession,
        botcommand_service: BotCommandService,
        role_service: RoleService
    ):
        '''
        Бизнес-логика ограничения доступа к ручкам по ролям

        Args:
            db (AsyncSession): Асинхронная сессия БД
            botcommand_service (BotCommandService): Сервис команд бота
            role_service (RoleService): Сервис ролей
        '''
        self.botcommand_service = botcommand_service
        self.role_service = role_service
        super().__init__(
            PermissionRepository(db),
            PermissionModel,
            single_model_name="ограничение доступа к команде бота по ролям",
            multiple_models_name="ограничения доступа к команде бота по ролям"
        )

    async def create(self, model: PermissionModel) -> PermissionModel:
        '''
        Создание ограничения доступа к команде бота по ролям

        Args:
            model (PermissionModel): SQLAlchemy-модель ограничения \
                доступа к команде бота по ролям

        Returns:
            PermissionModel: SQLAlchemy-модель ограничения доступа \
                к команде бота по ролям

        Raises:
            WasNotCreatedError: Ограничение доступа к команде бота \
                по ролям не было создано
        '''
        filter = {
            "botcommand_id": model.botcommand_id,
            "role_id": model.role_id
        }
        if not await self.exists(filter, raise_exc=False):
            return await super().create(model)
        else:
            return await self.get(filter)

    async def create_with_role_and_botcommand(
        self,
        botcommand_model: BotCommandModel,
        role_model: RoleModel
    ) -> PermissionModel:
        '''
        Создание ограничения доступа к команде бота по ролям

        Args:
            botcommand_model (BotCommandModel): SQLAlchemy-модель ручки
            role_model (RoleModel): SQLAlchemy-модель роли

        Returns:
            PermissionModel: SQLAlchemy-модель ограничения доступа \
                к команде бота по ролям

        Raises:
            WasNotCreatedError: Ограничение доступа к команде бота \
                по ролям не было создано
            NotFoundError: Ручка или роль не найдены
        '''
        await self.role_service.exists({
            "id": role_model.id,
            "role_name": role_model.name
        })
        await self.botcommand_service.exists({
            "id": botcommand_model.id,
            "name": botcommand_model.name
        })

        model = PermissionModel.from_schema(
            PermissionSimpleSchema(
                role_id=role_model.id,
                botcommand_id=botcommand_model.id
            )
        )

        permission = await self.create(model)
        return permission

    async def create_for_roles(
        self,
        endpoint_name: str,
        *role_models: RoleModel,
        create_endpoint: bool = True
    ) -> list[PermissionModel]:
        '''
        Создание ограничения доступа к команде бота по нескольким ролям

        Args:
            endpoint_model (BotCommandModel): SQLAlchemy-модель ручки
            *role_models (RoleModel): SQLAlchemy-модели ролей

        Returns:
            PermissionModel: SQLAlchemy-модель ограничения доступа \
                к команде бота по ролям

        Raises:
            WasNotCreatedError: Ограничение доступа к команде бота \
                по ролям не было создано
            NotFoundError: Роль не найдена
        '''
        endpoint_exists = self.botcommand_service.exists(
            {"name": endpoint_name},
            raise_exc=False
        )
        if endpoint_exists:
            endpoint = await self.botcommand_service.get(
                {"name": endpoint_name}
            )
        elif create_endpoint:
            endpoint = await self.botcommand_service.create_with_name(
                endpoint_name
            )
        else:
            raise NotFoundError('Ручка не найдена')

        permissions = []
        for role in role_models:
            filter = {
                "role_id": role.id,
                "endpoint_id": endpoint.id
            }
            if not await self.exists(filter, raise_exc=False):
                permission = await self.create_with_role_and_botcommand(
                    endpoint, role
                )
            else:
                permission = await self.get(filter)
            permissions.append(permission)

        return permissions

    async def check_permission(
        self,
        endpoint_name: str,
        user_model: UserModel,
        raise_exc: bool = True
    ) -> bool:
        '''
        Проверка доступа к команде бота для пользователя

        Args:
            endpoint_name (str): Название ручки
            user_model (UserModel): SQLAlchemy-модель роли

        Returns:
            bool: `True` - доступ есть, `False` - доступа нет

        Raises:
            WasNotCreatedError: Ограничение доступа к команде бота \
                по ролям не было создано
            ForbiddenError: Доступ запрещен
            NotFoundError: Ручка не найдена
        '''
        endpoint: BotCommandModel = await self.botcommand_service.get({
            "name": endpoint_name
        })
        if user_model is None:
            raise UnauthorizedError("Вы неавторизованы")

        filter = {
            "endpoint_id": endpoint.id,
            "role_id": user_model.role.id
        }
        exists = await self.exists(filter, raise_exc=False)
        if raise_exc and not exists:
            raise ForbiddenError('Доступ запрещен')
        else:
            return exists
