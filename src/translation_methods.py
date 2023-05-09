import re
import logging

import numpy as np
import spacy
import torch

from PyQt5 import QtCore
from PyQt5.QtWidgets import QPlainTextEdit

from googletrans import Translator
from rake_nltk import Metric, Rake
from typing import List

from config.settings import Path
from postgres_db.postgres_database import Database
from src.custom_functionality import message_boxes as msg
from src.custom_functionality.functions import timeit
from src.custom_functionality.functions import singleton

logging.basicConfig(level=logging.WARNING)


class Translators:
    __slots__ = [
        "tr_model",
        "_tr_method",
        "_src_lang",
        "_dest_lang",
        "_fairseq_model",
        "_google_translator",
    ]

    def __init__(self, tr_method, src_lang, dest_lang) -> None:
        
        self.tr_model = None        
        self._tr_method = tr_method
        self._src_lang = src_lang
        self._dest_lang = dest_lang
       
        #self._google_translator = None
        #self._fairseq_model = None

        match tr_method:
            
            case "fairseq":
                self.tr_model = torch.hub.load(
                    "pytorch/fairseq",
                    "transformer.wmt19.en-ru.single_model",
                    tokenizer="moses",
                    bpe="fastbpe",
                    verbose=False,
                )
                self.tr_model.cuda()
            
            case "googletrans":
                self.tr_model = Translator()

    def translate_text(self, txt: List[str]) -> None:
        match self._tr_method:
            case "googletrans":
                
                to_string = "|".join(txt)
                result = self.tr_model.translate(to_string, src=self._src_lang, dest=self._dest_lang)
                return result.text.split("|")
            
            case "fairseq":
                return self.tr_model.translate(txt, verbose=False)

    def process_batches(self, formatted_batch, translate_batch):
        tr_words = self.translate_text(translate_batch)
        formatted_sentences = "".join(formatted_batch).format(*tr_words)
        return formatted_sentences


class CefrAndEfllexMethod:

    __slots__ = ["database", "nlp"]

    def __init__(self, spacy_model_type: str, nlp_max_size: int):
        self.database = Database()
        self.nlp = spacy.load(spacy_model_type)
        self.nlp.max_length = nlp_max_size

    def _preprocess(self, file) -> str:

        with open(Path.USER_BOOKS.format(file), "r") as user_file:
            text = user_file.read()

        text = text.replace("\n", " ").replace("\t", " ")

        try:
            doc = self.nlp(text, disable=["ner"])

        except ValueError as ve:
            msg.error_message(repr(ve))
            return None

        return doc

    def translate(self, translators, file, levels, out_file_name, logger, batch):
        def process_batch(sentences, words):

            translated_words = translators.translate_text(words)

            part = "".join(sentences).format(*translated_words)

            with open(out_file_name, "a") as out_file:
                out_file.write(part)

            sentences.clear()
            return sentences

        modified_parts = []
        words_to_translate = []
        counter = 0

        # Clean file if exists otherwise create it
        open(out_file_name, "w").close()

        logger.appendPlainText(f"Preprocessing file {file}...")
        QtCore.QCoreApplication.processEvents()

        # Preprocess text
        doc = self._preprocess(file)

        if doc is None:
            logger.appendPlainText(f"Preprocessing failed due to spacy error.\n")
            QtCore.QCoreApplication.processEvents()
            return

        sents_size = len(list(doc.sents))

        logger.appendPlainText(f"Preprocessing end...\nTranslating text...")
        QtCore.QCoreApplication.processEvents()

        for sent_n, sent in enumerate(doc.sents):

            if sent_n % 10 == 0:
                logger.appendPlainText(
                    f"Progress {sent_n} / {sents_size} | {round(sent_n*100/sents_size, 2)} %"
                )
                QtCore.QCoreApplication.processEvents()

            text = sent.text

            for word in sent:

                if not (word.is_punct or word.is_stop):
                    word_level = self.database.get_cefr_level(
                        word.lemma_, spacy.explain(word.pos_), word.tag_
                    )

                    if word_level in levels:

                        words_to_translate.append(word.text)
                        bounds = re.search(word.text, text, flags=re.IGNORECASE)

                        # Fromat current sentence to format ""... [word - {i}] ...", wher "i" is index of translated word
                        # that will be formated with -------> str.format(*list_of_translated_words) so that
                        # there is less calls to translator
                        text = text[: bounds.end(0) + 1] + f" [{word.text} - {{{counter}}}] " + text[bounds.end(0) + 1 :]
                        
                        counter += 1

            text += "\n\n"

            if not words_to_translate or len(words_to_translate) < batch:
                modified_parts.append(text)
                continue

            elif len(words_to_translate) > batch:
                modified_parts = process_batch(modified_parts, words_to_translate)

                # Clean buffer array
                words_to_translate.clear()
                counter = 0

        if words_to_translate:
            process_batch(modified_parts, words_to_translate)

        logger.appendPlainText(f"{sents_size}/{sents_size} | 100% \nFinished.")
        QtCore.QCoreApplication.processEvents()


class RakeMethod:
    __slots__ = ["rake", "punct_regex", "file", "out_file"]

    def __init__(
        self,
        file,
        out_file,
        language: str,
        rake_min_words: int,
        rake_max_words: int,
        rake_ranking_method: Metric,
        allow_repeated_phrases: bool
    ):
        self.file = file
        self.out_file = out_file

        self.rake = Rake(
            language=language,
            min_length=rake_min_words,
            max_length=rake_max_words,
            ranking_metric=rake_ranking_method,
            include_repeated_phrases=allow_repeated_phrases
        )

        self.punct_regex = re.compile('[@_!#$%^&*()<>?/\\\|}{~:[\]]') 


    def _preprocess(self, file) -> List[str]:
        
        with open(Path.USER_BOOKS.format(file), "r") as user_file:
            text = user_file.read()

        splitted_by_tab = text.split("\n\n")
        splitted_by_tab = list(
            map(lambda string: string.replace("\n", " "), splitted_by_tab)
        )

        return splitted_by_tab


    def _write_batch(self, batch) -> None:
        with open(self.out_file, "a") as user_out_file:
            user_out_file.write(batch)


    def translate(
        self, 
        translators: Translators, 
        logger: QPlainTextEdit, 
        batch_size: int
    ) -> None:
        processed_text = self._preprocess(self.file)

        translate_list = []
        modifiend_sents = []
        counter = 0
        size = len(processed_text)

        # Open file and truncate it, or create if not exists
        open(self.out_file, "w").close()

        logger.appendPlainText(f"Preprocessing file {self.file}...")
        QtCore.QCoreApplication.processEvents()

        logger.appendPlainText(f"Preprocessing end...\nTranslating text...")
        QtCore.QCoreApplication.processEvents()

        for index, paragraph in enumerate(processed_text):
               
            if index % 10 == 0:
                logger.appendPlainText(
                    f"Progress {index} / {size} | {round(index*100/size, 2)} %"
                )
                QtCore.QCoreApplication.processEvents()

            self.rake.extract_keywords_from_text(paragraph)
            key_phrases = self.rake.get_ranked_phrases()

            text = paragraph

            for key_phrase in key_phrases:

                if self.punct_regex.search(key_phrase) is not None:
                    continue

                bounds = re.search(key_phrase, text, re.IGNORECASE)
                if bounds is None:
                    continue
                
                # Translation somewhere here (if it's one thing at a time)
                translate_list.append(key_phrase)
                text = text[:bounds.end(0) + 1] + f" [{key_phrase} - {{{counter}}}] " + text[bounds.end(0) + 1:]
                counter += 1

            text += "\n\n"

            if not translate_list or len(translate_list) < batch_size:
                modifiend_sents.append(text)
                continue 
            
            elif len(translate_list) > batch_size:
                
                translated_batch = translators.process_batches(modifiend_sents, translate_list)
                self._write_batch(translated_batch)

                modifiend_sents.clear()
                translate_list.clear()
                counter = 0

        
        if translate_list:
            translated_batch = translators.process_batches(modifiend_sents, translate_list)
            self._write_batch(translated_batch)

        logger.appendPlainText(f"{size}/{size} | 100% \nFinished.")
        QtCore.QCoreApplication.processEvents()
