import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

text = "Hello world"

tokens = enc.encode(text)

print(tokens)