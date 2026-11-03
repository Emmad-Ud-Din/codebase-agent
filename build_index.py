import chromadb

from config import COLLECTION_NAME, DB_PATH
from main import extract_functions, find_python_files


def main() -> None:
    files = find_python_files("repos/requests/src")
    chunks = []
    for file in files:
        chunks.extend(extract_functions(file))

    client = chromadb.PersistentClient(path=DB_PATH)
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(name=COLLECTION_NAME)

    collection.upsert(
        ids=[f"{c['file']}:{c['start_line']}" for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[
            {"name": c["name"], "file": c["file"], "start_line": c["start_line"]}
            for c in chunks
        ],
    )

    print(f"Indexed {collection.count()} functions.")


if __name__ == "__main__":
    main()
