import re
from collections import defaultdict
import math

from lxml import html, etree
from .book import Book
from .page_loader import download_page, wait_for_delay

def error_handler(where, raw):
    """
    Обработчик ошибки при парсинге html страницы
    :param where: string - что не распарсилось
    :param raw: html-узел
    :return: None
    """
    print('ERROR: Parsing error (%s not parsed):' % where)
    print(etree.tostring(raw))
    print()
    return None


def try_get_book_link(link):
    """
    Проверяет валидность ссылки на книгу
    :param link: string - ссылка
    :return: string or None
    """
    if "/book.py/" in link or "/work/" in link:
        return link
    return None


def try_parse_month(raw_month):
    """
    Возвращает месяц в нужном виде
    :param raw_month: string - месяц в текстовом виде
    :return: string - месяц в цифровом виде
    """
    dict = defaultdict(lambda: '01', {
        'Январь': '01',
        'Февраль': '02',
        'Март': '03',
        'Апрель': '04',
        'Май': '05',
        'Июнь': '06',
        'Июль': '07',
        'Август': '08',
        'Сентябрь': '09',
        'Октябрь': '10',
        'Ноябрь': '11',
        'Декабрь': '12'
    })
    return dict[raw_month]


def is_last_page(page):
    """
    Проверяет, что на странице уже пустой список объектов (она последняя)
    :param page: страница
    :return: bool
    """
    return bool(len(page.xpath('//div[@class="with-pad"]')))


def is_redirecting_page(page):
    """
    Проверяет, что страница является перенаправляющей
    :param page: страница
    :return: bool
    """
    flag = bool(len(page.xpath('//div[@class="page-404"]')))
    if flag:
        print('ERROR: Oops! Livelib suspects that you are a bot! Reading stopped.')
        print()
    return flag


def href_i(href, i):
    """
    Возвращает ссылку на i-ую страницу данного типа
    :param href: string - ссылка на страницу
    :param i: int - номер страницы
    :return: string - нужная ссылка
    """
    return href + '/~' + str(i)


def date_parser(date):
    """
    Конвертирует дату в нужный формат
    :param date: string
    :return: string or None
    """
    m = re.search('\d{4} г.', date)
    if m is not None:
        year = m.group(0).split(' ')[0]
        raw_month = date.split(' ')[0]
        month = try_parse_month(raw_month)
        return '%s-%s-01' % (year, month)
    return None


def handle_xpath(html_node, request, i=0):
    """
    Обертка над xpath. Возвращает i-ый найденный узел. Если он не нашелся, то возвращается None
    :param html_node: html-узел
    :param request: string - xpath запрос
    :param i: int - индекс (по дефолту 0)
    :return: нужный html-узел или None
    """
    if html_node is None:
        return None
    tmp = html_node.xpath(request)
    return tmp[i] if i < len(tmp) else None


def book_parser(book_html, date=None, status=None):
    """
    Парсит html-узел с книгой
    :param book_html: html-узел с книгой
    :param date: string or None - дата прочтения
    :param status: string - статус книги
    :return: Book or None
    """
    book_data = handle_xpath(book_html, './/div/div/div[@class="brow-data"]/div')
    if book_data is None:
        return error_handler('book_data', book_html)

    book_name = handle_xpath(book_data, './/a[contains(@class, "brow-book.py-name")]')
    link = try_get_book_link(book_name.get("href"))  # в аргументах лежит ссылка
    if link is None:
        return error_handler('link', book_html)
    name = None if book_name is None else book_name.text

    author = book_data.xpath('.//a[contains(@class, "brow-book.py-author")]/text()')
    if len(author):
        author = ', '.join(author)  # в случае нескольких авторов нужно добавить запятые

    rating = None
    if status == 'read':
        rating = handle_xpath(book_data, './/div[@class="brow-ratings"]/span/span/span/text()')

    return Book(link, status, name, author, rating, date)


def slash_add(left, right):
    return left + '/' + right


def get_books(user_href, status, page_count=math.inf, min_delay=30, max_delay=60):
    """
    Возвращает список книг (классов Book)
    :param user_href: string - ссылка на пользователя
    :param status: string - статус книг
    :param page_count: int or float - количество страниц, которые нужно обработать (по дефолту бесконечность)
    :param min_delay: int - минимальное время задержки между запросами (по дефолту 30)
    :param max_delay: int - максимальное время задержки между запросами (по дефолту 60)
    :return: list - список классов Book
    """
    books = []
    href = slash_add(user_href, status)
    page_idx = 1

    while page_idx <= page_count:
        wait_for_delay(min_delay, max_delay)

        # если происходит какая-то ошибка с подключением, переходим к следующей странице
        try:
            page = html.fromstring(download_page(href_i(href, page_idx)))
        except Exception:
            continue
        finally:
            page_idx += 1

        if is_last_page(page) or is_redirecting_page(page):
            break

        last_date = None
        for div_book_html in page.xpath('.//div[@id="booklist"]/div'):
            date = handle_xpath(div_book_html, './/h2/text()')
            if date is not None:
                date = date_parser(date)
                if status == 'read' and date is not None:
                    last_date = date
            else:
                book = book_parser(div_book_html, last_date, status)
                if book is not None:
                    books.append(book)

    return books


def search_result_book_parser(book_html):
    book = {}
    book_data = handle_xpath(book_html, './/div[@class="ll-redirect-book"]/div')
    if book_data is None:
        return None
        # return error_handler('book_data', book_html)

    book_name = handle_xpath(book_data, './/div[@class="brow-title"]/a')
    book['link'] = f'https://livelib.ru{book_name.get("href")}'  # в аргументах лежит ссылка
    book['name'] = None if book_name is None else book_name.text

    author = book_data.xpath('.//a[contains(@class, "description")]/text()')
    if len(author):
        author = ', '.join(author)  # в случае нескольких авторов нужно добавить запятые
    book['author'] = author

    return book



def find_book(search_text):
    """
    Возвращает список книг (классов Book)
    :param search_text: string - поисковый запрос
    :return: list - список классов Book
    """
    books = []

    # если происходит какая-то ошибка с подключением, переходим к следующей странице
    try:
        page = html.fromstring(download_page(f"https://www.livelib.ru/find/{search_text}"))
    except Exception as e:
        print(f"There is exception fired: {e}")
        return None

    for div_book_html in page.xpath('.//div[@id="objects-block"][2]/div'):
        book = search_result_book_parser(div_book_html)
        if book is not None:
            books.append(book)
    for div_book_html in page.xpath('.//div[@id="objects-block"][1]/div'):
        book = search_result_book_parser(div_book_html)
        if book is not None:
            books.append(book)

    return books


def get_book_meta(row):
    meta = {}
    doc = download_page(row['WorkLink'], title_contains=row['WorkTitle'])
    if doc is None:
        return None

    doc.strip()
    page = html.fromstring(doc)

    genres = []
    for genre_a in page.xpath("//*[contains(text(), ' Жанры:')]/a"):
        genre = genre_a.text
        if '№' in genre:
            genre = genre[genre.find("в") + 2:]
        genres.append(genre)

    rating = page.xpath('//div[@class="bc-rating"]/a/span')[0].text.strip()
    meta['genres'] = genres
    meta['rating'] = rating

    return meta
