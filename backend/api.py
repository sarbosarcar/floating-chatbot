from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chat import prompt_answer
from retrieval import fetch_sources, load_index
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# Load the index
db = load_index("index")

# Allow CORS for dev and production environments
origins = [
    "http://localhost:5173",  # Development
    "https://floating-chatbot-frontend.vercel.app/",  # Replace with actual production domain
    "*"
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

# Define routes
@app.get("/")
def read_root():
    return {"message": "Welcome to the Srijan Fest Chatbot!"}

@app.post("/chat")
def ask_question(request: QuestionRequest):
    question = request.question
    contents = fetch_sources(question, db)
    reply = prompt_answer(question, contents)
    return {"response": reply}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")