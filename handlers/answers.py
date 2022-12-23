from aiogram import Router
from aiogram import types

from pars_wb import pars_product_wb

router = Router()
stuff_list = []


@router.message(commands=["description"])
async def cmd_special_buttons(message: types.Message):
    await message.answer('Бот вводит в поисковую строку наименование товара \n'
                         'и по артикулу находит его положение на странице поиска\n'
                         'Введите артикул или наименование товара! \n'
                         'Пример: 37260674 \n'
                         'или \n'
                         'Пример: Омега 3')


@router.message(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer('Привет! Введите артикул или наименование товара! \n'
                         'Пример: 37260674 \n'
                         'или \n'
                         'Пример: Омега 3')


@router.message(content_types="text")
async def answer_about_stuff(message: types.Message):
    text_answer = {'product': 'Введите наименование товара! \n'
                              'Пример: Омега 3',
                   'articul': 'Введите артикул товара! \n'
                              'Пример: 37260674'

                   }

    inf_stuff = message.text
    if not len(stuff_list):
        if inf_stuff.isdigit():
            int(inf_stuff)
            await message.answer(text_answer['product'])
        else:
            str(inf_stuff)
            await message.answer(text_answer['articul'])

            stuff_list.append(inf_stuff)

    elif len(stuff_list) == 1:
        if isinstance(stuff_list[0], int) and not inf_stuff.isdigit():
            stuff_list.append(str(inf_stuff))
            await message.answer('Начался поиск товара!')
        elif isinstance(stuff_list[0], str) and inf_stuff.isdigit():
            stuff_list.append(int(inf_stuff))
            stuff_list[0], stuff_list[1] = stuff_list[1], stuff_list[0]
            await message.answer('Начался поиск товара!')
        elif isinstance(stuff_list[0], int):
            await message.answer(text_answer['product'])
        else:
            await message.answer(text_answer['articul'])

    if len(stuff_list) == 2:

        articul = stuff_list.pop(0)
        product = stuff_list.pop(0)

        try:
            answer_after_pars = await pars_product_wb(product, articul)
            await message.answer(answer_after_pars)

        except Exception:
            await message.answer('Попробуйте ввести заново информацию\n'
                                 'Пример: 37260674\n'
                                 'или\n'
                                 'Пример: Омега 3')
