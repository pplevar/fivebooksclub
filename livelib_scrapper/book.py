def handle_none(none):
    """
    Возвращет пустую строку, если объект является None, сам объект иначе
    :param none: any class - какой-то объект
    :return: param class or string
    """
    return '' if none is None else none


def add_livelib(link):
    """
    Добавляет доменное имя к ссылке, взятой из внутренностей HTML-кода, где доменное имя опускается
    :param link: string - ссылка, начинается с '/'
    :return: string - полноценная ссылка, к которой можно обращаться
    """
    ll = 'https://www.livelib.ru'
    return link if ll in link else ll + link


class Book:
    def __init__(self, link=None, status=None, name=None, author=None, rating=None, date=None):
        self.name = handle_none(name)
        self.author = handle_none(author)
        self.status = handle_none(status)
        self.rating = handle_none(rating)
        self.date = handle_none(date)
        self.link = add_livelib(handle_none(link))

    def __str__(self):
        return '%s\t%s\t%s\t%s\t%s\t%s' % (self.name, self.author, self.status, self.rating, self.date, self.link)

    def __eq__(self, other):
        return self.link == other.link

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_list(self):
        return self.__dict__.values()

    def add_name(self, name):
        self.name = name

    def add_author(self, author):
        self.author = author