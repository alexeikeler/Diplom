import gzip

import gutenbergpy.textget
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator

from config.settings import Constants, Images, Path, Titles
from postgres_db import postgres_database
from src.custom_functionality import message_boxes as msg
from src.custom_functionality import qt_widgets_functions
from src.words_analysis.dataset_creater import BooksDownloader

gb_form, gb_base = uic.loadUiType(uifile=Path.GUTENBERG_BOOKS_UI_PATH)


class GutenbergBooksForm(gb_form, gb_base):
    def __init__(self):

        super(gb_base, self).__init__()
        self.setupUi(self)

        self.db = postgres_database.PsqlDatabase()

        self.search_by_id_button.clicked.connect(self.get_text_by_id_button_handler)
        self.search_button.clicked.connect(self.search_by_user_input)

        self.limit_slider.valueChanged[int].connect(self._on_limit_slider_value_changed)

        self.text_id_line_edit.setValidator(
            QRegExpValidator(QRegExp(Constants.IDS_REGEX), self.text_id_line_edit)
        )

        self.l_date_edit.setDate(Constants.CURRENT_L_DATE)
        self.r_date_edit.setDate(Constants.CURRENT_R_DATE)

    #        self.table.cellClicked.connect(self.cell_was_clicked)
    #       self.books_table.cellClicked.connect(self.cell_clicked)

    def _on_limit_slider_value_changed(self, value: int) -> None:
        self.limit_label.setText(f"Limit: {value}")

    def get_title(self) -> str:
        title = self.title_line_edit.text().lower()

        if not title:
            return Constants.ANY

        return "%" + title + "%"

    def get_authors(self) -> str:
        authors = self.authors_line_edit.text()

        if not authors:
            return Constants.ANY

        # Prep name for regex: %Firstname, Lastname%

        authors = authors.rsplit(" ", 1)[::-1]
        return "%" + ", ".join(authors) + "%"

    def get_subjects(self) -> str:

        subjects = self.subject_line_edit.text().lower().split()

        if not subjects:
            return Constants.ANY

        # Form a regex: %((tag)|(tag)|...|(tag))%
        return f"%({''.join([f'({subject})|' for subject in subjects])[:-1]})%"

    def get_selected_languages(self) -> str:

        languages = {
            "ru": self.ru_check_box.isChecked(),
            "en": self.en_check_box.isChecked(),
            "ge": self.ge_check_box.isChecked(),
        }

        if not any(languages.values()):
            return Constants.ANY

        # Form a regex: (language|language|language) from selected languages
        return (
            "("
            + "".join([f"{lng}|" for lng, val in languages.items() if val])[:-1]
            + ")"
        )

    def load_data(self, data: pd.DataFrame) -> None:

        self.books_table.clear()
        self.books_table.verticalHeader().setMinimumSectionSize(30)
        rows, cols = data.shape
        qt_widgets_functions.config_table(
            self.books_table,
            rows,
            cols,
            data.columns,
            {
                0: QtWidgets.QHeaderView.ResizeToContents,
                1: QtWidgets.QHeaderView.ResizeToContents,
                2: QtWidgets.QHeaderView.ResizeToContents,
                4: QtWidgets.QHeaderView.ResizeToContents,
                5: QtWidgets.QHeaderView.ResizeToContents,
                6: QtWidgets.QHeaderView.Stretch,
            },
            enable_column_sort=True,
        )

        for i in range(rows):

            download_button = QtWidgets.QPushButton("")
            download_button.setIcon(QtGui.QIcon(Images.DOWNLOAD_ICON))
            download_button.setIconSize(
                QtCore.QSize(Images.X_IMG_SIZE, Images.Y_IMG_SIZE)
            )
            # download_button.setMaximumSize(Images.X_BTN_SIZE, Images.Y_BTN_SIZE)
            download_button.clicked.connect(self.download_button_clicked)

            # download_lay = QtWidgets.QHBoxLayout()
            # download_lay.addWidget(download_button)
            # download_lay.setAlignment(QtCore.Qt.AlignCenter)
            # download_lay.setContentsMargins(0, 0, 0, 0)

            # download_widget = QtWidgets.QWidget()
            # download_widget.setLayout(download_lay)

            tags_button = QtWidgets.QPushButton("")
            tags_button.setIcon(QtGui.QIcon(Images.INFO_ICON))
            tags_button.setIconSize(QtCore.QSize(Images.X_IMG_SIZE, Images.Y_IMG_SIZE))
            # tags_button.setMaximumSize(Images.X_BTN_SIZE, Images.Y_BTN_SIZE)

            # tags_lay = QtWidgets.QHBoxLayout()
            # tags_lay.addWidget(tags_button)
            # tags_lay.setAlignment(QtCore.Qt.AlignCenter)
            # tags_lay.setContentsMargins(0, 0, 0, 0)
            # tags_widget = QtWidgets.QWidget()
            # tags_widget.setLayout(tags_lay)

            self.books_table.setCellWidget(i, 0, download_button)
            self.books_table.setCellWidget(i, 1, tags_button)

            for j in range(2, cols):
                item = QtWidgets.QTableWidgetItem(str(data.loc[i][j]))
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.books_table.setItem(i, j, item)

    def search_by_user_input(self):

        text_author = self.get_authors()
        text_title = self.get_title()

        text_subject = self.get_subjects()
        text_languages = self.get_selected_languages()

        l_date = self.l_date_edit.date().toPyDate()
        r_date = self.r_date_edit.date().toPyDate()

        lim = self.limit_slider.value()

        data = self.db.get_texts(
            text_author, text_title, text_languages, text_subject, l_date, r_date, lim
        )

        data = pd.DataFrame(data, columns=Titles.BOOKS_TABLE_COLUMNS[1:])
        data.insert(0, Titles.BOOKS_TABLE_COLUMNS[0], None)

        self.load_data(data)

    def get_text_by_id_button_handler(self) -> None:

        text_id = self.text_id_line_edit.text()

        if not text_id:
            msg.error_message("Empty id line!")
            return

        result = self.db.get_text_by_id(int(text_id))

        if result is None:
            msg.error_message(f"Text with id {text_id} does not exist!")
            return

        data = pd.DataFrame([result], columns=Titles.BOOKS_TABLE_COLUMNS[1:])
        data.insert(0, Titles.BOOKS_TABLE_COLUMNS[0], None)

        self.load_data(data)

    def download_button_clicked(self):

        book_id = int(
            self.books_table.item(
                self.books_table.currentRow(), Titles.BOOK_ID_COL
            ).text()
        )

        BooksDownloader.download_book(book_id, Path.USER_BOOKS)
