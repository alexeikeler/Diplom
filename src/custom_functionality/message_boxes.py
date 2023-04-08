from PyQt5 import QtWidgets


def info_message(msg_text: str):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText(msg_text)
    msg.setWindowTitle("Info message")
    msg.exec_()


def warning_message(msg_text: str):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setText(msg_text)
    msg.setWindowTitle("Warning message")
    msg.exec_()


def error_message(msg_text: str):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setText(msg_text)
    msg.setWindowTitle("Error message")
    msg.exec_()
