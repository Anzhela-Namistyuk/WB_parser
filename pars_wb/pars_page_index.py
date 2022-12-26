import asyncio
import logging

import aiohttp
import json

from pars_wb.constants import URL
from pars_wb.configs import configure_logging
from pars_wb.exception import ErrorSearch


class PagePositionProduct:

    def __init__(self, product, id_product):
        self.product = product
        self.id_product = id_product
        self.start_page = 2
        self.failure = None
        self.success = None

    async def make_request(self, page):
        """
        Делает запрос. Если возникла ошибка,
        делает повторный запрос.
        Возвращает ответ."""
        params = {
                  'dest': '-1029256,-51490,12358257,123585482',
                  'page': f'{page}',
                  'query': f'{self.product}',
                  'resultset': 'catalog',
                  'sort': 'popular',
                  'suppressSpellcheck': 'false'
                  }

        async with aiohttp.ClientSession() as session:
            try:
                resp = await session.get(url=URL, params=params)
            except Exception as e:
                logging.info(
                    f'Возникла ошибка соединения {e} при запросе по адресу {URL} страница {page}'
                )
                resp = await session.get(url=URL,  params=params)
            return resp

    async def get_page_to_products(self, page):
        """
        Получает ответ со страницы,
        находит данные о продукции, записывает ответ
        в переменную self.success если товар нашелся,
        если товар не нашелся или товаров с таким названием
        не существует, то ответ записывает в self.failure.
        """
        resp = await self.make_request(page)
        logging.info('Ответ с сайта получен')

        try:
            text = await resp.text()
            logging.info(f'Текст ответа со страницы {page} получен')
            dict_resp = json.loads(text)
            data = dict_resp.get('data')
            if not data:
                logging.info(f'Данных нет')
                if page > 1:
                    self.failure = (f'Товар "{self.product}" с артиклем '
                                    f'{self.id_product} не был найден')
                else:
                    self.failure = (f'Не было найдено ни одного'
                                    f' товара "{self.product}"')

                raise ErrorSearch('ErrorSearch')

            logging.info(f'Данные есть')
            products = data.get('products')

            if not products:
                logging.info(f'Товаров нет')
                self.failure = f'Такого товара "{self.product}" нет'
                return

            position = self.get_positions(products)

            if position:
                self.success = (f'Товар "{self.product}" артикул - {self.id_product} '
                                f'находится на странице {page} позиция {position}')

        except Exception as e:
            logging.error('Ошибка', e)
            logging.info(
                f'Поиск товара "{self.product}" '
                f'не дал результатов. Страница {page}')

    def get_positions(self, products_on_page):
        """
        Поиск товара на странице с заданным артиклем.
        Если такой находится, то возвращает номер его позиции.
        """
        for index, product in enumerate(products_on_page):
            id_product = product.get('id')
            if id_product == self.id_product:
                position = index + 1
                return position

    async def get_by_ten_page(self, end_page):
        """
        Создает очередь для обработки 10 страниц.
        """
        task_list = []
        for page in range(self.start_page, end_page):
            task = asyncio.create_task(self.get_page_to_products(page))
            task_list.append(task)
        await asyncio.gather(*task_list)

    async def search_id(self):
        """
        Запускает поиск товара сначала
        по первой странице, для проверки,
        что по данному товару есть данные,
        если данные есть, то запускает поиск товаров
        по каждым 10-и страницам. Если на первых 100
        страницах не был найден товар, то записывает ответ
        в self.failure.
        """
        await self.get_page_to_products(1)
        logging.info(f'Обработана 1 страница')
        if self.success or self.failure:
            return
        while self.start_page < 101:
            end_page = self.start_page + 5
            await self.get_by_ten_page(end_page)
            logging.info(f'Обработано {end_page} страниц')
            if self.success or self.failure:
                return
            self.start_page = end_page
        self.failure = (f'Товара {self.product} с артикулом - {self.id_product} '
                        f'нет на первых 100 страницах поиска')


async def pars_product_wb(product, id_product):
    configure_logging()
    logging.info('Парсер запущен!')

    product = PagePositionProduct(product, id_product)
    logging.info(f'Класс PagePositionProduct - имеет '
                 f'товар {product.product},'
                 f' артикул {product.id_product}')
    await product.search_id()

    logging.info('Парсер завершил работу.')
    return product.success if product.success else product.failure
