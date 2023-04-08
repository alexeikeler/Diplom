from PyQt5 import uic

from src.forms_code.gutenberg_books_form import GutenbergBooksForm
from config.settings import Path, Titles


main_form, main_base = uic.loadUiType(uifile=Path.MAIN_FORM_UI_PATH)


class MainForm(main_form, main_base):

    def __init__(self):

        super(main_base, self).__init__()
        self.setupUi(self)

        self.tab_widget.addTab(GutenbergBooksForm(), Titles.GUTEBERG_BOOKS_TAB_TITLE)
