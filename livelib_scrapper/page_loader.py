import time
import random
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def download_page(link, title_contains='Результаты поиска'):
    """
    Скачивает страницу
    :param link: string - ссылка на страницу
    :return: string? - тело страницы
    """
    from __main__ import driver
    driver.get(link)
    try:
        # WebDriverWait(driver, 5).until(
        #     EC.title_contains(title_contains)
        # )
        from selenium.webdriver.common.by import By
        WebDriverWait(driver, 7).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bc-info__wrapper"))
        )
        return driver.page_source.encode('utf-8')
    except:
        return None



def wait_for_delay(min_delay, max_delay=-1):
    """
    Останавливает программу на некоторое число секунд. Нужна, чтобы сайт не распознал в нас бота
    :param min_delay: int - минимальное число секунд
    :param max_delay: int - максимальное число секунд
    """
    if max_delay == -1:
        delay = min_delay
    elif max_delay < min_delay:
        delay = max_delay
    else:
        delay = random.randint(min_delay, max_delay)
    print("Waiting %s sec..." % delay)
    time.sleep(delay)
