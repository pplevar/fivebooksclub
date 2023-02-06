import ast
import os
from selenium import webdriver
from livelib_scrapper.scrapper import find_book, get_book_meta
import pandas as pd

DATA_FILE_PATH = 'resources/initial.xlsx'

import os

# os.environ['MOZ_HEADLESS'] = '1'
driver = webdriver.Chrome()


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

    if books is None:
        print('DOWNLOADING ERROR')
        return None

    if len(books) == 0:
        print('NOTHING FOUND')
        return None

    i = 0
    for book in books:
        i += 1
        print(f"[{i}]\t[{book['author']}]\t{book['name']}")

    chosen = int(input("Choose [0] Exit: "))
    if chosen == 0:
        return None
    else:
        return books[chosen - 1]


def get_books_meta():
    in_df = pd.read_excel(DATA_FILE_PATH)
    for index, row in in_df.iterrows():
        if str(row['WorkLink']) != 'nan' and str(row['Genres']) == 'nan':
            meta = get_book_meta(row)
            if meta:
                row['Genres'] = meta['genres']
                row['Rating'] = meta['rating']
                print(f"Writing META for {row['Title']}: {meta}")
                in_df.loc[index] = row
                in_df.to_excel(DATA_FILE_PATH, index=False)
            else:
                print(f"ERROR during download for: {row['Title']}")


def get_genre_stat():
    in_df = pd.read_excel(DATA_FILE_PATH)
    out_stat = []
    for index, row in in_df.iterrows():
        genres_str = row['Genres']
        if str(genres_str) != 'nan':
            genres = ast.literal_eval(genres_str)
            for genre in genres:
                out_stat.append({
                    "Requested": row["Requested"],
                    "Genre": genre
                })
    out_df = pd.DataFrame(out_stat)
    res = out_df.groupby(['Requested', 'Genre'])['Genre'].count()
    out = []
    for r in res.items():
        out.append({
            "Requested": r[0][0],
            "Genre": r[0][1],
            "Count": r[1]
        })
    pd.DataFrame(out).to_excel('resources/genre-stat.xlsx', index=False)


# get_book_links()
# get_books_meta()

get_genre_stat()

driver.quit()
