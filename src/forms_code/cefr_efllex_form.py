from typing import List, Tuple

from PyQt5 import QtCore, QtGui, QtWidgets, uic

from config.settings import Constants
from config.settings import Constants, Path


ce_form_tab, ce_tab_base = uic.loadUiType(uifile=Path.CEFR_EFLLEX_TAB_PATH)


class CefrEfllexTabForm(ce_form_tab, ce_tab_base):
    def __init__(self):

        super(ce_tab_base, self).__init__()
        self.setupUi(self)

        self.cefr_spacy_model_combo_box.addItems(Constants.SPACY_MODELS.get("en"))
        
        self.src_lng_combo_box.addItems(("en",))
        self.trgt_lng_combo_box.addItems(("uk", "de"))
        self.trgt_lng_combo_box.setCurrentText("uk")

        self.batch_size_slider.valueChanged.connect(self._on_batch_slider_value_changed)
        self.nlp_max_size_slider.valueChanged.connect(self._on_nlp_slider_value_changed)

    def _on_nlp_slider_value_changed(self, value) -> None:
        self.spacy_doc_sz_value_label.setText(str(value))

    def _on_batch_slider_value_changed(self, value) -> None:
        self.batch_size_value_label.setText(str(value))

    def get_selected_languages(self) -> Tuple[str, str]:
        return (self.src_lng_combo_box.currentText(), self.trgt_lng_combo_box.currentText())

    def get_selected_levels(self) -> List[str]:

        levels = []
        items_number: int = self.cefr_layout.count()

        for i in range(items_number):
            widget = self.cefr_layout.itemAt(i).widget()
            if widget.isChecked():
                levels.append(widget.objectName())

        return levels

    def get_batch_size(self) -> int:
        return self.batch_size_slider.value()

    def get_spacy_max_doc_size(self) -> int:
        return self.nlp_max_size_slider.value()

    def get_spacy_model(self) -> str:
        return self.cefr_spacy_model_combo_box.currentText()
