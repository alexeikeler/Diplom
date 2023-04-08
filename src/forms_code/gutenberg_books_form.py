import pandas as pd
import requests

from bs4 import BeautifulSoup
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QCheckBox, QGroupBox

from postgres_db import postgres_database
from config.settings import Path


gb_form, gb_base = uic.loadUiType(uifile=Path.GUTENBERG_BOOKS_UI_PATH)


class GutenbergBooksForm(gb_form, gb_base):

    def __init__(self):

        super(gb_base, self).__init__()
        self.setupUi(self)

        self.db = postgres_database.Database()

        self.books_table = QtWidgets.QTableWidget()
        self.box_lay = QVBoxLayout()
        self.books_table_group_box.setLayout(self.box_lay)
        self.box_lay.addWidget(self.books_table)

        self.search_by_id_button.clicked.connect(self.search_by_id_button_handler)

    def search_by_id_button_handler(self):
        text_id = self.text_id_line_edit.text()
        print("Text: ", text_id)