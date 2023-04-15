import multiprocessing as mp
import os
import string
from typing import List, Set

import numpy as np
import pandas as pd
import gutenbergpy.textget
import requests
import spacy
from bs4 import BeautifulSoup
from sklearn.base import BaseEstimator, TransformerMixin

from config.settings import Path
from src.custom_functionality import message_boxes as msg


class BooksDownloader:
    def __init__(self) -> None:
        self._ulr: str = "https://www.gutenberg.org/browse/scores/top#books-last30"
      
    def _get_ids(self, top_n: int) -> List[int]:

        try:
            soup = BeautifulSoup(
                requests.get(self._ulr).text, 
                "lxml"
                )

        except Exception as e:
            msg.error_message(f"Scrape error. Text:\n{repr(e)}")
            return

        # List with top 100 books (30 days)
        books = soup.find_all("ol")[-2].find_all("a")
        ids = []

        # Get href text (/ebooks/some_number), 
        # split by "/", return the last element (book id)
        for i in range(top_n):
            ids.append(
                int(
                    books[i]["href"].split("/")[-1]
                )    
            )

        return ids
    
    def _get_existing_books(self):
        return os.listdir(Path.DATASET_PATH.format(""))

    @staticmethod
    def download_books(ids: List[int] | Set[int], path: str):

        for book_id in ids:
            raw = gutenbergpy.textget.get_text_by_id(book_id)
            cleaned = gutenbergpy.textget.strip_headers(raw)

            cleaned = cleaned.decode("utf-8")

            with open(path.format(f"{book_id}.txt"), "w+") as f:
                f.write(cleaned)
            
            os.remove(f"texts/{book_id}.txt.gz")


class TextPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, n_jobs=1):
        """
        Text preprocessing transformer includes steps:
            1. Punctuation removal
            2. Stop words removal
            3. Lemmatization
        n_jobs - parallel jobs to run
        """
        self.nlp = spacy.load("en_core_web_sm")
        self.n_jobs = n_jobs

    def _preprocess_part(self, part):
        return part.apply(self._preprocess_text)

    def _preprocess_text(self, text):
        doc = self.nlp(text)
        removed_punct = self._remove_punct(doc)
        removed_stop_words = self._remove_stop_words(removed_punct)
        return self._lemmatize(removed_stop_words)

    def _remove_punct(self, doc):
        return (t for t in doc if t.text not in string.punctuation)

    def _remove_stop_words(self, doc):
        return (t for t in doc if not t.is_stop)

    def _lemmatize(self, doc):
        return ' '.join(t.lemma_ for t in doc)
    
    def fit(self, X, y=None):
        return self

    def transform(self, X, *_):
        X_copy = X.copy()

        partitions = 1
        cores = mp.cpu_count()
        if self.n_jobs <= -1:
            partitions = cores
        elif self.n_jobs <= 0:
            return X_copy.apply(self._preprocess_text)
        else:
            partitions = min(self.n_jobs, cores)

        data_split = np.array_split(X_copy, partitions)
        pool = mp.Pool(cores)
        data = pd.concat(pool.map(self._preprocess_part, data_split))
        pool.close()
        pool.join()

        return data

