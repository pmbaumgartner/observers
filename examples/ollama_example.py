from observers.observers.models.openai import wrap_openai
from observers.stores.duckdb import DuckDBStore
from openai import OpenAI

store = DuckDBStore().connect()

openai_client = OpenAI(
    base_url="http://localhost:11434/v1",
)

client = wrap_openai(openai_client, store=store)

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-Coder-32B-Instruct",
    messages=[{"role": "user", "content": "Tell me a joke."}],
)
