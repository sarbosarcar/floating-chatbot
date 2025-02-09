import requests
import dotenv
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
from huggingface_hub import InferenceClient
# from retrieval import load_index
import json

dotenv.load_dotenv()
API_KEY = os.environ.get("HUGGINGFACEHUB_API_KEY")

# model_id = "meta-llama/Meta-Llama-3-8B-Instruct" 
model_id = "meta-llama/Meta-Llama-3-8B-Instruct" 

# Initialize the Hugging Face inference client
client = InferenceClient(model=model_id, token=API_KEY)

# Define the prompt template for a chatbot system
PROMPT_TEMPLATE = """
Context:
{context}

User Query:
{query}

Generate a helpful response.
"""

messages = [
    {
        "role": "system",
        "content": "You are an AI chatbot integrated on a website, helping users with their queries by providing appropriate responses based on the context provided. Respond in a concise, informative manner and maintain an approachable tone. If you do not know an answer clearly state so. You will not add extra information and provide the shortest, clearest possible answer. If the spellings for events retrieved do not match, do not reply with any details."
    },
]

# Function to generate a chatbot response
def prompt_answer(query, context):
    # Construct the prompt
    prompt = PROMPT_TEMPLATE.format(context=context, query=query)
    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )
    try:
        # Call the inference client
        response = client.chat_completion(messages, max_tokens=2048).choices[0].message.content
    except Exception as e:
        response = f"An error occurred! Please retry!: {e}"
    return response

def get_response(question: str):
    """Generates an AI response using the LLM chain with event data as context"""
    with open('data2/web_data.json', encoding="utf-8") as f:
        data = json.load(f)
    prompt = prompt_answer(question, data)
    return response