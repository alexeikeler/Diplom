import logging
import re

logging.basicConfig(level=logging.WARNING)

import numpy as np
import spacy
import torch

from googletrans import Translator
from PyQt5 import QtCore
from rake_nltk import Metric, Rake
from typing import List

from config.settings import Path
from postgres_db.postgres_database import Database
from src.custom_functionality import message_boxes as msg


class Translators:
    __slots__ = [
        "_tr_method",
        "_src_lang",
        "_dest_lang",
        "_fairseq_model",
        "_google_translator",
    ]

    def __init__(self, tr_method, src_lang, dest_lang) -> None:
        self._tr_method = tr_method
        self._src_lang = src_lang
        self._dest_lang = dest_lang
        self._google_translator = Translator()

        if tr_method == "fairseq":
            self._fairseq_model = torch.hub.load(
                "pytorch/fairseq",
                "transformer.wmt19.en-ru.single_model",
                tokenizer="moses",
                bpe="fastbpe",
                verbose=False,
            )
            self._fairseq_model.cuda()

    def translate_text(self, txt: str) -> None:
        match self._tr_method:
            case "googletrans":
                return self._google_translator.translate(
                    txt, src=self._src_lang, dest=self._dest_lang
                ).text
            case "fairseq":
                return self._fairseq_model.translate(txt, verbose=False)


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

            translated_words = translators.translate_text("|".join(words)).split("|")

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
                        text = (
                            text[: bounds.end(0) + 1]
                            + f" [{word.text} - {{{counter}}}] "
                            + text[bounds.end(0) + 1 :]
                        )
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
    __slots__ = ["nlp", "rake"]

    def __init__(
        self,
        spacy_model_type: str,
        nlp_max_size: int,
        language: str,
        rake_min_words: int,
        rake_max_words: int,
        rake_ranking_method: Metric,
    ):
        
        self.nlp = spacy.load(spacy_model_type)
        self.nlp.max_length = nlp_max_size

        self.rake = Rake(
            language=language,
            min_length=rake_min_words,
            max_length=rake_max_words,
            ranking_metric=rake_ranking_method
        )

    def _preprocess(file) -> List[str]:
        
        with open(Path.USER_BOOKS.format(file), "r") as user_file:
            text = user_file.read()

        splitted_by_tab = text.split("\n\n")
        splitted_by_tab = list(map(lambda string: string.replace("\n", " "), splitted_by_tab))


    def translate(file, out_file_name, logger) -> None:
        pass

    # def np_key_word_translator(self):
        
    #     size = len(list(doc.sents))
    #     modified_sents = np.empty(size, dtype=object)
    #     #flag = False
    #     docsz = len(list(doc.sents))
                    
    #     for i, sent in enumerate(doc.sents):
    #         if i % 100 == 0:
    #                 print(f"{i}/{docsz}")
    #         rake.extract_keywords_from_text(sent.text)

    #         key_phrases = rake.get_ranked_phrases()
    #         text = sent.text

    #         for key_phrase in key_phrases:
                
    #             if regex.search(key_phrase) is not None:
    #                 continue
                
    #             bounds = re.search(key_phrase, text, re.IGNORECASE)    

    #             if bounds is None:
    #                 continue
                    
    #             #tr = gt.translate(key_phrase, src="en", dest="ru").text
    #             text = text[:bounds.end(0) + 1] + "(tr...)" + text[bounds.end(0)+1:]
        
    #         modified_sents[i] = text
        
    #     return modified_sents