import re

import chromadb
from rank_bm25 import BM25Okapi

from config import COLLECTION_NAME, DB_PATH

collection = chromadb.PersistentClient(path=DB_PATH).get_collection(
    name=COLLECTION_NAME
)


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


everything = collection.get(include=["documents", "metadatas"])
all_ids = everything["ids"]
id_to_name = {
    chunk_id: meta["name"] for chunk_id, meta in zip(all_ids, everything["metadatas"])
}
bm25 = BM25Okapi([tokenize(doc) for doc in everything["documents"]])


def vector_search(query: str, n: int) -> list[str]:
    results = collection.query(query_texts=[query], n_results=n)
    return results["ids"][0]


def keyword_search(query: str, n: int) -> list[str]:
    scores = bm25.get_scores(tokenize(query))
    ranked = sorted(zip(all_ids, scores), key=lambda pair: pair[1], reverse=True)
    return [chunk_id for chunk_id, score in ranked[:n]]


def hybrid_search(query: str, n: int) -> list[str]:
    combined = {}
    for ranking in (vector_search(query, 20), keyword_search(query, 20)):
        for rank, chunk_id in enumerate(ranking):
            combined[chunk_id] = combined.get(chunk_id, 0) + 1 / (60 + rank)
    ranked = sorted(combined, key=combined.get, reverse=True)
    return ranked[:n]


def names_for(ids: list[str]) -> list[str]:
    return [id_to_name[chunk_id] for chunk_id in ids]
