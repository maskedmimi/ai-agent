from langchain_ollama import ChatOllama

llm = ChatOllama(model="qwen3:8b")
response = llm.invoke("Say hello in one sentence.")
print(response.content)
