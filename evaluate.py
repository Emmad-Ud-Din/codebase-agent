import json

import chromadb

from config import COLLECTION_NAME, DB_PATH


def main() -> None:
    with open("evals.json", encoding="utf-8") as f:
        cases = json.load(f)

    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)

    hits = 0
    for case in cases:
        results = collection.query(query_texts=[case["question"]], n_results=3)
        found = [meta["name"] for meta in results["metadatas"][0]]

        passed = any(name in found for name in case["expected"])
        if passed:
            hits += 1

        mark = "PASS" if passed else "FAIL"
        print(f"[{mark}] {case['question']}")
        print(f"       expected: {case['expected']}")
        print(f"       got:      {found}")

    score = hits / len(cases) * 100
    print(f"\nHit rate @3: {hits}/{len(cases)} ({score:.0f}%)")


if __name__ == "__main__":
    main()
