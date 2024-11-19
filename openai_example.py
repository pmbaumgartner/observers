from llmdump import Store, wrap_openai
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
