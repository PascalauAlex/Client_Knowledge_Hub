import tiktoken
from urllib3.util import retry


def num_token_from_string(string: str, encoding_name: str = "cl100k_base")->int:
    """Returns the number of tokens in a string"""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


print(num_token_from_string(string="Test number of tokens per string"))