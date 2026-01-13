# from sqlalchemy import Table, Column, ForeignKey
# from base.model import BaseModel

# permissions_table = Table(
#     "permissions",
#     BaseModel.metadata,
#     Column("role_id", ForeignKey("roles.id"), primary_key=True),
#     Column("botcommand_id", ForeignKey("botcommands.id"), primary_key=True)
# )
