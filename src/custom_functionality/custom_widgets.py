import pandas as pd

from nltk.stem import WordNetLemmatizer

from matplotlib import pyplot as plt

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QPlainTextEdit

from postgres_db.postgres_database import PsqlDatabase
from config.settings import Constants


plt.style.use('ggplot')


class SmartPlainTextEdit(QPlainTextEdit):
    
    def __init__(self, logger):
        QPlainTextEdit.__init__(self)
        self.db = PsqlDatabase()
        self.lemmatizer = WordNetLemmatizer()
        self.logger = logger

    def _close_figure(self, event):
        if event.key == 'escape':
            plt.close(event.canvas.figure)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_1:

            cursor = self.textCursor()

            if cursor.hasSelection():

                word = self.lemmatizer.lemmatize(cursor.selectedText())
                freqs = self.db.get_word_frequency(word)

                if not freqs:
                    self.logger.appendPlainText(f"Word {word} doesn't exist in EFLLEX dataset.")
                    QtCore.QCoreApplication.processEvents()
                    return
                
                df = pd.DataFrame(freqs, columns=Constants.WORD_FREQ_COLUMNS)
                self.plotter(df)
                return
            
        return super().keyPressEvent(event)
    
    def plotter(self, df):

        ax1_values = df[Constants.SUBSET_1].values[0]
        ax2_values = df[Constants.SUBSET_2].values[0]
        _, (ax1, ax2) = plt.subplots(2, 1, figsize=(10,10), facecolor='white', dpi= 80)
        
        ax1.vlines(x=Constants.SUBSET_1, ymin=0, ymax=ax1_values, color='firebrick', alpha=0.7, linewidth=50)
        # Annotate Text
        for i, freq in enumerate(ax1_values):
            ax1.text(i, float(freq)+0.1, freq, horizontalalignment='center')

        # Title, Label, Ticks and Ylim
        ax1.set_title("Frequencies", fontdict={'size':22})
        ax1.set(xlabel = "CEFR level", ylabel='Frequency (normalized/million)', ylim=(0, max(ax1_values) + 5))#, xlim = (-0.25, 5))
        ax1.set_xticks(Constants.SUBSET_1, rotation=60, horizontalalignment='right', fontsize=12)


        ax2.vlines(x=Constants.SUBSET_2, ymin=0, ymax=ax2_values, color='firebrick', alpha=0.7, linewidth=50)
        # Annotate Text
        for i, freq in enumerate(ax2_values):
            ax2.text(i, freq+0.1, freq, horizontalalignment='center')

        # Title, Label, Ticks and Ylim
        ax2.set_title("Frequencies", fontdict={'size':22})
        ax2.set(xlabel = "CEFR level (dataset)", ylabel='Frequency (dataset)', ylim=(0, max(ax2_values) + 5))#, xlim = (-0.25, 5))
        ax2.set_xticks(Constants.SUBSET_2, rotation=60, horizontalalignment='right', fontsize=12)

        
        plt.gcf().canvas.mpl_connect('key_press_event', self._close_figure)
        plt.tight_layout()
        plt.show()