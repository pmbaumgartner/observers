import os

from observers.observers.models.openai import wrap_openai
from observers.stores.duckdb import DuckDBStore
from openai import OpenAI

store = DuckDBStore().connect()

api_key = os.environ["HF_TOKEN"]
openai_client = OpenAI(
    base_url="https://api-inference.huggingface.co/v1/", api_key=api_key
)

client = wrap_openai(openai_client, store=store)

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-Coder-32B-Instruct",
    messages=[{"role": "user", "content": "Tell me a joke."}],
)
