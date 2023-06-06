import os
from typing import List, Set

import gutenbergpy.textget
import requests
from bs4 import BeautifulSoup
from PyQt5 import QtCore

from config.settings import Constants
from src.custom_functionality import message_boxes as msg


class BooksDownloader:
    def __init__(self) -> None:

        self._ulr = Constants.GUTENBERG_TOP_30_BOOKS

    def _get_ids(self, top_n: int) -> Set[int]:

        try:
            soup = BeautifulSoup(requests.get(self._ulr).text, "lxml")

        except Exception as e:
            msg.error_message(f"Scrape error. Text:\n{repr(e)}")
            return

        # List with top 100 books (30 days)
        books = soup.find_all("ol")[-2].find_all("a")
        ids = set()

        # Get href text (/ebooks/some_number),
        # split by "/", return the last element (book id)
        for i in range(top_n):
            ids.add(books[i]["href"].split("/")[-1])

        return ids

    @staticmethod
    def download_book(book_id: List[int] | Set[int], path: str):
        try:
            raw = gutenbergpy.textget.get_text_by_id(book_id)
            cleaned = gutenbergpy.textget.strip_headers(raw)
            cleaned = cleaned.decode("utf-8")
            book_path = path.format(f"{book_id}.txt")

            with open(book_path, "w+") as f:
                f.write(cleaned)

            os.remove(f"texts/{book_id}.txt.gz")

            if os.path.exists(book_path):
                msg.info_message(f"Book {book_id} has been downloaded.")

        except Exception as e:
            msg.info_message(
                f"Skipping book {book_id} due to occured error:\n{repr(e)}"
            )

    @staticmethod
    def download_books(ids: Set[int], path: str, text_edit):

        for book_id in ids:

            try:
                text_edit.append(f"Downloadig book: {str(book_id)}")

                raw = gutenbergpy.textget.get_text_by_id(book_id)
                cleaned = gutenbergpy.textget.strip_headers(raw)
                cleaned = cleaned.decode("utf-8")
                book_path = path.format(f"{book_id}.txt")

                with open(book_path, "w+") as f:
                    f.write(cleaned)

                os.remove(f"texts/{book_id}.txt.gz")

                if os.path.exists(book_path):
                    text_edit.append(f"Book {book_id} has been downloaded.\n")
                    QtCore.QCoreApplication.processEvents()

            except Exception as e:
                text_edit.append(
                    f"Skipping book {book_id} due to occured error:\n{repr(e)}\n"
                )
                QtCore.QCoreApplication.processEvents()

