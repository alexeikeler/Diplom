from PyQt5 import QtGui
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QPlainTextEdit
from matplotlib import pyplot as plt

from postgres_db.postgres_database import Database



class SmartPlainTextEdit(QPlainTextEdit):

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_1:
    
            cursor = self.textCursor()
    
            if cursor.hasSelection():
                
                word, tag = cursor.selectedText().replace(" ", "").split(",")
                print(word, tag)
                freqs = self.database.get_word_frequencies(word, tag)                
                self.plot_word_frequencies(word, freqs)

                return
        return super().keyPressEvent(event)
    