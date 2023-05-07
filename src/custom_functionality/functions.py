import glob
import itertools
from functools import wraps
from pathlib import Path as PythonPath
from typing import FrozenSet, Iterable, List, Tuple

from config.settings import Path


def partition(l: List, size: int) -> Iterable:
    for i in range(0, len(l), size):
        yield list(itertools.islice(l, i, i + size))


def get_books_and_titles(path: str = "") -> Tuple[FrozenSet[str], FrozenSet[str]]:

    books = frozenset(glob.glob(f"{Path.DATASET_PATH.format(path)}/*.txt"))

    titles = frozenset([PythonPath(text).stem for text in books])

    return books, titles


def singleton(orig_cls):
    orig_new = orig_cls.__new__
    instance = None

    @wraps(orig_cls.__new__)
    def __new__(cls, *args, **kwargs):

        nonlocal instance

        if instance is None:
            instance = orig_new(cls, *args, **kwargs)
        return instance

    orig_cls.__new__ = __new__
    return orig_cls
