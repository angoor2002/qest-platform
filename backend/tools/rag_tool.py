import os
from uuid import uuid4
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI

from langchain.chains import RetrievalQA
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
import random

llm = AzureChatOpenAI(
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


def get_rag_answer(query: str) -> dict:
    collection_name: str = "qest_assignment"
    persist_dir: str = "chroma_dir"

    # Load persisted vector store
    vectorstore = Chroma(
        collection_name=collection_name,
        persist_directory=persist_dir,
        embedding_function=embeddings
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # Create QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    # Run inference
    result = qa_chain.invoke({"query": query})

    return (str(result["result"]))
    return {
        "answer": result["result"],
    }
