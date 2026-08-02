from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic, AuthenticationError, APIError

client = Anthropic()

try:
    resp = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=10,
        messages=[{"role": "user", "content": "Say hi"}],
    )
    print("Key works. Response:", resp.content[0].text)
except AuthenticationError:
    print("Key is missing or invalid — check .env and that load_dotenv() ran.")
except APIError as e:
    print(f"Key loaded, but request failed: {e}")