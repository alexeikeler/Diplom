import glob
import multiprocessing as mp
from dataclasses import dataclass
from pathlib import Path as PythonPath
from typing import Tuple

from PyQt5.QtCore import QDate
from rake_nltk import Metric


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
        "Title",
    )
    BOOK_ID_COL: int = 2
    TAGS_COL: int = 1


@dataclass
class Path:
    MAIN_FORM_UI_PATH: str = "ui/qt_forms/main_form.ui"
    GUTENBERG_BOOKS_UI_PATH: str = "ui/qt_forms/gutenberg_books_form.ui"
    CORPUS_UI_PATH: str = "ui/qt_forms/corpus_form.ui"

    CEFR_EFLLEX_TAB_PATH: str = "ui/qt_forms/cefr_efllex_tab_form.ui"
    RAKE_TAB_PATH: str = "ui/qt_forms/rake_tab_form.ui"

    DATASET_PATH: str = "texts/dataset/{0}"
    USER_BOOKS: str = "texts/user_books/{0}"

    CEFR_DS_PATH: str = "texts/csv_data/full_cefr_dataset.csv"
    EFLLEX_DS_PATH: str = "texts/csv_data/efllex_dataset.csv"

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
    SPACY_MODELS: Tuple[str] = ("en_core_web_lg", "en_core_web_md", "en_core_web_sm")
    CORES: int = mp.cpu_count()
    BATCH_SIZE: int = 3
    GUTENBERG_TOP_30_BOOKS: str = (
        "https://www.gutenberg.org/browse/scores/top#books-last30"
    )

    LANGUAGES: tuple = ("en", "ru")
    TRANSLATION_METHODS = {
        "googletrans": "https://pypi.org/project/googletrans/",
        "fairseq": "https://github.com/facebookresearch/fairseq#pre-trained-models-and-examples",
    }

    SPLIT_METHODS: tuple = ("by paragraph", "by sentence")

    KEY_WORD_EXTRACTION_METHODS = {
        "CEFR and EFLLex": "cefr_and_efllex_levels_tab",
        "TF-IDF and s2v": "tfidf_and_s2v_tab",
        "RAKE": "rake_tab",
    }

    END_PUNCT: tuple = ("! ", "? ", ". ", "... ", "?", "!", "...", ".")

    RAKE_RANKING_METHODS = {
        "Deg/Freq ratio": Metric.DEGREE_TO_FREQUENCY_RATIO,
        "Word degree": Metric.WORD_DEGREE,
        "Word frequency": Metric.WORD_FREQUENCY,
    }
    SHORT_LANGS = {
        "en": "english",
        "de": "german",
        "uk": "ukrainian"
    }

    WORD_FREQ_COLUMNS = [
        "word",
        "tag",
        "A1", 
        "A2",
        "B1",
        "B2",
        "C1",
        "total",
        "A1_ds",
        "A2_ds",
        "B1_ds",
        "B2_ds",
        "C1_ds",
        "total_ds"
    ]

    SUBSET_1 = [        "A1", 
        "A2",
        "B1",
        "B2",
        "C1",
        "total",
]
    SUBSET_2 = [ "A1_ds",
        "A2_ds",
        "B1_ds",
        "B2_ds",
        "C1_ds",
        "total_ds"]
