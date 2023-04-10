from dataclasses import dataclass
from typing import Tuple
from PyQt5.QtCore import QDate


@dataclass
class Titles:
    GUTEBERG_BOOKS_TAB_TITLE: str = "Books"
    BOOKS_TABLE_COLUMNS: Tuple[str] = (
        "Download", 
        "Tags",
        "ID", 
        "Issued",
        "Language", 
        "Authors", 
        "Title"
        )

@dataclass
class Path:
    MAIN_FORM_UI_PATH: str = "ui/qt_forms/main_form.ui"
    GUTENBERG_BOOKS_UI_PATH: str = "ui/qt_forms/gutenberg_books_form.ui"

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
    