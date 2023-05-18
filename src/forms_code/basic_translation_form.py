from PyQt5 import QtCore, QtGui, QtWidgets, uic

from config.settings import Constants, Path


bt_tab_form, bt_tab_base = uic.loadUiType(uifile=Path.BASIC_TRANSLATION_TAB_PATH)


class BasicTranslationTabForm(bt_tab_form, bt_tab_base):
    def __init__(self):

        super(bt_tab_base, self).__init__()
        self.setupUi(self)

