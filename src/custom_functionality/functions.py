import glob
import itertools
from typing import Iterable, List, Tuple, FrozenSet
from pathlib import Path as PythonPath
from config.settings import Path


def partition(l: List, size: int) -> Iterable:
    for i in range(0, len(l), size):
        yield list(itertools.islice(l, i, i + size))

def get_books_and_titles(path: str = "") -> Tuple[FrozenSet[str], FrozenSet[str]]:

    books = frozenset(glob.glob(f"{Path.DATASET_PATH.format(path)}/*.txt"))
    
    titles = frozenset([PythonPath(text).stem for text in books]) 
    
    return books, titles
