from PyQt5 import QtWidgets, QtGui, QtCore, uic

from config.settings import Path
from src.words_analysis.dataset_creater import BooksDownloader, TextPreprocessor
from src.custom_functionality import message_boxes as msg


corpus_form, corpus_base = uic.loadUiType(uifile=Path.CORPUS_UI_PATH)


class CorpusForm(corpus_form, corpus_base):
    def __init__(self):

        super(corpus_base, self).__init__()
        self.setupUi(self)

        self.update_dataset_button.clicked.connect(self.update_dataset)

        self.downloader = BooksDownloader()
        self.text_preprocessor = TextPreprocessor()
    
    def update_dataset(self):
        top_n = self.top_n_spin_box.value()

        new_books = self.downloader._get_ids(top_n)
        existing_books = self.downloader._get_existing_books()

        books_to_download = set(new_books) - set(existing_books)

        if not books_to_download:
            msg.error_message("No new books were found.")
            return
        
        self.text_edit.append(f"Downloading books...")
        self.downloader.download_books(books_to_download, Path.DATASET_PATH)
        self.text_edit.append(f"Downloading is finished.")
        



    def preprocess_documents(self):
        pass

    def calculate_tf_idf(self):
        pass