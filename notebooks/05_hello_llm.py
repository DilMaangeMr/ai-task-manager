from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()                      # reads .env into environment variables
client = Anthropic()               # picks up ANTHROPIC_API_KEY

resp = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=200,
    system="You are a concise assistant.",
    messages=[{"role": "user", "content": "Give me 3 tips to start a big task."}],
)
print(resp.content[0].text)
print("tokens in/out:", resp.usage.input_tokens, resp.usage.output_tokens)