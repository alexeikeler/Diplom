from PyQt5 import QtCore, QtGui, QtWidgets, uic

from config.settings import Constants, Path

rake_tab_form, rake_tab_base = uic.loadUiType(uifile=Path.RAKE_TAB_PATH)


class RakeTabForm(rake_tab_form, rake_tab_base):
    def __init__(self):

        super(rake_tab_base, self).__init__()
        self.setupUi(self)

        self.ranking_methods_combo_box.addItems(Constants.RAKE_RANKING_METHODS)

        # Connect sliders to handlers
        self.max_words_slider.valueChanged.connect(self._max_slider_value_changed)
        self.min_words_slider.valueChanged.connect(self._min_slider_value_changed)

    def _min_slider_value_changed(self, value: int) -> None:
        self.min_words_val_label.setText(str(value))

    def _max_slider_value_changed(self, value: int) -> None:
        self.max_words_val_label.setText(str(value))
        self.min_words_slider.setMaximum(value - 1)

    def get_max_value(self) -> int:
        return self.max_words_slider.value()

    def get_min_value(self) -> int:
        return self.min_words_slider.value()

    def get_ranking_method(self) -> str:
        return self.ranking_methods_combo_box.currentText()

    def get_repeated_phrases(self) -> bool:
        return self.inc_rep_phrs_check_box.isChecked()
