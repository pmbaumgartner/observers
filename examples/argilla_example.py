import os

from observers.observers.models.openai import wrap_openai
from observers.stores.argilla import ArgillaStore
from openai import OpenAI

api_url = "https://argilla-synthetic-data-generator-argilla-reviewer.hf.space/"
api_key = "f_c6Kli8JQRkXaVpR4bFSPcE_XZF91gLOkTmE-wcqUlhRvPIfLKZiCE3YRv_IKgIHb7xRAXgPKn3EKRs3Ui17lWIHU6aynNfB3oTsSbVXMw"

store = ArgillaStore(api_url=api_url, api_key=api_key)

api_key = os.environ["HF_TOKEN"]
openai_client = OpenAI(
    base_url="https://api-inference.huggingface.co/v1/", api_key=api_key
)

client = wrap_openai(openai_client, store=store)

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-Coder-32B-Instruct",
    messages=[{"role": "user", "content": "Tell me a joke."}],
)
