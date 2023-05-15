import os
import webbrowser
from functools import partial

from PyQt5 import QtCore, QtGui, QtWidgets, uic

import src.custom_functionality.custom_widgets as custom_qt_widgets
from config.settings import Constants, Path, Titles
from src.custom_functionality import message_boxes as msg

from src.forms_code.cefr_efllex_form import CefrEfllexTabForm
from src.forms_code.rake_tab_form import RakeTabForm

from src.translation_methods import Translators
from src.translation_methods import CefrAndEfllexMethod
from src.translation_methods import RakeMethod

from src.forms_code.gutenberg_books_form import GutenbergBooksForm
from src.forms_code.corpus_form import CorpusForm


main_form, main_base = uic.loadUiType(uifile=Path.MAIN_FORM_UI_PATH)


class MainForm(main_form, main_base):
    def __init__(self):

        super(main_base, self).__init__()
        self.setupUi(self)
        
        # Add other tabs to main form
        self.tab_widget.addTab(GutenbergBooksForm(), Titles.GUTEBERG_BOOKS_TAB_TITLE)
        self.tab_widget.addTab(CorpusForm(), Titles.CORPUS_SETTINGS_TAB_TITLE)

        # Add other tabs to key-word extraction methods
        # and connect their buttons

        self.key_word_extr_tab_widget.clear()

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
        self.key_word_extr_tab_widget.addTab(self.cefr_efllex_tab, "CEFR and EFLLEX")

        # RAKE tab
        self.rake_tab = RakeTabForm()
        self.rake_tab.apply_rake_button.clicked.connect(self.apply_rake_button_clicked)
        self.rake_tab.info_rake_button.clicked.connect(self.info_rake_button_clicked)
        self.rake_tab.default_rake_button.clicked.connect(
            self.default_rake_button_clicked
        )
        self.key_word_extr_tab_widget.addTab(self.rake_tab, "RAKE")

        # Setup plain text edit
        # self.preview_plain_text_edit = QtWidgets.QPlainTextEdit()
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

        # Connect widgets to handlers
        self.source_language_combo_box.addItems(Constants.LANGUAGES)
        self.source_language_combo_box.setCurrentText(Constants.LANGUAGES[0])

        self.target_language_combo_box.addItems(Constants.LANGUAGES)
        self.target_language_combo_box.setCurrentText(Constants.LANGUAGES[1])

        self.translation_method_combo_box.addItems(Constants.TRANSLATION_METHODS.keys())
        self.split_method_combo_box.addItems(Constants.SPLIT_METHODS)

        self.kw_translator_combo_box.addItems(Constants.TRANSLATION_METHODS.keys())

        self.swap_languages_button.clicked.connect(self.swap_languages)

        self.translation_info_button.clicked.connect(
            partial(self.show_info, "translation_info")
        )
        self.split_info_button.clicked.connect(
            partial(self.show_info, "translation_info")
        )

        self.preview_text_button.clicked.connect(self.preview_text)
        self.open_text_button.clicked.connect(self.open_text_in_editor)

        # self.translate_button.clicked.connect(self.translate)

    def apply_cefr_efllex_button_clicked(self):

        levels = self.cefr_efllex_tab.get_selected_levels()
        model_type = self.cefr_efllex_tab.get_spacy_model()
        nlp_max_size = self.cefr_efllex_tab.get_spacy_max_doc_size()
        batch_size = self.cefr_efllex_tab.get_batch_size()

        filename = self.selected_text_line_edit.text()
        if not filename:
            msg.error_message("Select a file first!")
            return

        out_file_name = Path.USER_BOOKS.format(
            f"translated_texts/{filename.split('.')[0]}_cefr_efllex_{'_'.join(levels)}.txt"
        )
        out_file_name = os.path.abspath(out_file_name)

        self.logger.appendPlainText("Loading translation model...")
        QtCore.QCoreApplication.processEvents()

        method = CefrAndEfllexMethod(model_type, nlp_max_size)

        translators = Translators(
            self.kw_translator_combo_box.currentText(),
            self.source_language_combo_box.currentText(),
            self.target_language_combo_box.currentText(),
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

        model_type = self.kw_translator_combo_box.currentText()
        source_lng = self.source_language_combo_box.currentText()
        dest_lng = self.target_language_combo_box.currentText()

        filename = self.selected_text_line_edit.text()
        if not filename:
            msg.error_message("Select a file first!")
            return

        out_file_name = Path.USER_BOOKS.format(
            f"translated_texts/{filename.split('.')[0]}_rake_.txt"
        )
        out_file_name = os.path.abspath(out_file_name)

        self.logger.appendPlainText("Loading translation model...")
        QtCore.QCoreApplication.processEvents()

        translators = Translators(
            model_type,
            source_lng,
            dest_lng
        )

        self.logger.appendPlainText("Translation model have been loaded")
        QtCore.QCoreApplication.processEvents()

        method = RakeMethod(
            filename,
            out_file_name,
            Constants.SHORT_LANGS.get(source_lng),
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

        # TODO FIX BUG WITH PATH SO THAT THERE IS NO NEED IN ABSOLUTE PATH (os.getcwd????)
        text_file = f"/home/alex/Diplom/texts/user_books/translated_texts/{text}"
        if not text_file:
            msg.error_message("Select a translated text!")
            return
        
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

    def swap_languages(self):
        transtaled_lang = self.target_language_combo_box.currentText()
        source_lang = self.source_language_combo_box.currentText()

        self.source_language_combo_box.setCurrentText(transtaled_lang)
        self.target_language_combo_box.setCurrentText(source_lang)

    def show_info(self, caller: str):
        if caller == "translation_info":
            info_about = Constants.TRANSLATION_METHODS.get(
                self.translation_method_combo_box.currentText()
            )
            webbrowser.open(info_about)
        elif caller == "split_info":
            pass

    # def translate(
    #     self,
    #  ):
    #     print(os.getcwd())

    #     translated_text = dict()
    #     corpus_size = 0

    #     filename = self.selected_text_line_edit.text()
    #     src_lang = self.source_language_combo_box.currentText()
    #     target_lang = self.target_language_combo_box.currentText()
    #     translation_method = self.translation_method_combo_box.currentText()
    #     split_method = self.split_method_combo_box.currentText()

    #     if not filename:
    #         self.logger.appendPlainText("You should select a text first!")
    #         QtCore.QCoreApplication.processEvents()

    #         return

    #     self.logger.appendPlainText(f"Reading file {filename} ...")

    #     try:
    #         with open(Path.USER_BOOKS.format(filename), "r") as file:
    #             text = file.read()
    #     except Exception as e:
    #         self.logger.appendPlainText(repr(e))
    #         QtCore.QCoreApplication.processEvents()
    #         return

    #     self.logger.appendPlainText(f"Reading {filename}: OK\n")

    #     # Split text according to user choise
    #     if split_method == Constants.SPLIT_METHODS[1]: # Split by sentences using spacy lib

    #         text = text.replace("\n", " ")
    #         self.logger.appendPlainText("Loading spacy model and preprocessing text.")
    #         QtCore.QCoreApplication.processEvents()

    #         nlp = spacy.load("en_core_web_sm")
    #         doc = nlp(text)
    #         corpus_size = len(list(doc.sents))

    #     elif split_method == Constants.SPLIT_METHODS[0]: # Split by paragraphs ((\t) ?)

    #         self.logger.appendPlainText("Splitting text be paragraphs.")
    #         QtCore.QCoreApplication.processEvents()

    #         paragraphs = text.split("\t")
    #         corpus_size = len(paragraphs)

    #     #TODO find a way to avoid code duplication in math/case block
    #     #TODO avoid lots of IF/ELSE statements in match/case block

    #     match translation_method:

    #         case "googletrans":

    #             google_translator = Translator()
    #             self.logger.appendPlainText(f"Translating file {filename} with googletrans...")
    #             QtCore.QCoreApplication.processEvents()

    #             if split_method == Constants.SPLIT_METHODS[0]:

    #                 for i, paragraph in enumerate(paragraphs):
    #                     self.logger.appendPlainText(f"Progress: {round(i / corpus_size * 100, 2)} %")
    #                     QtCore.QCoreApplication.processEvents()

    #                     translated_paragraph = google_translator.translate(paragraph, src=src_lang, dest=target_lang)
    #                     translated_text[paragraph] = translated_paragraph.text

    #             elif split_method == Constants.SPLIT_METHODS[1]:

    #                 for i, sent in enumerate(doc.sents):
    #                     self.logger.appendPlainText(f"Progress: {round(i / corpus_size * 100, 2)} %")
    #                     QtCore.QCoreApplication.processEvents()

    #                     translated_sent = google_translator.translate(sent.text, src=src_lang, dest=target_lang)
    #                     translated_text[sent.text] = translated_sent.text

    #         case "fairseq":

    #             fairseq_model = torch.hub.load(
    #                 'pytorch/fairseq',
    #                 'transformer.wmt19.en-ru.single_model',
    #                 tokenizer='moses',
    #                 bpe='fastbpe',
    #                 verbose=False
    #             )

    #             fairseq_model.cuda()

    #             if split_method == Constants.SPLIT_METHODS[0]:

    #                 for i, paragraph in enumerate(paragraphs):
    #                     self.logger.appendPlainText(f"Progress: {round(i / corpus_size * 100, 2)} %")
    #                     QtCore.QCoreApplication.processEvents()

    #                     translated_text[paragraph] = fairseq_model.translate(paragraph, verbose=False)

    #             elif split_method == Constants.SPLIT_METHODS[1]:

    #                 for i, sent in enumerate(doc.sents):
    #                     self.logger.appendPlainText(f"Progress: {round(i / corpus_size * 100, 2)} %")
    #                     QtCore.QCoreApplication.processEvents()

    #                     translated_text[sent.text] = fairseq_model.translate(sent.text, verbose=False)

    #         case "argotranslate":

    #             if split_method == Constants.SPLIT_METHODS[0]:

    #                 for i, paragraph in enumerate(paragraphs):
    #                     self.logger.appendPlainText(f"Progress: {round(i / corpus_size * 100, 2)} %")
    #                     QtCore.QCoreApplication.processEvents()

    #                     translated_paragraph = argo_translate.translate(paragraph, src_lang, target_lang)
    #                     translated_text[paragraph] = translated_paragraph

    #             elif split_method == Constants.SPLIT_METHODS[1]:

    #                 for i, sent in enumerate(doc.sents):
    #                     self.logger.appendPlainText(f"Progress: {round(i / corpus_size * 100, 2)} %")
    #                     QtCore.QCoreApplication.processEvents()

    #                     translated_sent = argo_translate.translate(sent.text, src_lang, target_lang)
    #                     translated_text[sent.text] = translated_sent

    #     #out_file = Path.USER_BOOKS.format(f"translated_books/{filename[:-4]}_{translation_method}.txt")
    #     # TODO: FIX BUG WITH THE PATH ABOVE

    #     out_file = f"/home/alex/Diplom/texts/user_books/translated_texts/{filename[:-4]}_{translation_method}_{split_method}.txt"

    #     self.logger.appendPlainText(f"Writing {out_file}...")
    #     QtCore.QCoreApplication.processEvents()

    #     with open(out_file, "w+") as file:
    #         for original, translated in translated_text.items():
    #             file.write(original)
    #             file.write("\n\n[Translated fragment start]\n\n")
    #             file.write(translated)
    #             file.write("\n\n[Translated fragment end]\n\n")

    #     self.logger.appendPlainText(f"File {out_file}: OK")
    #     QtCore.QCoreApplication.processEvents()
