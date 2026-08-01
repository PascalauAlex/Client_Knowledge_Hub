from config import settings
from openai import OpenAI



def _get_client(secret_key: str = settings.openai_key):
    _client = OpenAI(
        api_key=secret_key,
    )
    return _client


client = _get_client()

messages = [
    {"role": "system", "content": "You are a funny assistant"},
    {"role": "user", "content": "De cate ori a fost omul pe luna?"}
]
response = client.chat.completions.create(model="gpt-3.5-turbo",messages=messages, temperature=0.5)
print(response.choices[0].message.content)









