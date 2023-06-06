from typing import Tuple, List

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from superqt import QRangeSlider, QDoubleSlider

from config.settings import Constants, Path


key_bert_form, key_word_base = uic.loadUiType(uifile=Path.KEY_BERT_TRANSLATION_TAB_PATH)


class KeyBertTranslationForm(key_bert_form, key_word_base):
    def __init__(self):
        super(key_word_base, self).__init__()
        self.setupUi(self)

        self.custom_candidates = None

        self.src_lng_combo_box.addItems(Constants.SHORT_LANGS.keys())
        self.src_lng_combo_box.setCurrentText("en")
        self.trgt_lng_combo_box.addItems(Constants.SHORT_LANGS.keys())
        self.trgt_lng_combo_box.setCurrentText("uk")
        self.spacy_model_combo_box.addItems(Constants.SPACY_MODELS.get("en"))

        self.ngram_range_slider = QRangeSlider(QtCore.Qt.Orientation.Horizontal)
        self.ngram_range_slider.setValue((2, 3))
        self.ngram_range_slider.setRange(1, 10)

        self.diversity_slider = QDoubleSlider(QtCore.Qt.Orientation.Horizontal)
        self.diversity_slider.setRange(0, 1)
        self.diversity_slider.setSingleStep(0.05)
        self.diversity_slider.setValue(0.8)

        self.key_bert_settings_grid_layout.addWidget(self.ngram_range_slider, 1, 1)
        self.key_bert_settings_grid_layout.addWidget(self.diversity_slider, 3, 1)

        # Slider handlers
        self.ngram_range_slider.valueChanged.connect(self._on_ngram_range_slider_value_changed)
        self.top_n_phrases_slider.valueChanged.connect(self._on_top_n_phrases_slider_value_changed)
        self.diversity_slider.valueChanged.connect(self._on_diversity_slider_value_changed)
        self.nr_candidates_slider.valueChanged.connect(self._on_nr_candidates_value_changed)
        self.doc_max_size_slider.valueChanged.connect(self._on_doc_max_size_slider_value_changed)
        self.sentences_batch_slider.valueChanged.connect(self._on_sentences_batch_size_slider_value_changed)

        # Check box handlers
        self.use_mmr_check_box.toggled.connect(self._on_use_mmr_check_box_checked)
        self.use_max_sum_check_box.toggled.connect(self._on_use_max_sum_check_box_checked)
        self.use_custom_candidates_check_box.toggled.connect(self._on_use_custom_candidates_check_box_checked)
        self.batch_of_sentences_check_box.toggled.connect(self._on_batch_of_senteces_check_box_checked)
        self.paragraph_check_box.toggled.connect(self._on_paragraph_check_box_checked)

        # Combo box handlers
        self.src_lng_combo_box.currentTextChanged.connect(self._on_source_language_value_changed)

        # Buttons
        self.add_custom_candidates_button.clicked.connect(self.add_custom_candidates_button_clicked)

    def _on_batch_of_senteces_check_box_checked(self, state: bool) -> None:
        self.paragraph_check_box.setChecked(not state if state else state)
        self.paragraph_check_box.setEnabled(not state)
        self.paragraph_sign_line_edit.setEnabled(not state)

    def _on_paragraph_check_box_checked(self, state: bool) -> None:
        self.batch_of_sentences_check_box.setChecked(not state if state else state)
        self.batch_of_sentences_check_box.setEnabled(not state)
        self.sentences_batch_slider.setEnabled(not state)

    def _on_source_language_value_changed(self, value: str) -> None:
        self.spacy_model_combo_box.clear()
        self.spacy_model_combo_box.addItems(Constants.SPACY_MODELS.get(value))

    def _on_doc_max_size_slider_value_changed(self, value: int) -> None:
        self.doc_max_size_value_label.setText(str(value))

    def _on_use_mmr_check_box_checked(self, state: bool) -> None:
        self.use_max_sum_check_box.setChecked(not state if state else state)
        self.use_max_sum_check_box.setEnabled(not state)
        self.nr_candidates_slider.setEnabled(not state)
    
    def _on_use_max_sum_check_box_checked(self, state: bool) -> None:
        self.use_mmr_check_box.setChecked(not state if state else state)
        self.use_mmr_check_box.setEnabled(not state)
        self.diversity_slider.setEnabled(not state)

    def _on_use_custom_candidates_check_box_checked(self, state: bool) -> None:
        self.add_custom_candidates_button.setEnabled(state)

    def _on_sentences_batch_size_slider_value_changed(self, value: int) -> None:
        self.senteces_batch_size_label.setText(str(value))

    def _on_ngram_range_slider_value_changed(self, values: Tuple[int, int]) -> None:
        self.phrase_length_range.setText(f" [{values[0]}, {values[1]}]")
    
    def _on_top_n_phrases_slider_value_changed(self, value: int) -> None:
        self.top_n_phrases_value_label.setText(str(value))

    def _on_diversity_slider_value_changed(self, value: float) -> None:
        self.mmr_value_label.setText(str(round(value, 2)))

    def _on_nr_candidates_value_changed(self, value: int) -> None:
        self.nr_candidates_value_label.setText(str(value))

    def add_custom_candidates_button_clicked(self) -> None:
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'File browser', '(*.txt)')
        self.custom_candidates = file_name[0]

    def get_top_n_phrases(self) -> int:
        return self.top_n_phrases_slider.value()
    
    def get_ngram_value(self) -> Tuple[int, int]:
        return self.ngram_range_slider.value()

    # MMR and diversity
    def get_mmr_check_box_state(self) -> bool:
        return self.use_mmr_check_box.isChecked()

    def get_diversity_value(self) -> float:
        return self.diversity_slider.value()
    
    # Max sum and nr candidates
    def get_use_max_sum_state(self) -> bool:
        return self.use_max_sum_check_box.isChecked()
    
    def get_nr_candidates(self) -> int:
        return self.nr_candidates_slider.value()
    
    # Other
    def get_custom_candidates(self) -> List[str] | None:
        if self.custom_candidates is None: 
            return None

        with open(self.custom_candidates, "r") as file:
            candidates = file.read()
        
        return candidates.split("\n")
    
    def remove_stop_words(self) -> bool:
        return self.remove_stop_words_check_box.isChecked()
    
    def get_selected_languages(self) -> Tuple[str, str]:
        return (self.src_lng_combo_box.currentText(), self.trgt_lng_combo_box.currentText())

    def get_spacy_model(self) -> str:
        return self.spacy_model_combo_box.currentText()

    def get_nlp_max_size(self) -> int:
        return self.doc_max_size_slider.value()
    
    def split_by_sentences(self) -> bool:
        return self.batch_of_sentences_check_box.isChecked()
    
    def sentences_batch_size(self) -> int:
        return self.sentences_batch_slider.value()
    
    def split_by_paragraphs(self) -> bool:
        return self.paragraph_check_box.isChecked()
    
    def paragraph_split_sign(self) -> str:
        return self.paragraph_sign_line_edit.text()