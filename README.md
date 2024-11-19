# llmdump

This is a lightweight library for tracking and syncing LLM completions to a local store and a Hugging Face dataset.

## Usage

### Tracking OpenAI Requests with `wrap_openai`

```python
from openai import OpenAI
import os

store = Store().connect()

api_key = os.environ["HF_INFERENCE_API_KEY"]
openai_client = OpenAI(base_url="https://api-inference.huggingface.co/v1/", api_key=api_key)

client = wrap_openai(openai_client, store=store)

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-Coder-32B-Instruct",
    messages=[
        {"role": "user", "content": "Tell me a joke."}
    ],
)
```

### Viewing / Querying Local Store

The default store is [DuckDB](https://duckdb.org/) and can be viewed and queried using the [DuckDB CLI](https://duckdb.org/#quickinstall).

```bash
> duckdb store.db
> from openai_records limit 10;
┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬───┬─────────┬──────────────────────┬───────────┐
│          id          │        model         │      timestamp       │       messages       │ … │  error  │     raw_response     │ synced_at │
│       varchar        │       varchar        │      timestamp       │ struct("role" varc…  │   │ varchar │         json         │ timestamp │
├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼───┼─────────┼──────────────────────┼───────────┤
│ 89cb15f1-d902-4586…  │ Qwen/Qwen2.5-Coder…  │ 2024-11-19 17:12:3…  │ [{'role': user, 'c…  │ … │         │ {"id": "", "choice…  │           │
│ 415dd081-5000-4d1a…  │ Qwen/Qwen2.5-Coder…  │ 2024-11-19 17:28:5…  │ [{'role': user, 'c…  │ … │         │ {"id": "", "choice…  │           │
│ chatcmpl-926         │ llama3.1             │ 2024-11-19 17:31:5…  │ [{'role': user, 'c…  │ … │         │ {"id": "chatcmpl-9…  │           │
├──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴───┴─────────┴──────────────────────┴───────────┤
│ 3 rows                                                                                                                16 columns (7 shown) │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

