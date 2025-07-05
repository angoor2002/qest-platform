import os
from uuid import uuid4
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI

from tools.create_tool import create_client,create_order
from tools.query_tool import query_tool
from tools.rag_tool import get_rag_answer

import random

checkpointer=MemorySaver()
config = {"configurable": {"thread_id": "user-123"}}

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


def agentic_workflow(message,session_id):
    route_decision=None
    @tool
    def queryTool(message: str) -> str:
        """
        A natural-language insights engine over our fitness and education database—covering clients, 
        orders, courses & classes. Translate user questions into MongoDB queries to retrieve data from a MongoDB database. Data like business KPIs 
        like revenue, enrollment, attendance, and client activity, should be easily retrieved.

        Should be able to handle questions like:
        - "How much revenue did we generate this month?"
        - "Which course has the highest enrollment?"
        - "What is the attendance percentage for Pilates?"
        - "How many inactive clients do we have?"
        - "Can you give me the details of order x?"

        """
        # print("Inside queryTool: ", message)
        res=query_tool(message)
        # print("Query tool res: ", res)
        return res
    
    @tool
    def createClient(name: str, email: str, phone: str) -> str:
        """
        Create a new client in the database.
        """
        name = name or ""
        email = email or ""
        phone = phone or ""
        try:
            create_client(name,email,phone)
            return f"Client {name} created with email {email} and phone {phone}."
        except Exception as e:
            return f" something went wrong in creating client"

    @tool
    def createOrder(client_id: str = None, service_id: str = None, amount: float = None, status: str = None,service_type: str=None) -> str:
        """
        Create a new order in the database.
        """
        if amount is None or status is None:
            return "Error: 'amount' and 'status' are required."
        client_id = client_id or str(uuid4())
        service_id = service_id or str(uuid4())
        amount= amount or 0.0000
        status=status or "pending"
        service_type=service_type or random.choice(["course","class"])
        
        try:
            create_order(client_id,service_id,amount,status)
            return f"Order created for client {client_id} with service {service_id}, amount {amount}, status {status}."
        except Exception as e:
            return f" something went wrong in creating Order"
    @tool
    def rag_tool(query: str)->str:
        """

        This tool retrieves relevant answers from a vector-based knowledge base built from the studio's FAQ PDF.
        It's ideal for handling general inquiries about studio policies, class guidelines, and health-related topics.

        Example usage:
        - "What should I bring to my first Pilates class?"
        - "Can I do yoga if I’m pregnant?"
        - "How many times a week should I attend to see results?"
        - "Is there a waitlist if a class is full?"
        - "Do you allow men in the classes?"
        - "What's the difference between Yoga and Pilates?"
        - "How do I cancel or reschedule my session?"
        - "What equipment does the studio provide?"
        - "Can Pilates help with back pain?"

        Returns:
            A string answer to the query based on the FAQ document.
        """
        return get_rag_answer(query)
    
    supportools=[queryTool,rag_tool, createClient, createOrder]
    dashboardtools=[queryTool]

    support_model_with_tools=llm.bind_tools(supportools)
    dashboard_model_with_tools=llm.bind_tools(dashboardtools)
    
    def supportAgent(state: MessagesState) -> dict:
        print("support Agent")
        messages=state["messages"]
        response= support_model_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def dashboardAgent(state: MessagesState) -> dict:
        print("dashboard Agent")
        messages=state["messages"]
        response= dashboard_model_with_tools.invoke(messages)
        return {"messages": [response]}

    def support_should_continue(state: MessagesState):
        last = state["messages"][-1]
        return "supporttools" if getattr(last, "tool_calls", None) else END
    
    def dashboard_should_continue(state: MessagesState):
        last = state["messages"][-1]
        return "dashboardtools" if getattr(last, "tool_calls", None) else END

    def route_decision(state: MessagesState):
        route = route_decision
        # print(f"Route decision: {route}")  # Debug print
        if route == "yes":
            return "supportAgent"
        elif route == "no":
            return "dashboardAgent"
        else:
            print(f"Unexpected route value: {route}")
            return "supportAgent"  # Default fallback instead of END

    def routerAgent(state):
        last = state["messages"][-1].content
        # print(f"Router processing: {last}")  # Debug print
        prompt = f"""
        You are an intelligent router deciding whether a query should go to the **supportAgent** or the **dashboardAgent**.

        **supportAgent** handles:
        - Client enquiries (search by name/email/phone)
        - Course/class information (list/filter services)
        - Order and payment status (paid, pending, dues)
        - Creating new clients or orders using external APIs

        **dashboardAgent** handles:
        - Business analytics and metrics
        - Revenue reports, outstanding payments
        - Client activity insights (active/inactive, birthdays)
        - Attendance and service trends

        Answer ONLY:
        - "yes" → if the query is for supportAgent
        - "no"  → if the query is for dashboardAgent

        Query: "{last}"
        Is this a supportAgent query?
        Answer only with "yes" or "no".
        """
        resp = llm.invoke(prompt).content.strip().lower()
        route_decision=resp.lower()

        return {"route": resp, "messages": state["messages"]}

    support_tool_node = ToolNode(supportools)
    dashboard_tool_node = ToolNode(dashboardtools)

    workflow = StateGraph(MessagesState)
    workflow.add_node("router", routerAgent)
    workflow.add_node("supportAgent", supportAgent)
    workflow.add_node("dashboardAgent", dashboardAgent)
    workflow.add_node("supporttools", support_tool_node)
    workflow.add_node("dashboardtools", dashboard_tool_node)

    workflow.add_edge(START, "router")
    workflow.add_conditional_edges("router", route_decision)
    
    workflow.add_conditional_edges("supportAgent", support_should_continue)
    workflow.add_conditional_edges("dashboardAgent", dashboard_should_continue)
    
    workflow.add_edge("supporttools", "supportAgent")
    workflow.add_edge("dashboardtools", "dashboardAgent")

    app_graph = workflow.compile(checkpointer=checkpointer)

    res = app_graph.invoke(
        {"messages": [HumanMessage(content=message)]},
        {"configurable": {"thread_id": session_id}}
    )

    return res['messages'][-1].content


# print(agentic_workflow("What are the different courses offered?","session_123"))