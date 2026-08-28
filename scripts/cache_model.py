#!/usr/bin/env python3
from sentence_transformers import SentenceTransformer


MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"


if __name__ == "__main__":
    model = SentenceTransformer(MODEL_ID)
    probe = model.encode(["deterministic model cache probe"], normalize_embeddings=True)
    print(MODEL_ID, probe.shape)
