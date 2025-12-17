from aiogram import Router, types, F

router = Router()


@router.message(F.text & F.chat.type == 'private')
async def read_message(message: types.Message):
    await message.answer(str(message.text))
