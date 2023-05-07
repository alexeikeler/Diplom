import glob
import multiprocessing as mp
import os
import re
import string
from typing import List, Set

import gutenbergpy.textget
import numpy as np
import pandas as pd
import requests
import spacy
from bs4 import BeautifulSoup
from PyQt5 import QtCore

from config.settings import Constants, Path
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


class TextPreprocessor:
    def __init__(
        self,
        remove_punct: bool,
        remove_non_alphabet: bool,
        remove_stop_words: bool,
        lemmantize: bool,
        to_lowercase: bool,
        model: str,
        n_jobs: int = 1,
    ):
        """
        Text preprocessing transformer includes steps:
            -1. To lower
            0. Remove non alphabet chrs
            1. Punctuation removal
            2. Stop words removal
            3. Lemmatization
        n_jobs - parallel jobs to run
        """

        self.remove_punct = remove_punct
        self.remove_non_alphabet = remove_non_alphabet
        self.remove_stop_words = remove_stop_words
        self.lemmantize = lemmantize
        self.to_lowercase = to_lowercase
        self.n_jobs = n_jobs

        self.nlp = spacy.load(model)

    def _preprocess_part(self, part):
        return part.apply(self._preprocess_text)

    def _preprocess_text(self, text):

        if len(text) > self.nlp.max_length:
            text = text[: self.nlp.max_length]

        if self.to_lowercase:
            text = text.lower()

        if self.remove_non_alphabet:
            text = self._remove_non_alphabet(text)

        doc = self.nlp(text)

        if self.remove_punct:
            text = self._remove_punct(doc)

        if self.remove_stop_words:
            text = self._remove_stop_words(text)

        if self.lemmantize:
            text = self._lemmatize(text)

        return text

    def _remove_non_alphabet(self, text):
        return re.sub("[^A-Za-z]+", " ", text)

    def _remove_punct(self, doc):
        return (t for t in doc if t.text not in string.punctuation)

    def _remove_stop_words(self, doc):
        return (t for t in doc if not t.is_stop)

    def _lemmatize(self, doc):
        return " ".join(t.lemma_ for t in doc)

    def transform(self, batch: pd.DataFrame):

        batch_cp = batch.copy()

        partitions = 1
        cores = mp.cpu_count()

        if self.n_jobs <= -1:
            partitions = cores
        elif self.n_jobs <= 0:
            return batch_cp.apply(self._preprocess_text)
        else:
            partitions = min(self.n_jobs, cores)

        data_split = np.array_split(batch_cp, partitions)
        pool = mp.Pool(cores)
        data = pd.concat(pool.map(self._preprocess_part, data_split))
        pool.close()
        pool.join()

        return data
