import multiprocessing as mp
import glob

from dataclasses import dataclass
from typing import Tuple
from PyQt5.QtCore import QDate
from pathlib import Path as PythonPath



@dataclass
class Titles:
    GUTEBERG_BOOKS_TAB_TITLE: str = "Books"
    CORPUS_SETTINGS_TAB_TITLE: str = "Corpus settings"
    BOOKS_TABLE_COLUMNS: Tuple[str] = (
        "Download", 
        "Tags",
        "ID", 
        "Issued",
        "Language", 
        "Authors", 
        "Title"
        )
    BOOK_ID_COL: int = 2
    TAGS_COL: int = 1

@dataclass
class Path:
    MAIN_FORM_UI_PATH: str = "ui/qt_forms/main_form.ui"
    GUTENBERG_BOOKS_UI_PATH: str = "ui/qt_forms/gutenberg_books_form.ui"
    CORPUS_UI_PATH: str = "ui/qt_forms/corpus_form.ui"
    DATASET_PATH: str = "texts/dataset/{0}"
    USER_BOOKS: str = "texts/user_books/{0}"

    
    EXISTING_BOOKS = frozenset(glob.glob(f"{DATASET_PATH.format('')}/*.txt"))
    EXISTING_TITLES = frozenset([PythonPath(text).stem for text in EXISTING_BOOKS]) 

@dataclass
class Images:
    X_BTN_SIZE: int = 32
    Y_BTN_SIZE: int = 32
    

    X_IMG_SIZE: int = 16
    Y_IMG_SIZE: int = 16

    DOWNLOAD_ICON: str = "ui/images/download_icon.png"
    INFO_ICON: str = "ui/images/info.png"

@dataclass
class Constants:
    IDS_REGEX: int = "[1-9][0-9]*"
    ANY: str = "%"
    CURRENT_L_DATE: QDate = QDate(1971, 12, 1)
    CURRENT_R_DATE: QDate = QDate(2023, 4, 1)
    SPACY_MODELS: Tuple[str] = ("en_core_web_sm", "en_core_web_md", "en_core_web_lg")
    CORES: int = mp.cpu_count()
    BATCH_SIZE: int = 3
    GUTENBERG_TOP_30_BOOKS: str = "https://www.gutenberg.org/browse/scores/top#books-last30"

    LANGUAGES: tuple = ("en", "ru")
    TRANSLATION_METHODS = {
        "googletrans": "https://pypi.org/project/googletrans/",
        "argotranslate": "https://github.com/argosopentech/argos-translate",
        "fairseq": "https://github.com/facebookresearch/fairseq#pre-trained-models-and-examples"
    }
    
    SPLIT_METHODS: tuple = ("by paragraph", "by sentence")
