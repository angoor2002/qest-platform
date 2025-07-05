from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env

model = AzureChatOpenAI(
    api_key=os.getenv("AZURE_OPENAI_CHAT_API_KEY"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_MODEL"),
    api_version=os.getenv("AZURE_OPENAI_CHAT_API_VERSION"),
    temperature=0.3,
    max_tokens=800,
    azure_endpoint=os.getenv("AZURE_OPENAI_CHAT_ENDPOINT"),
)

embeddings = AzureOpenAIEmbeddings(
    model=os.getenv("EMBEDDING_MODEL"),
    azure_endpoint=os.getenv("AZURE_OPENAI_EMBED_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_EMBED_API_KEY"),
    openai_api_version=os.getenv("AZURE_OPENAI_EMBED_API_VERSION"),
)