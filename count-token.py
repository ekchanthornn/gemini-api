count = client.models.count_tokens(
    model="gemini-3.8-flash",
    contents="Prompt ខ្ញុំ..."
)
print(f"Token: {count.total_tokens}")