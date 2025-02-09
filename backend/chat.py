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

model_id = "meta-llama/Meta-Llama-3-8B-Instruct" 
# model_id = "deepset/roberta-base-squad2" 

# Initialize the Hugging Face inference client
client = InferenceClient(model=model_id, token=API_KEY)

# Define the prompt template for a chatbot system
PROMPT_TEMPLATE = """
You are an AI chatbot integrated on the Srijan website organized by the Faculty of Engineering & Technology Students' Union (F.E.T.S.U.) at Jadavpur University.Your task is to help users with their queries by providing appropriate responses based on the context provided. If you do not know an answer clearly state so. You will not add extra information, do not assume anything and provide the clearest possible answer. If the spellings for events retrieved do not match, do not reply with any details.
```
Context:
{context}
```
```
User Query:
{query}
```
Generate a helpful response.
Answer:
"""

# Function to generate a chatbot response
def prompt_answer(query, context):
    # Construct the prompt
    prompt = PROMPT_TEMPLATE.format(context=context, query=query)
    messages = [
        {
            "role": "system",
            "content": "You are an AI chatbot integrated on a website, helping users with their queries by providing appropriate responses based on the context provided. If you do not know an answer clearly state so. You will not add extra information, do not assume anything and provide the clearest possible answer. If the spellings for events retrieved do not match, do not reply with any details."
        },
    ]
    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )
    try:
        # Call the inference client
        # response = client.chat_completion(messages, max_new_tokens=128).choices[0].message.content
        response = client.text_generation(prompt, max_new_tokens=128, temperature=0.4).strip()
    except Exception as e:
        response = f"It seems like there was some trouble responding to the query! Please retry."
        print(e)
    return response

def get_response(question: str):
    """Generates an AI response using the LLM chain with event data as context"""
    with open('data2/web_data.json', encoding="utf-8") as f:
        data = json.load(f)
    prompt = prompt_answer(question, data)
    return response