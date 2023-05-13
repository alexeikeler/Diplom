import time
import glob
import itertools

from functools import wraps
from pathlib import Path as PythonPath
from typing import FrozenSet, Iterable, List, Tuple

from config.settings import Path


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def timeit(func):

    @wraps(func)
    def timeit_wrapper(*args, **kwargs):

        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time

        print(f'Function {func.__name__}, took {total_time:.4f} seconds.')

        return result

    return timeit_wrapper


def partition(l: List, size: int) -> Iterable:
    for i in range(0, len(l), size):
        yield list(itertools.islice(l, i, i + size))


def get_books_and_titles(path: str = "") -> Tuple[FrozenSet[str], FrozenSet[str]]:

    books = frozenset(glob.glob(f"{Path.DATASET_PATH.format(path)}/*.txt"))

    titles = frozenset([PythonPath(text).stem for text in books])

    return books, titles


def write_file(file_name: str, text: str, mode: str) -> None:
    with open(file_name, mode) as user_out_file:
        user_out_file.write(text)

