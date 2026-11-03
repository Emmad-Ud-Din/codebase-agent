import sys

import chromadb

from config import COLLECTION_NAME, DB_PATH


def main() -> None:
    question = " ".join(sys.argv[1:])
    if not question:
        print('Usage: uv run search.py "your question"')
        return

    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)

    results = collection.query(query_texts=[question], n_results=3)

    print(f"Question: {question}\n")
    for meta, distance in zip(results["metadatas"][0], results["distances"][0]):
        print(f"{meta['name']}  ({meta['file']}, line {meta['start_line']})")
        print(f"  distance: {distance:.3f}\n")


if __name__ == "__main__":
    main()
