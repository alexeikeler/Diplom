import os
import time
import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtCore, uic

from config.settings import Path, Constants
from src.words_analysis.dataset_creater import BooksDownloader, TextPreprocessor
from src.words_analysis import metrics

from src.custom_functionality import message_boxes as msg
from src.custom_functionality import functions as funcs

corpus_form, corpus_base = uic.loadUiType(uifile=Path.CORPUS_UI_PATH)


class CorpusForm(corpus_form, corpus_base):
    def __init__(self):

        super(corpus_base, self).__init__()
        self.setupUi(self)

        self.create_corpus_button.clicked.connect(self.create_corpus)
        self.show_files_button.clicked.connect(self.show_files)
        self.gen_tfidf_button.clicked.connect(self.generate_tfidf)

        self.remove_punct_check_box.setChecked(True)
        self.lemmantizer_check_box.setChecked(True)
        self.remove_non_alphabet.setChecked(True)
        self.apply_lowercase_check_box.setChecked(True)
        self.remove_stop_words_check_box.setChecked(True)
        
        self.models_check_box.addItems(Constants.SPACY_MODELS)
        
        self.parallel_check_box.setChecked(True)
        self.parallel_check_box.stateChanged.connect(self._parallel_check_box_state)

        self.cores_spin_box.setMaximum(Constants.CORES)
        self.cores_spin_box.setValue(Constants.CORES)
        self.cores_spin_box.setEnabled(True)

        self.cores_spin_box.setMinimum(1)
        self.cores_spin_box.setMaximum(Constants.CORES)
        self.text_batch_size_spin_box.setValue(Constants.BATCH_SIZE)

    def _parallel_check_box_state(self, state):
        if state:
            self.cores_spin_box.setEnabled(True)

        else:
            self.cores_spin_box.setEnabled(False)

    def create_corpus(self):
        #self.text_edit.setText("Downloading books...")
        #self.download_documents()
        #self.text_edit.append("Downloading is finished.")

        msg.info_message("Downloading is finished.")

        self.text_edit.append("Preprocessing downloaded texts...")
        self.preprocess_documents()
        self.text_edit.append("\nPreprocessing is finished.")

        msg.info_message("Preprocessing is finished.")


    def download_documents(self):

        downloader = BooksDownloader()
        
        top_n = self.top_n_spin_box.value()
 
        new_books = downloader._get_ids(top_n)
        _, existing_titles = funcs.get_books_and_titles()

        self.text_edit.append(f"Existing books: {len(existing_titles)}")
        
        self.text_edit.append(
            f"Books from project gutenberg ({top_n} most popular): {len(new_books)}"
        )        
    
        books_to_download = new_books - existing_titles
       
        if not books_to_download:
            msg.info_message("No new books were found.")
            self.text_edit.setText("")
            return
        
        self.text_edit.append(f"New books: {len(books_to_download)}")
        self.text_edit.append(f"Donwloading new books...")
        
        QtCore.QCoreApplication.processEvents()
        
        downloader.download_books(
            books_to_download, 
            Path.DATASET_PATH, 
            self.text_edit
        )

        del(downloader)

    def show_files(self):
        file_browser = QtWidgets.QFileDialog(self, "Files", Path.DATASET_PATH.format(""))
        file_browser.show()

    def preprocess_documents(self):
        
        remove_punct = self.remove_punct_check_box.isChecked()
        remove_non_alphabet = self.remove_non_alphabet.isChecked()
        remove_stop_words = self.remove_stop_words_check_box.isChecked()
        lemmantize = self.lemmantizer_check_box.isChecked()
        to_lowercase = self.apply_lowercase_check_box.isChecked()

        model = self.models_check_box.currentText()
        n_jobs = self.cores_spin_box.value()
        batch_size = self.text_batch_size_spin_box.value()

        text_preprocessor = TextPreprocessor(
            remove_punct,
            remove_non_alphabet,
            remove_stop_words,
            lemmantize,
            to_lowercase,
            model,
            n_jobs    
        )

        self.text_edit.append("\nSelected settings:")
        self.text_edit.append("-"*50)
        
        self.text_edit.append(f"{remove_punct=}")
        self.text_edit.append(f"{remove_non_alphabet=}")
        self.text_edit.append(f"{remove_stop_words=}")
        self.text_edit.append(f"{lemmantize=}")
        self.text_edit.append(f"{to_lowercase=}")
        self.text_edit.append(f"{model=}")
        self.text_edit.append(f"{n_jobs=}")
        self.text_edit.append(f"{batch_size=}")
        
        self.text_edit.append("-"*50)
        
        QtCore.QCoreApplication.processEvents()
        
        books, titles = funcs.get_books_and_titles()
        union = tuple(zip(books, titles))
        files_partition = list(funcs.partition(union, batch_size))
        size = len(files_partition)

        for i, partition in enumerate(files_partition, 1):

            start = time.time()    

            self.text_edit.append(f"Cleaning batches: {i} / {size}")
            QtCore.QCoreApplication.processEvents()
        
            df = pd.DataFrame(columns=["text"])
            
            for book, _ in partition:
                with open(book, "r") as f:
                    df.loc[len(df)] = f.read()


            cleaned = text_preprocessor.transform(df["text"])

            for  i, data in enumerate(partition):
                path = Path.DATASET_PATH.format(f"cleaned/{data[1]}_cleaned.txt")
                with open(path, "w+") as f:
                    f.write(cleaned[i])
            
            passed_time = time.time() - start
            self.text_edit.append(f"Time: {passed_time:.2f}\n")
            QtCore.QCoreApplication.processEvents()
            
                

        del(text_preprocessor)
            
    def generate_tfidf(self):
        files, _ = funcs.get_books_and_titles("/cleaned/")
        metrics.tfidf_metric(files)
