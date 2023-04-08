from dataclasses import dataclass

# https://mirror2.sandyriver.net/pub/gutenberg/2/5/0/1/25018/25018-h/


@dataclass
class Titles:
    GUTEBERG_BOOKS_TAB_TITLE: str = "Books"


@dataclass
class Path:
    MAIN_FORM_UI_PATH: str = "ui/qt_forms/main_form.ui"
    GUTENBERG_BOOKS_UI_PATH: str = "ui/qt_forms/gutenberg_books_form.ui"
