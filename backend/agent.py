from retrieval import fetch_sources, load_index
from chat import prompt_answer

from mistralai import Mistral

import functools
import dotenv
import asyncio
import json
import time
import random
import os

model = "mistral-large-latest"

dotenv.load_dotenv()
API_KEY = os.environ.get("MISTRALAI_API_KEY")

db = load_index("index")

def create_messages():
    return [
        {
            "role": "system",
            "content": """You are a helpful bot on the Srijan'25 website and are here to assist with questions specific to any event or the fest in general. For every query, return concise, clear and relevant answers. You should check if the following context is sufficient to answer the user:
    Context:
    Srijan'25 is the annual techno-management fest organized by the Faculty of Engineering and Technology Students' Union (F.E.T.S.U.) at Jadavpur University. It is one of the largest of its kind in eastern India and attracts participation for diverse events. There are 40+ events (details of which can be found on the website). The fest is organized by F.E.T.S.U., JU for students and is a great opportunity to learn, compete, and network with peers.

    If the above context does not clearly contain the answer to the query, you must use the `db_search` tool to fetch relevant information about a specific event from the database and respond with that context. Always format tool calls in a structured way. If the above context is sufficient, call the `response` tool to provide a direct response to the query.
    Moreover, if the fetched context refers to an event with a different name or spelling, you will fail to answer and ask for further clarification. If the user asks for a general overview of Srijan'25 without reference to any event, you should use the `response` tool to provide a direct response to the query."""
        },
    ]

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

messages = create_messages()


client = Mistral(api_key=API_KEY)


def call_agent(query: str, use_tools: bool = True, retries=5, backoff_factor=1.5):
    global messages
    if use_tools:
        messages.append(
        {
            "role": "user", 
            "content": query
        })
    
    for attempt in range(retries):
        try:
            if use_tools:
                response = client.chat.complete(
                    model=model,
                    messages=messages,
                    tools=tools,
                    tool_choice="any",
                )
            else:
                response = client.chat.complete(
                    model=model,
                    messages=messages,
                )
            messages.append(response.choices[0].message)
            return response
        except Exception as e:
            if "Requests rate limit exceeded" in str(e):
                wait_time = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                messages = create_messages()

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
    response = call_agent(query, use_tools=False)
    messages.append({"role":"assistant", "content":response.choices[0].message.content})
    print(messages)
    if messages[-3]["role"] == "tool":
        if messages[-3]["name"] == "db_search":
            return response.choices[0].message.content
        else:
            return messages[-3]["content"]

if __name__ == "__main__":
    print(fetch_response("what is data drift?"))