from llmdump import Store, wrap_openai
from openai import OpenAI

store = Store().connect()

# make sure ollama is running locally
openai_client = OpenAI(base_url="http://localhost:11434/v1")

client = wrap_openai(openai_client, store=store)

response = client.chat.completions.create(
    model="llama3.1",
    messages=[
        {"role": "user", "content": "Who is your creator?"}
    ],
)
