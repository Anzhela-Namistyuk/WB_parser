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
    if len(stuff_list) < 2:
        inf_stuff = message.text
        stuff_list.append(inf_stuff)
    if len(stuff_list) == 1:
        if stuff_list[0].isdigit():
            await message.answer('Введите наименование товара! \n'
                                 'Пример: Омега 3')
        else:
            await message.answer('Введите артикул товара! \n'
                                 'Пример: 37260674')
    elif len(stuff_list) == 2:
        articul = stuff_list.pop(0)
        product = stuff_list.pop(0)
        if not articul.isdigit() and product.isdigit():
            articul, product = product, articul
        elif articul.isdigit() and product.isdigit():
            await message.answer('Вы два раза ввели номер артикула!!! \n'
                                 'Введите по очереди артикул затем наименование \n '
                                 'Пример: \n'
                                 '37260674 \n'
                                 'Затем \n'
                                 'Омега 3')
        elif not articul.isdigit() and not product.isdigit():
            await message.answer('Вы два раза ввели название товара!!! \n'
                                 'Введите по очереди артикул затем наименование \n '
                                 'Пример: \n'
                                 '37260674 \n'
                                 'Затем \n'
                                 'Омега 3')
        else:
            try:
                product = str(product)
                articul = int(articul)
                await message.answer('Начался поиск товара!')
                answer_after_pars = await pars_product_wb(product, articul)
                await message.answer(answer_after_pars)

            except Exception:
                await message.answer('Попробуйте ввести заново информацию\n'
                                     'Пример: 37260674\n'
                                     'или\n'
                                     'Пример: Омега 3')
