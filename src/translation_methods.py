import logging
logging.basicConfig(level=logging.WARNING)

import torch
import spacy
import pandas as pd
from PyQt5 import QtCore

from googletrans import Translator
from argostranslate import translate as argo_translate

from config.settings import Path, Constants


class Translators:
    __slots__ = ["_tr_method", "_src_lang", "_dest_lang", "_fairseq_model", "_google_translator"]
    def __init__(self, tr_method, src_lang, dest_lang) -> None:
        self._tr_method = tr_method
        self._src_lang = src_lang
        self._dest_lang = dest_lang
        self._google_translator = Translator()
        self._fairseq_model = torch.hub.load('pytorch/fairseq', 'transformer.wmt19.en-ru.single_model', tokenizer='moses', bpe='fastbpe', verbose=False)
        self._fairseq_model.cuda()

    def translate_text(self, txt: str) -> None:
        match self._tr_method:
            case "googletrans":
                return self._google_translator.translate(txt, src=self._src_lang, dest=self._dest_lang).text
            case "argotranslate":
                return argo_translate.translate(txt, from_code=self._src_lang, to_code=self._dest_lang)
            case "fairseq":
                return self._fairseq_model.translate(txt, verbose=False)
                


class CefrAndEfllexMethod:

    __slots__ = ["cefr_table", "efllex_table", "nlp"]

    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        self.cefr_table = pd.read_csv(Path.CEFR_DS_PATH, index_col=0)
        self.efllex_table = pd.read_csv(Path.EFLLEX_DS_PATH, index_col=0)

    def _get_cefr_level(self, word_, pos_) -> str | None:
        level = self.cefr_table[(self.cefr_table.word == word_) & (self.cefr_table.pos == pos_)]
        if level.empty:
            return None
        return level.cefr.item()
    
    def _get_efllex_level(self, word_, tag_) -> str | None:
        row = self.efllex_table[(self.efllex_table.word == word_) & (self.efllex_table.tag == tag_)]
        if row.empty:
            return None
        return row.iloc[:,2:].apply(lambda x: x.iloc[x.values.nonzero()[0]], axis=1).columns[0][-2:].upper()
    
    def _preprocess(self, file) -> str:

        with open(Path.USER_BOOKS.format(file), "r") as user_file:
            text = user_file.read()

        text = text.replace("\n", " ").replace("\t", " ")

        doc = self.nlp(text)
        return doc


    def translate(self, translators, file, levels, out_file_name, logger, batch_size=Constants.TEXT_BATCH_SIZE):
        logger.appendPlainText(f"Preprocessing file {file}...")
        QtCore.QCoreApplication.processEvents()

        parts = []
        size = 0
        
        open(out_file_name, "w").close()
        
        # Preprocess text
        doc = self._preprocess(file)
        sents_size = len(list(doc.sents))

        logger.appendPlainText(f"Preprocessing end...\nTranslating text...")
        QtCore.QCoreApplication.processEvents()

        for sent_n, sent in enumerate(doc.sents):
            parts.append("\n\n")
            size+=2

            if sent_n % 10 == 0:
                logger.appendPlainText(f"Progress {sent_n} / {sents_size} | {round(sent_n*100/sents_size, 2)} %")
                QtCore.QCoreApplication.processEvents()

            for i in range(len(sent) - 1):
                # Get current and next token
                c_t = sent[i]
                n_t = sent[i+1]
                str_end = "" if n_t.is_punct else " "

                if not (c_t.is_punct or c_t.is_stop):
                    
                    word_level = self._get_cefr_level(c_t.lemma_, spacy.explain(c_t.pos_)) or self._get_efllex_level(c_t.lemma_, c_t.tag_)
                    
                    # If word is not in selected levels set to None
                    if word_level not in levels: 
                        word_level = None
                    else:
                        tr_word = translators.translate_text(c_t.lemma_)

                    text = f"{c_t.text} ({c_t.lemma_} - {tr_word}){str_end}" if word_level is not None else c_t.text + str_end
                    size += len(text)
                    parts.append(text)
                
                else:
                    text = c_t.text  + str_end
                    size +=  len(text)
                    parts.append(text)

            if not parts[-1].endswith(Constants.END_PUNCT):
               parts.append(".")
               size += 1

            # If size of current part is bigger then batch_size, write it
            if size > batch_size:
                
                with open(out_file_name, "a") as user_file:
                    user_file.write("".join(parts))
                
                parts = []
                size = 0

        # If size < batch_size, but it's the last batch, then write it
        with open(out_file_name, "a") as user_file:
            user_file.write("".join(parts))
        
        logger.appendPlainText(f"{sents_size}/{sents_size} | 100% \nFinished.")
        QtCore.QCoreApplication.processEvents()