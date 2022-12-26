import logging

from aiogram import Router
from aiogram import types

from pars_wb import pars_product_wb
from pars_wb.configs import configure_logging

router = Router()

configure_logging()


class ItemDescription:
    product = None
    item_code = None

    def __str__(self):
        return f'{self.product}, {self.item_code}'


ITEM_DESCRIPTION = ItemDescription()


START_MESSAGE = ('Введите артикул или наименование товара! \n'
                 'Пример: 37260674 \n'
                 'или \n'
                 'Пример: Омега 3')


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
    await message.answer('Привет!')
    await message.answer(START_MESSAGE)


@router.message(content_types="text")
async def answer_about_stuff(message: types.Message):
    text_answer = {'product': 'Введите наименование товара! \n'
                              'Пример: Омега 3',
                   'item_code': 'Введите артикул товара! \n'
                                'Пример: 37260674'

                   }

    inf_stuff = message.text

    if not ITEM_DESCRIPTION.item_code and inf_stuff.isdigit():
        ITEM_DESCRIPTION.item_code = int(inf_stuff)

    elif not ITEM_DESCRIPTION.product:
        ITEM_DESCRIPTION.product = inf_stuff
    logging.debug(f'{ITEM_DESCRIPTION.product} , {ITEM_DESCRIPTION.item_code}')

    if not ITEM_DESCRIPTION.product and not ITEM_DESCRIPTION.item_code:
        await message.answer(text_answer['product'])

    elif not ITEM_DESCRIPTION.item_code:
        await message.answer(text_answer['item_code'])

    elif not ITEM_DESCRIPTION.product:
        await message.answer(text_answer['product'])
    else:
        await message.answer('Начался поиск товара!')
        try:

            answer_after_pars = await pars_product_wb(
                ITEM_DESCRIPTION.product, ITEM_DESCRIPTION.item_code
            )
            await message.answer(answer_after_pars)

        except Exception as e:
            logging.info(f'Произошла ошибка{e}')
            await message.answer('Попробуйте ввести заново информацию\n'
                                 'Пример: 37260674\n'
                                 'или\n'
                                 'Пример: Омега 3')

        ITEM_DESCRIPTION.item_code = None
        ITEM_DESCRIPTION.product = None
        await message.answer(START_MESSAGE)

