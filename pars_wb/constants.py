from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

URL = 'https://search.wb.ru/exactmatch/ru/common/v4/search?'
HEADERS = {
    "Accept": "*/*",
    "User-Aget": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                 "(KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}