from typing import Tuple
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from config.settings import Constants, Path


bt_tab_form, bt_tab_base = uic.loadUiType(uifile=Path.BASIC_TRANSLATION_TAB_PATH)


class BasicTranslationTabForm(bt_tab_form, bt_tab_base):
    def __init__(self):

        super(bt_tab_base, self).__init__()
        self.setupUi(self)

        self.translation_method_combo_box.addItems(Constants.TRANSLATION_METHODS.keys())
        self.translation_method_combo_box.currentTextChanged.connect(self._on_translation_method_combo_box_value_changed)
        self.translation_method_combo_box.setCurrentText("googletrans")
        self.fairseq_translation_model_label.setEnabled(False)
        self.fairseq_translation_model_combo_box.setEnabled(False)

        self.split_method_combo_box.addItems(Constants.SPLIT_METHODS)        
        
        self.bt_spacy_model_combo_box.addItems(Constants.SPACY_MODELS.get("en"))
        
        self.fairseq_translation_model_combo_box.addItems(Constants.FAIRSEQ_MODELS.keys())
        
        self.src_lng_combo_box.addItems(Constants.SHORT_LANGS.keys())
        self.src_lng_combo_box.setCurrentText("en")
        self.src_lng_combo_box.currentTextChanged.connect(self._on_src_lng_combo_box_text_changed)
        
        self.trgt_lng_combo_box.addItems(Constants.SHORT_LANGS.keys())
        self.trgt_lng_combo_box.setCurrentText("uk")
        
        self.doc_max_size_slider.valueChanged.connect(self._on_doc_max_size_slider_value_changed)

    def _on_src_lng_combo_box_text_changed(self, value: str) -> None:
        self.bt_spacy_model_combo_box.clear()
        self.bt_spacy_model_combo_box.addItems(Constants.SPACY_MODELS.get(value))

    def _on_translation_method_combo_box_value_changed(self, value: str) -> None:
        match value:
            case "googletrans":
                self.fairseq_translation_model_label.setEnabled(False)
                self.fairseq_translation_model_combo_box.setEnabled(False)
            case "fairseq":
                self.fairseq_translation_model_label.setEnabled(True)
                self.fairseq_translation_model_combo_box.setEnabled(True)

    def _on_doc_max_size_slider_value_changed(self, value: int) -> None:
        self.doc_max_size_value_label.setText(str(value))

    def get_translation_method(self) -> str:
        return self.translation_method_combo_box.currentText()
    
    def get_fairseq_model(self) -> str:
        return Constants.FAIRSEQ_MODELS.get(
            self.fairseq_translation_model_combo_box.currentText()
            )

    def get_spacy_model(self) -> str:
        return self.bt_spacy_model_combo_box.currentText()

    def get_spacy_doc_size(self) -> int:
        return self.doc_max_size_slider.value()

    def get_split_method(self) -> str:
        return self.split_method_combo_box.currentText()
    
    def get_selected_languages(self) -> Tuple[str, str]:
        return (self.src_lng_combo_box.currentText(), self.trgt_lng_combo_box.currentText())

    def get_mark_options(self) -> Tuple[bool, bool]:
        return (self.mark_original_text_check_box.isChecked(), self.mark_translated_text_check_box.isChecked())
