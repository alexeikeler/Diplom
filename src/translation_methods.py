import re
import logging

import spacy
from spacy.tokens.doc import Doc

import torch

from PyQt5 import QtCore
from PyQt5.QtWidgets import QPlainTextEdit

from googletrans import Translator
from rake_nltk import Metric, Rake
from typing import List

import src.custom_functionality.functions as funcs
from config.settings import Path
from postgres_db.postgres_database import PsqlDatabase
from src.custom_functionality import message_boxes as msg


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

    def __init__(self, tr_method, src_lang, dest_lang, fairseq_model=None) -> None:
        
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
                    fairseq_model,
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
                
                # Fast but may brake some times due to mismatch between
                # amount of strings

                # Using \n instead of | fixed the issue?
                
                to_string = "\n".join(txt)
                result = self.tr_model.translate(to_string, src=self._src_lang, dest=self._dest_lang)                
                return result.text.split("\n")
                
                # Slow but trustworthy
                #raw_result = self.tr_model.translate(txt, src=self._src_lang, dest=self._dest_lang)
                #result = [sub_text.text for sub_text in raw_result]
                #return list(result)


            case "fairseq":
                return self.tr_model.translate(txt, verbose=False)
    
    def translate_part(self, text):
        
        match self._tr_method:
            
            case "googletrans":
                translated = self.tr_model.translate(text, src=self._src_lang, dest=self._dest_lang)
                return translated.text

            case "fairseq":
                return self.tr_model.translate(text, verbose=False)    


    def process_batches(self, formatted_batch, translate_batch):
        tr_words = self.translate_text(translate_batch)
        formatted_sentences = "".join(formatted_batch).format(*tr_words)
        return formatted_sentences


class CefrAndEfllexMethod:

    __slots__ = ["database", "nlp"]

    def __init__(self, spacy_model_type: str, nlp_max_size: int):
        self.database = PsqlDatabase()
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

    def translate(
        self, 
        translators: Translators, 
        file, 
        levels, 
        out_file_name, 
        logger, 
        batch
    ) -> None:

        # Clean file if exists otherwise create it
        open(out_file_name, "w").close()

        modified_parts = []
        words_to_translate = []
        counter = 0
        
        # Preprocess text
        doc = self._preprocess(file)
        sents_size = len(list(doc.sents))

        logger.appendPlainText(f"Preprocessing file {file}...")
        QtCore.QCoreApplication.processEvents()

        if doc is None:
            logger.appendPlainText(f"Preprocessing failed due to spacy error.\n")
            QtCore.QCoreApplication.processEvents()
            return

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
                translated_batch = translators.process_batches(modified_parts, words_to_translate)
                funcs.write_file(out_file_name, translated_batch, "a")
    
                # Clean buffer lists
                modified_parts.clear()
                words_to_translate.clear()
                counter = 0

        if words_to_translate:
            translated_batch = translators.process_batches(modified_parts, words_to_translate)
            funcs.write_file(out_file_name, translated_batch, "a")


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
                funcs.write_file(self.out_file, translated_batch, "a")
    
                modifiend_sents.clear()
                translate_list.clear()
                counter = 0

        
        if translate_list:
            translated_batch = translators.process_batches(modifiend_sents, translate_list)
            funcs.write_file(self.out_file, translated_batch, "a")

        logger.appendPlainText(f"{size}/{size} | 100% \nFinished.")
        QtCore.QCoreApplication.processEvents()


class KeyBertMethod:
    pass


class BasicTranslationMethod:

    def __init__(self, split_method: str, spacy_model_type: str, nlp_max_size: int):
        
        self.split_method = split_method
        self.nlp = None

        if self.split_method == "sentence":
            self.nlp = spacy.load(spacy_model_type)
            self.nlp.max_length = nlp_max_size

    def _read_file(self, file) -> str:
        with open(Path.USER_BOOKS.format(file), "r") as user_file:
            text = user_file.read()

        text = text.replace("\n", " ").replace("_", "")
        return text
    
    def _write_part(self, text_dict, out_file) -> None:
        with open(out_file, "w") as user_out_file:
            for original, translated in text_dict.items():
                user_out_file.write(original + "\n\n")
                user_out_file.write(translated + "\n\n")
                 
            
    
    def _preprocess_paragraphs(self, text: str) -> List[str]:
        if re.search("\n{3,}") is not None:
            text = re.sub("\n{3,}", "\n\n", text)
    
        text = text.split("\n\n")
        return text

    def _preprocess_sentences(self, text: str) -> Doc:

        try:
            doc = self.nlp(text, disable=["ner"])

        except ValueError as ve:
            msg.error_message(repr(ve))
            return None

        return doc

    def translate(self, translator, file, out_file, logger):

        text = self._read_file(file)
        
        modified_text = dict()

        match self.split_method:

            case "sentence":
                logger.appendPlainText("Preprocessing text...")
                QtCore.QCoreApplication.processEvents()

                doc = self._preprocess_sentences(text)

                logger.appendPlainText(f"Preprocessing end...\nTranslating text...")
                QtCore.QCoreApplication.processEvents()

                for sent in doc.sents:
                    modified_text[sent.text] = translator.translate_part(sent.text)
                
                self._write_part(modified_text, out_file)

                logger.appendPlainText(f"End of the translation.")
                QtCore.QCoreApplication.processEvents()


        

