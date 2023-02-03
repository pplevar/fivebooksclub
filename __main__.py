import os

from livelib_scrapper.scrapper import find_book
import pandas as pd

DATA_FILE_PATH = 'resources/initial.xlsx'


def get_book_links():
    in_df = pd.read_excel(DATA_FILE_PATH)
    for index, row in in_df.iterrows():
        if str(row['WorkLink']) == 'nan':
            book = find_work(row)
            if book:
                row['WorkTitle'] = book['name']
                row['WorkLink'] = book['link']
                row['WorkAuthors'] = book['author']
                in_df.loc[index] = row
                in_df.to_excel(DATA_FILE_PATH, index=False)


def find_work(row):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\n\n{row['Title']} [{row['Author']}]\n")

    books = find_book(f"{row['Title']} {row['Author']}")
    i = 0
    for book in books:
        i += 1
        print(f"[{i}]\t[{book['author']}]\t{book['name']}")

    chosen = int(input("Choose [0] Exit: "))
    if chosen == 0:
        return None
    else:
        return books[chosen-1]


get_book_links()
