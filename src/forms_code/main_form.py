import os
import webbrowser
from functools import partial

from PyQt5 import QtCore, QtGui, QtWidgets, uic

import src.custom_functionality.custom_widgets as custom_qt_widgets
from config.settings import Constants, Path, Titles
from src.custom_functionality import message_boxes as msg

from src.forms_code.basic_translation_form import BasicTranslationTabForm
from src.forms_code.cefr_efllex_form import CefrEfllexTabForm
from src.forms_code.rake_tab_form import RakeTabForm

from src.translation_methods import Translators
from src.translation_methods import CefrAndEfllexMethod
from src.translation_methods import RakeMethod
from src.translation_methods import BasicTranslationMethod


from src.forms_code.gutenberg_books_form import GutenbergBooksForm
#from src.forms_code.corpus_form import CorpusForm


main_form, main_base = uic.loadUiType(uifile=Path.MAIN_FORM_UI_PATH)


class MainForm(main_form, main_base):
    def __init__(self):

        super(main_base, self).__init__()
        self.setupUi(self)
        
        # Add other tabs to main form
        self.tab_widget.addTab(GutenbergBooksForm(), Titles.GUTEBERG_BOOKS_TAB_TITLE)
        #self.tab_widget.addTab(CorpusForm(), Titles.CORPUS_SETTINGS_TAB_TITLE)

        # Add other tabs to key-word extraction methods
        # and connect their buttons

        self.translation_algorithms_tab_widget.clear()

        # Basic translation tab
        self.basic_translation_tab = BasicTranslationTabForm()
        self.basic_translation_tab.apply_basic_translation_button.clicked.connect(
            self.apply_basic_translation_button_clicked
        )
        self.basic_translation_tab.info_basic_translation_button.clicked.connect(
            self.info_basic_translation_button_clicked
        )
        self.basic_translation_tab.default_basic_translation_button.clicked.connect(
            self.default_basic_translation_button_clicked
        )
        self.translation_algorithms_tab_widget.addTab(self.basic_translation_tab, "Basic translation")


        # CEFR AND EFLLEX tab
        self.cefr_efllex_tab = CefrEfllexTabForm()
        self.cefr_efllex_tab.apply_cefr_efllex_button.clicked.connect(
            self.apply_cefr_efllex_button_clicked
        )
        self.cefr_efllex_tab.info_cefr_efllex_button.clicked.connect(
            self.info_cefr_efllex_button_clicked
        )
        self.cefr_efllex_tab.default_cefr_efllex_button.clicked.connect(
            self.default_cefr_efllex_button_clicked
        )
        self.translation_algorithms_tab_widget.addTab(self.cefr_efllex_tab, "CEFR and EFLLEX")

        # RAKE tab
        self.rake_tab = RakeTabForm()
        self.rake_tab.apply_rake_button.clicked.connect(self.apply_rake_button_clicked)
        self.rake_tab.info_rake_button.clicked.connect(self.info_rake_button_clicked)
        self.rake_tab.default_rake_button.clicked.connect(
            self.default_rake_button_clicked
        )
        self.translation_algorithms_tab_widget.addTab(self.rake_tab, "RAKE")

        # Setup plain text edit
        self.preview_plain_text_edit = custom_qt_widgets.SmartPlainTextEdit(self.logger)
        self.text_output_layout.insertWidget(1, self.preview_plain_text_edit)

        # Setup file system
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath(Path.USER_BOOKS.format(""))

        self.files_tree_view.setModel(self.model)
        self.files_tree_view.setRootIndex(self.model.index(Path.USER_BOOKS.format("")))
        self.files_tree_view.setAlternatingRowColors(True)
        self.files_tree_view.setColumnWidth(0, 300)
        self.files_tree_view.doubleClicked.connect(self.show_selected_book)


        self.preview_text_button.clicked.connect(self.preview_text)
        self.open_text_button.clicked.connect(self.open_text_in_editor)


    def apply_basic_translation_button_clicked(self):
        
        spacy_model_type = self.basic_translation_tab.get_spacy_model()
        max_doc_size = self.basic_translation_tab.get_spacy_doc_size()
        tr_method = self.basic_translation_tab.get_translation_method()
        split_method = self.basic_translation_tab.get_split_method()
        src_lng, trgt_lng = self.basic_translation_tab.get_selected_languages()
        fairseq_model = self.basic_translation_tab.get_fairseq_model()
        mark_original, mark_translated = self.basic_translation_tab.get_mark_options()


        if src_lng == trgt_lng:
            msg.error_message("You have selected two identical languages!")
            return

        if tr_method == "fairseq" and "uk" in (src_lng, trgt_lng):
            msg.error_message("Current version of fairseq package doesn't support UK translation.")
            return

        filename = self.selected_text_line_edit.text()
        if not filename:
            msg.error_message("Select a file first!")
            return

        out_file_name = Path.USER_BOOKS.format(
            f"translated_texts/{filename.split('.')[0]}_basic_translation_{tr_method}_{src_lng}_to_{trgt_lng}.txt"
        )
        out_file_name = os.path.abspath(out_file_name)

        self.logger.appendPlainText("Loading translation model...")
        QtCore.QCoreApplication.processEvents()

        method = BasicTranslationMethod(
            split_method,
            spacy_model_type,
            max_doc_size
        )

        translator = Translators(
            tr_method,
            src_lng,
            trgt_lng,
            fairseq_model
        )

        method.translate(
            translator,
            filename,
            out_file_name,
            self.logger,
            mark_original,
            mark_translated
        )
                



    def info_basic_translation_button_clicked(self):
        pass

    def default_basic_translation_button_clicked(self):
        pass





    def apply_cefr_efllex_button_clicked(self):

        levels = self.cefr_efllex_tab.get_selected_levels()
        model_type = self.cefr_efllex_tab.get_spacy_model()
        nlp_max_size = self.cefr_efllex_tab.get_spacy_max_doc_size()
        batch_size = self.cefr_efllex_tab.get_batch_size()
        src_lng, trgt_lng = self.cefr_efllex_tab.get_selected_languages()


        filename = self.selected_text_line_edit.text()
        if not filename:
            msg.error_message("Select a file first!")
            return

        out_file_name = Path.USER_BOOKS.format(
            f"translated_texts/{filename.split('.')[0]}_cefr_efllex_{'_'.join(levels)}_{src_lng}_to_{trgt_lng}.txt"
        )
        out_file_name = os.path.abspath(out_file_name)

        self.logger.appendPlainText("Loading translation model...")
        QtCore.QCoreApplication.processEvents()

        method = CefrAndEfllexMethod(model_type, nlp_max_size)

        translators = Translators(
            "googletrans",
            src_lng,
            trgt_lng
        )

        self.logger.appendPlainText("Translation model have been loaded")
        QtCore.QCoreApplication.processEvents()

        method.translate(
            translators,
            filename,
            levels,
            out_file_name,
            self.logger,
            batch_size,
        )

    def info_cefr_efllex_button_clicked(self):
        pass

    def default_cefr_efllex_button_clicked(self):
        pass

    def apply_rake_button_clicked(self):
        
        max_words = self.rake_tab.get_max_value()
        min_words = self.rake_tab.get_min_value()
        ranking_method = self.rake_tab.get_ranking_method()
        allow_repeated_phrases = self.rake_tab.get_repeated_phrases()
        batch_size = self.rake_tab.get_batch_size()
        src_lng, trgt_lng = self.rake_tab.get_selected_languages()

        filename = self.selected_text_line_edit.text()
        if not filename:
            msg.error_message("Select a file first!")
            return

        out_file_name = Path.USER_BOOKS.format(
            f"translated_texts/{filename.split('.')[0]}_rake_{src_lng}_to_{trgt_lng}.txt"
        )
        out_file_name = os.path.abspath(out_file_name)

        self.logger.appendPlainText("Loading translation model...")
        QtCore.QCoreApplication.processEvents()

        translators = Translators(
            "googletrans",
            src_lng, 
            trgt_lng
        )

        self.logger.appendPlainText("Translation model have been loaded")
        QtCore.QCoreApplication.processEvents()

        method = RakeMethod(
            filename,
            out_file_name,
            Constants.SHORT_LANGS.get(src_lng),
            min_words,
            max_words,
            ranking_method,
            allow_repeated_phrases  
        )

        method.translate(translators, self.logger, batch_size)
        self.translated_text_line_edit.setText(out_file_name.split("/")[-1])

    def info_rake_button_clicked(self):
        pass

    def default_rake_button_clicked(self):
        pass

    def open_text_in_editor(self):
        text = self.translated_text_line_edit.text()
        text_file = f"/home/alex/Diplom/texts/user_books/translated_texts/{text}"

        webbrowser.open(text_file)

    def preview_text(self):

        self.preview_plain_text_edit.clear()
        text = self.translated_text_line_edit.text()

        if not text or text is None:
            msg.error_message("Select a translated text!")
            return

        text_file = Path.USER_BOOKS.format(f"translated_texts/{text}")
        with open(text_file, "r") as file:
            content = file.read()

        self.preview_plain_text_edit.appendPlainText(content)
        self.preview_plain_text_edit.moveCursor(QtGui.QTextCursor.Start)
        QtCore.QCoreApplication.processEvents()

    def show_selected_book(self, index):
        item = self.model.index(index.row(), 0, index.parent())
        file_name = self.model.fileName(item)
        file_path = self.model.filePath(item)

        if "translated_texts" in file_path:
            self.translated_text_line_edit.setText(file_name)
            return

        self.selected_text_line_edit.setText(file_name)

    def show_info(self, caller: str):
        if caller == "translation_info":
            info_about = Constants.TRANSLATION_METHODS.get(
                self.translation_method_combo_box.currentText()
            )
            webbrowser.open(info_about)
        elif caller == "split_info":
            pass
