from __future__ import annotations

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize


MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"


def tfidf_embeddings(documents: list[str]):
    vectorizer = TfidfVectorizer(
        lowercase=True, ngram_range=(1, 2), min_df=1, max_df=0.98,
        sublinear_tf=True, strip_accents="unicode", dtype=np.float64,
    )
    return normalize(vectorizer.fit_transform(documents)), vectorizer


def svd_embeddings(tfidf_matrix, seed: int = 42, rank: int = 100):
    components = min(rank, tfidf_matrix.shape[0] - 1, tfidf_matrix.shape[1] - 1)
    model = TruncatedSVD(n_components=components, algorithm="randomized", random_state=seed)
    return normalize(model.fit_transform(tfidf_matrix)), model


def sentence_embeddings(documents: list[str], batch_size: int = 32):
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_ID)
    matrix = model.encode(
        documents, batch_size=batch_size, show_progress_bar=False,
        convert_to_numpy=True, normalize_embeddings=True,
    )
    return matrix.astype(np.float64), model

