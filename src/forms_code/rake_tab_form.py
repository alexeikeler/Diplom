from typing import Tuple
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from config.settings import Constants, Path

rake_tab_form, rake_tab_base = uic.loadUiType(uifile=Path.RAKE_TAB_PATH)


class RakeTabForm(rake_tab_form, rake_tab_base):
    def __init__(self):

        super(rake_tab_base, self).__init__()
        self.setupUi(self)

        self.ranking_methods_combo_box.addItems(Constants.RAKE_RANKING_METHODS)
        self.src_lng_combo_box.addItems(Constants.SHORT_LANGS.keys())
        self.trgt_lng_combo_box.addItems(Constants.SHORT_LANGS.keys())

        self.src_lng_combo_box.setCurrentText("en")
        self.trgt_lng_combo_box.setCurrentText("uk")
        

        # Connect sliders to handlers
        self.max_words_slider.valueChanged.connect(self._max_slider_value_changed)
        self.min_words_slider.valueChanged.connect(self._min_slider_value_changed)
        self.rake_batch_size_slider.valueChanged.connect(self._batch_size_slider_value_changed)

    def _min_slider_value_changed(self, value: int) -> None:
        self.min_words_val_label.setText(str(value))

    def _max_slider_value_changed(self, value: int) -> None:
        self.max_words_val_label.setText(str(value))
        self.min_words_slider.setMaximum(value - 1)

    def _batch_size_slider_value_changed(self, value: int) -> None:
        self.rake_batch_size_value_label.setText(str(value))

    def get_selected_languages(self) -> Tuple[str, str]:
        return (self.src_lng_combo_box.currentText(), self.trgt_lng_combo_box.currentText())

    def get_max_value(self) -> int:
        return self.max_words_slider.value()

    def get_min_value(self) -> int:
        return self.min_words_slider.value()

    def get_ranking_method(self) -> str:
        return self.ranking_methods_combo_box.currentText()

    def get_repeated_phrases(self) -> bool:
        return self.inc_rep_phrs_check_box.isChecked()

    def get_batch_size(self) -> int:
        return self.rake_batch_size_slider.value()