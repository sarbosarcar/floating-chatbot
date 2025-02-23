# # Import relevant functionality
# from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
# from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
# from langgraph.checkpoint.memory import MemorySaver
# from langchain.memory import ConversationBufferMemory
# from langchain_core.runnables import RunnableConfig
# from langchain_core.tools import tool
# from langchain.agents import (Tool, AgentExecutor, create_react_agent, initialize_agent)
# from langchain.prompts import PromptTemplate
# from langchain import hub
# from langchain.llms import HuggingFaceHub
# from langgraph.graph import StateGraph, END
# import asyncio
# from typing import (
#     Annotated,
#     Sequence,
#     TypedDict,
# )
# from langchain_core.messages import BaseMessage
# from langgraph.graph.message import add_messages

# from langchain.prompts import PromptTemplate

from retrieval import fetch_sources, load_index
from chat import prompt_answer

from mistralai import Mistral

import functools
import dotenv
import asyncio
import json
import time
import os

model = "mistral-large-latest"

dotenv.load_dotenv()
API_KEY = os.environ.get("MISTRALAI_API_KEY")

db = load_index("index")

def db_search(query: str):
    """
    Search the database for relevant documents and return a reply based on the query.

    Args:
        query (str): The search query text to find relevant documents.

    Returns:
        str: A response to the user query based on the search results.
    """
    
    contents = fetch_sources(query, db, 1)
    # reply = await prompt_answer(question, contents)
    return contents

def response(reply: str):
    return reply

names_to_functions = {
    'db_search': functools.partial(db_search),
    'response': functools.partial(response),
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "db_search",
            "description": "Retrieve information about an event or topic from the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The event or topic to search the database for.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "response",
            "description": "Display direct response to a general query about overview of Srijan'25 without reference to any event",
            "parameters": {
                "type": "object",
                "properties": {
                    "reply": {
                        "type": "string",
                        "description": "Proper formatted response to the general query based on context in system prompt.",
                    }
                },
                "required": ["reply"],
            },
        },
    },
]

messages = [
    {
        "role": "system",
        "content": """You are a helpful bot on the Srijan'25 website and are here to assist with questions specific to any event or the fest in general. For every query, return concise, clear and relevant answers. You should check if the following context is sufficient to answer the user:
Context:
Srijan'25 is the annual techno-management fest organized by the Faculty of Engineering and Technology Students' Union (F.E.T.S.U.) at Jadavpur University. It is one of the largest of its kind in eastern India and attracts participation for diverse events. There are 40+ events (details of which can be found on the website). The fest is organized by F.E.T.S.U., JU for students and is a great opportunity to learn, compete, and network with peers.

If the above context does not clearly contain the answer to the query, you must use the `db_search` tool to fetch relevant information about a specific event from the database and respond with that context. Always format tool calls in a structured way. If the above context is sufficient, call the `response` tool to provide a direct response to the query."""
    },
]


client = Mistral(api_key=API_KEY)

# def call_agent(query: str):
#     messages.append(
#     {
#         "role": "user", 
#         "content": query
#     })
#     response = client.chat.complete(
#         model = model,
#         messages = messages,
#         tools = tools,
#         tool_choice = "any",
#     )
#     messages.append(response.choices[0].message)
#     return response
import time
import random

def call_agent(query: str, retries=5, backoff_factor=1.5):
    messages.append(
    {
        "role": "user", 
        "content": query
    })
    
    for attempt in range(retries):
        try:
            response = client.chat.complete(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="any",
            )
            messages.append(response.choices[0].message)
            return response
        except mistralai.models.sdkerror.SDKError as e:
            if "Requests rate limit exceeded" in str(e):
                wait_time = backoff_factor * (2 ** attempt) + random.uniform(0, 1)

def fetch_context(query: str):
    response = call_agent(query)
    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    function_params = json.loads(tool_call.function.arguments)
    function_result = names_to_functions[function_name](**function_params)
    if function_name == 'response':
        messages.append(
        {
            "role": "assistant",
            "content": function_result
        })
    return function_result

def fetch_response(query: str):
    response = call_agent(query)
    
    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    function_params = json.loads(tool_call.function.arguments)
    # print("\nfunction_name: ", function_name, "\nfunction_params: ", function_params)
    function_result = names_to_functions[function_name](**function_params)
    messages.append({"role": "tool", "name": function_name, "content": function_result, "tool_call_id": tool_call.id})
    response = client.chat.complete(
        model=model, 
        messages=messages
    )
    messages.append({"role":"assistant", "content":response.choices[0].message.content})
    print(messages)
    if messages[-2]["role"] == "tool":
        if messages[-2]["name"] == "db_search":
            return response.choices[0].message.content
        else:
            return messages[-2]["content"]

if __name__ == "__main__":
    print(fetch_response("What are the events related to phtotography?"))
    # print(response.choices[0].message.content)
# # Create the agent
# # memory = MemorySaver()
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key='output')

# class AgentState(TypedDict):
#     messages: Annotated[Sequence[BaseMessage], add_messages]

# # llm = HuggingFaceEndpoint(
# #     repo_id="meta-llama/Llama-3.2-3B-Instruct",
# #     # repo_id="mistralai/Mistral-7B-Instruct-v0.3",
# #     task="text-generation",
# #     max_new_tokens=512,
# #     huggingfacehub_api_token=API_KEY,
# #     temperature=0.1
# # )

# llm = HuggingFaceHub(
#     repo_id="mistralai/Mistral-7B-Instruct-v0.3",
#     model_kwargs={"temperature": 0.2, "max_length": 1024},
#     huggingfacehub_api_token=os.environ.get("HUGGINGFACEHUB_API_KEY")
# )

# @tool
# async def db_search(query: str):
#     """
#     Search the database for relevant documents and return a reply based on the query.

#     Args:
#         query (str): The search query text to find relevant documents.

#     Returns:
#         str: A response to the user query based on the search results.
#     """
    
#     contents = await fetch_sources(query, db, 2)
#     # reply = await prompt_answer(question, contents)
#     return contents

# model = ChatHuggingFace(llm=llm)

# tools = [
#     Tool(
#         name="DBSearch",
#         func=lambda query: asyncio.run(db_search(query)),
#         description="Search database for relevant documents. Contents of searches are stored in the database, so that they could be accessed through this tool"
#     )
# ]

# tools = [
#     # Tool(
#     #     name="Search",
#     #     func=lambda x: asyncio.run(fetch_sites(x)),
#     #     description="A search engine optimized for comprehensive, accurate, and trusted results. Useful for when you need to answer questions about current events. This returns only the answer - not the original source data.",
#     # ),
#     Tool(
#         name="DBSearch",
#         func=lambda query: asyncio.run(db_search(query)),
#         description="Search database for relevant documents. Contents of searches are cached in the database, so that they could be accessed through this tool"
#     ),
# ]

# 
#  for tool in tools}

# SYSTEM_PROMPT = hub.pull("hwchase17/react") + """You are a helpful bot on the Srijan'25 website and are here to assist with questions specific to any event or the fest in general. For every query, return concise, clear and relevant answers. You should check if the following context is sufficient to answer the user:
# Context:
# Srijan'25 is the annual techno-management fest organized by the Faculty of Engineering and Technology Students' Union (F.E.T.S.U.) at Jadavpur University. It is one of the largest of its kind in eastern India and attracts participation for diverse events. There are 40+ events (details of which can be found on the website). The fest is organized by students and for students and is a great opportunity to learn, compete, and network with peers.

# If the above context does not clearly contain the answer to the query, you must use the `DBsearch` tool to fetch relevant information about a specific event from the database and respond with that context. Always format tool calls in a structured way, for example, to call DBsearch, only return the function name, nothing else.

# Question:
# {query}
# """

# system_prompt = PromptTemplate(
#     input_variables=["query"],
#     template=SYSTEM_PROMPT
# )

# agent = initialize_agent(
#     tools, 
#     llm, 
#     agent="zero-shot-react-description", 
#     verbose=True, 
#     agent_kwargs={"system_message": SYSTEM_PROMPT} #system_prompt.format(query="{input}")}
#     )

# result = agent.run("What is srijan and who organizes it?")
# print(result)

# # Convert SYSTEM_PROMPT to a PromptTemplate
# prompt_template = PromptTemplate(input_variables=["input"], template=SYSTEM_PROMPT)

# agent_executor = create_react_agent(
#     llm=model, 
#     tools=tools, 
#     prompt=hub.pull("hwchase17/react"))

# rag_agent_executor = AgentExecutor(
#     agent=agent_executor,
#     tools=tools,
#     return_intermediate_steps=True,
#     verbose=True,
#     memory=memory,
#     handle_parsing_errors="Check your output and make sure it conforms! Do not output an action and a final answer at the same time.",
#     agent_executor_kwargs={
#         "max_iterations": 2,  
#         "max_execution_time": 20,  
#         "early_stopping_method": "generate"  
#     }
# )

# messages = [
#     SystemMessage(content=SYSTEM_PROMPT),
# ]

# # Define our tool node
# def tool_node(state: AgentState):
#     """
#     Tool node that runs all the tool calls in the last message and
#     appends the results to the state messages.
#     """
#     outputs = []
#     print("TOOL CALLED!")
#     for tool_call in state["messages"][-1].tool_calls:
#         tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
#         outputs.append(
#             ToolMessage(
#                 content=json.dumps(tool_result),
#                 name=tool_call["name"],
#                 tool_call_id=tool_call["id"],
#             )
#         )
#     return {"messages": outputs}

# # Define the node that calls the model
# def call_model(
#     state: AgentState,
#     config: RunnableConfig,
# ):
#     # this is similar to customizing the create_react_agent with 'prompt' parameter, but is more flexible
#     system_prompt = SystemMessage(SYSTEM_PROMPT)
#     response = model.invoke([system_prompt] + state["messages"], config)
#     # We return a list, because this will get added to the existing list
#     return {"messages": [response]}

# # Define the conditional edge that determines whether to continue or not
# def should_continue(state: AgentState):
#     messages = state["messages"]
#     last_message = messages[-1]
#     # If there is no function call, then we finish
#     if not last_message.tool_calls:
#         return "end"
#     # Otherwise if there is, we continue
#     else:
#         return "continue" #db_search(last_message.content)

# # Define a new graph
# workflow = StateGraph(AgentState)

# # Define the two nodes we will cycle between
# workflow.add_node("agent", call_model)
# workflow.add_node("tools", tool_node)

# # Set the entrypoint as `agent`
# # This means that this node is the first one called
# workflow.set_entry_point("agent")

# # We now add a conditional edge
# workflow.add_conditional_edges(
#     # First, we define the start node. We use `agent`.
#     # This means these are the edges taken after the `agent` node is called.
#     "agent",
#     # Next, we pass in the function that will determine which node is called next.
#     should_continue,
#     # Finally we pass in a mapping.
#     # The keys are strings, and the values are other nodes.
#     # END is a special node marking that the graph should finish.
#     # What will happen is we will call `should_continue`, and then the output of that
#     # will be matched against the keys in this mapping.
#     # Based on which one it matches, that node will then be called.
#     {
#         # If `tools`, then we call the tool node.
#         "continue": "tools",
#         # Otherwise we finish.
#         "end": END,
#     },
# )

# # We now add a normal edge from `tools` to `agent`.
# # This means that after `tools` is called, `agent` node is called next.
# workflow.add_edge("tools", "agent")

# # Now we can compile and visualize our graph
# graph = workflow.compile()

# # Helper function for formatting the stream nicely
# def print_stream(stream):
#     for s in stream:
#         message = s["messages"][-1]
#         if isinstance(message, tuple):
#             print(message)
#         else:
#             message.pretty_print()


# inputs = {"messages": [("user", "what is h42 and who are the organizers?")]}
# # print_stream(graph.stream(inputs, stream_mode="values"))
# print(*graph.stream(inputs, stream_mode="values"))





