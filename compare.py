import json

from hybrid import hybrid_search, keyword_search, names_for, vector_search

METHODS = {
    "vector": vector_search,
    "keyword": keyword_search,
    "hybrid": hybrid_search,
}


def main() -> None:
    with open("evals.json", encoding="utf-8") as f:
        cases = json.load(f)

    for method_name, search in METHODS.items():
        hits = 0
        for case in cases:
            found = names_for(search(case["question"], 3))
            if any(name in found for name in case["expected"]):
                hits += 1
            else:
                print(f"  [{method_name}] FAIL: {case['question']} -> {found}")
        print(
            f"{method_name:>8}: {hits}/{len(cases)} ({hits / len(cases) * 100:.0f}%)\n"
        )


if __name__ == "__main__":
    main()
