from PyQt5 import QtGui
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QApplication, QPlainTextEdit


class SmartPlainTextEdit(QPlainTextEdit):

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_End:
            cursor = self.textCursor()
            if cursor.hasSelection():
                print(cursor.selectedText())
                return
        return super().keyPressEvent(event)