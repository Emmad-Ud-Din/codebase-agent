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
   returned. `hybrid.py` adds keyword search (BM25) and combines both rankings with
   Reciprocal Rank Fusion.
4. **Evals** (`evaluate.py` + `evals.json`): 15 questions with known answers, scored
   by hit rate @3 (is the right function in the top 3 results?). `compare.py` scores
   vector, keyword and hybrid search side by side.
5. **Agent** (`agent.py`): an LLM that uses `search_code` (hybrid search) as a tool. A hand-written
   agent loop runs the searches the model asks for and sends the results back until
   it gives a final answer, citing each function as `file:line`.

## Results

Chunking, measured on the first 10 questions with vector search:

| Change | Hit rate @3 |
|---|---|
| Baseline: raw function code | 7/10 (70%) |
| Header with file, class and docstring at the top of each chunk | 8/10 (80%) |

Search method, measured on all 15 questions (`uv run compare.py`):

| Method | Hit rate @3 |
|---|---|
| Keyword (BM25) | 11/15 (73%) |
| Vector | 12/15 (80%) |
| Hybrid (vector + BM25, Reciprocal Rank Fusion) | 13/15 (87%) |

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone --depth 1 https://github.com/psf/requests.git repos/requests
uv run build_index.py
uv run search.py how are cookies merged
uv run evaluate.py
uv run compare.py
```

The agent needs an Anthropic API key. Put it in a `.env` file (already in `.gitignore`):

```
ANTHROPIC_API_KEY=your-key-here
```

Then ask a question:

```bash
uv run --env-file .env agent.py how does the session handle redirects
```
