# codebase-agent

A Python learning project: an AI agent that answers questions about a codebase.
It currently indexes the [`requests`](https://github.com/psf/requests) library and
searches it by meaning.

## How it works

1. **Chunking** (`main.py`): Python's built-in `ast` module splits every file into
   one chunk per function or method. Each chunk starts with a header naming its
   file, class, function and docstring.
2. **Indexing** (`build_index.py`): the chunks are embedded with Chroma's built-in
   `all-MiniLM-L6-v2` model and stored in a local Chroma database.
3. **Search** (`search.py`): a question is embedded and the 3 closest functions are
   returned.
4. **Evals** (`evaluate.py` + `evals.json`): 10 questions with known answers, scored
   by hit rate @3 (is the right function in the top 3 results?).

## Results

| Change | Hit rate @3 |
|---|---|
| Baseline: raw function code | 7/10 (70%) |
| Header with file, class and docstring at the top of each chunk | 8/10 (80%) |

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone --depth 1 https://github.com/psf/requests.git repos/requests
uv run build_index.py
uv run search.py how are cookies merged
uv run evaluate.py
```
