import asyncio
import logging

import aiohttp
import json

from pars_wb.constants import URL, HEADERS
from pars_wb.configs import configure_logging
from pars_wb.exception import ErrorSearch


class PagePositionProduct:

    def __init__(self, product, id_product):
        self.product = product
        self.id_product = id_product
        self.start_page = 2
        self.answer = None

    async def make_request(self, page):
        params = {'appType': '1', 'couponsGeo': '2,12,3,18,15,21', 'curr': 'rub',
                  'dest': '-1029256,-51490,12358257,123585482', 'emp': '0', 'lang': 'ru',
                  'locale': 'ru', 'page': f'{page}', 'pricemarginCoeff': '1.0', 'query': f'{self.product}',
                  'reg': '1', 'regions': '80,64,83,4,38,33,70,82,69,68,86,75,30,40,48,1,22,66,31,71',
                  'resultset': 'catalog', 'sort': 'popular', 'spp': '30', 'sppFixGeo': '4',
                  'suppressSpellcheck': 'false'}

        async with aiohttp.ClientSession() as session:
            try:
                resp = await session.get(url=URL, headers=HEADERS, params=params)
            except Exception as e:
                logging.info(
                    f'Возникла ошибка соединения {e} при запросе по адресу {URL} страница {page}'
                )
                resp = await session.get(url=URL, headers=HEADERS, params=params)
            return resp

    async def get_page_to_products(self, page):
        resp = await self.make_request(page)

        try:
            text = await resp.text()
            dict_resp = json.loads(text)
            data = dict_resp.get('data')
            if not data:
                if page > 1:
                    self.answer = (f'Товар "{self.product}" с артиклем '
                                   f'{self.id_product} не был найден')
                else:
                    self.answer = f'Не было найдено ни одного товара "{self.product}"'

                raise ErrorSearch('ErrorSearch')

            products = data.get('products')
            position = await self.get_positions(products)
            if position:
                self.answer = (f'Товар "{self.product}" артикул - {self.id_product} '
                               f'находится на странице {page} позиция {position}')

        except Exception as e:
            logging.info(e)
            logging.info(
                f'Поиск товара "{self.product}" '
                f'не дал результатов. Страница {page}')

    async def get_positions(self, products_on_page):
        for index, product in enumerate(products_on_page):
            id_product = product.get('id')
            if id_product == self.id_product:
                position = index + 1
                return position

    async def get_by_ten_page(self, end_page):
        task_list = []
        for page in range(self.start_page, end_page):
            task = asyncio.create_task(self.get_page_to_products(page))
            task_list.append(task)
            await asyncio.gather(*task_list)

    async def search_id(self):

        await self.get_page_to_products(1)
        if self.answer:
            return
        while self.start_page < 101:
            end_page = self.start_page + 10
            await self.get_by_ten_page(end_page)
            if self.answer:
                return
            self.start_page = end_page
        self.answer = (f'Товара {self.product} с артикулом - {self.id_product} '
                       f'нет на первых 100 страницах поиска')


async def pars_product_wb(product, id_product):
    configure_logging()
    logging.info('Парсер запущен!')
    logging.info(f'Поиск {product} {id_product}')

    product = PagePositionProduct(product, id_product)
    await product.search_id()

    logging.info('Парсер завершил работу.')
    return product.answer
