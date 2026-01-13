from dependencies import get_db, get_user_service, get_role_service, get_botcommand_service
from botcommand.models.model import BotCommandModel
from botcommand.schemas.schema import BotCommandSimpleSchema
from user.schemas.schema import UserSimpleSchema
from user.models.model import UserModel
from role.schemas.schema import RoleSchema
from role.models.model import RoleModel


async def fill_db():
    bot_commands = [
        'start',
        'find',
        'parse',
    ]
    admins = [
        {
            'id': 788177685,
            'user_name': '@oselish',
            'role_id': 1,
        },
        {
            'id': 6508357756,
            'user_name': '@alexey2003petrov',
            'role_id': 1,
        },
    ]
    roles = [
        {
            'id': 1,
            'name': 'admin'
        },
        {
            'id': 2,
            'name': 'user'
        },
    ]
    async for db in get_db():
        user_service = await get_user_service(db)
        role_service = await get_role_service(db)
        botcommand_service = await get_botcommand_service(db)
        for bc in bot_commands:
            await botcommand_service.create(
                BotCommandModel.from_schema(BotCommandSimpleSchema(name=bc))
            )
        for r in roles:
            await role_service.create(
                RoleModel.from_schema(RoleSchema(**r))
            )
        for adm in admins:
            await user_service.create(
                UserModel.from_schema(UserSimpleSchema(**adm))
            )
