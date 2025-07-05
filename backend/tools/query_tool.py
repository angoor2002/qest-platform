import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_mongodb.agent_toolkit import (
    MONGODB_AGENT_SYSTEM_PROMPT,
    MongoDBDatabase,
    MongoDBDatabaseToolkit,
)

# ATLAS_CONNECTION_STRING = 'mongodb+srv://ankursp:12345@cluster0.jz4jrmf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

mongo_uri=os.getenv('MONGODB_URI')

ATLAS_DB_NAME = 'qest_db'
# NATURAL_LANGUAGE_QUERY = 'Can you give me the details of the order with order id 21f6cd85-9d58-4543-9fe6-79abe38ca159?'


import os

from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI

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

def query_tool(query: str)->str:

    class NaturalLanguageToMQL:
        def __init__(self):
            self.llm = model
            self.system_message = MONGODB_AGENT_SYSTEM_PROMPT.format(top_k=5)
            self.db_wrapper = MongoDBDatabase.from_connection_string(
                                mongo_uri, 
                                database=ATLAS_DB_NAME)
            self.toolkit = MongoDBDatabaseToolkit(db=self.db_wrapper, llm=self.llm)
            self.agent = create_react_agent(
                            self.llm, 
                            self.toolkit.get_tools(), 
                            prompt=self.system_message)
            self.res = []

        def convert_to_mql_and_execute_query(self, query):
            # Start the agent with the agent.stream() method
            events = self.agent.stream(
                {"messages": [("user", query)]},
                stream_mode="values",
            )
            # Add output (events) from the agent to the self.messages list
            # self.res=events[-1]["messages"]
            for event in events:
                self.res=event["messages"]
            return self.res[-1].content
        
        def return_results(self):
            # Print the the end-user's expected output from 
            # the final message produced by the agent.
            print(self.messages[-1].content)

    converter = NaturalLanguageToMQL()
    res=converter.convert_to_mql_and_execute_query(query)
    return res

# if __name__ == '__main__':
#     print(query_tool(NATURAL_LANGUAGE_QUERY))