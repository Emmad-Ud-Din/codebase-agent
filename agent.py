import sys

import anthropic
import chromadb

from config import COLLECTION_NAME, DB_PATH

MODEL = "claude-opus-5-5"

SYSTEM_PROMPT = """You answer questions about the source code of the Python `requests` library.
Use the search_code tool to find the relevant functions before you answer. If the first
results don't answer the question, search again with different words.
Base your answer only on code you found, and cite each function you rely on as file:line.
If you can't find the answer in the code, say so instead of guessing."""

TOOLS = [
    {
        "name": "search_code",
        "description": (
            "Search the requests library's source code by meaning. Returns the 5 most "
            "relevant functions, each with its file, line number, class, docstring "
            "and full source code."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What to look for, in plain English, e.g. 'how redirects are followed'.",
                },
            },
            "required": ["query"],
        },
    },
]

client = anthropic.Anthropic()
collection = chromadb.PersistentClient(path=DB_PATH).get_collection(
    name=COLLECTION_NAME
)


def search_code(query: str) -> str:
    results = collection.query(query_texts=[query], n_results=5)
    parts = []
    for meta, document in zip(results["metadatas"][0], results["documents"][0]):
        parts.append(f"--- {meta['file']}:{meta['start_line']} ---\n{document}")
    return "\n\n".join(parts)


def run_agent(question: str) -> str:
    messages = [{"role": "user", "content": question}]

    while True:
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
            output_config={"effort": "medium"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            break

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                query = block.input["query"]
                print(f"  [searching] {query}")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": search_code(query),
                    }
                )
        messages.append({"role": "user", "content": tool_results})

    if response.stop_reason == "refusal":
        return "Sorry, the model declined to answer this question."
    return "".join(block.text for block in response.content if block.type == "text")


def main() -> None:
    question = " ".join(sys.argv[1:])
    if not question:
        print('Usage: uv run --env-file .env agent.py "your question"')
        return

    print(f"Question: {question}\n")
    answer = run_agent(question)
    print(f"\n{answer}")


if __name__ == "__main__":
    main()
