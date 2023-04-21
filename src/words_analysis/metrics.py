import time

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


def tfidf_metric(files) -> pd.DataFrame:
    st = time.time()
    tfidf_vectorizer = TfidfVectorizer(input="filename")
    tfidf_vector = tfidf_vectorizer.fit_transform(files)
    tfidf_dataframe = pd.DataFrame(
        tfidf_vector.toarray(), 
        index=files, 
        columns=tfidf_vectorizer.get_feature_names_out()
    )

    tfidf_dataframe.loc["all_doc_freq"] = (tfidf_dataframe > 0).sum()
    tfidf_dataframe.to_csv("tfidf_metric.csv")

    end = time.time() - st
    print(f"Time: {end:.2f}\n")