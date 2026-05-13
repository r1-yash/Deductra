from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from tavily import TavilyClient
from prompt import SYSTEM_PROMPT, PROMPT_TEMPLATE
from groq import Groq
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User
import uuid
import os

load_dotenv()
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# initialize tavily client once at startup
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# initialize groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# initialize SQLAlchemy engine + session once at startup
# (same pattern as groq/tavily clients — create once, reuse)
engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)

# 1 defined the shape of my query here
class QueryRequest(BaseModel):
    query: str

class UserSyncRequest(BaseModel):
    id: str        # this is the Supabase auth user id (UUID)
    email: str
    name: str | None = None  # optional, comes from GitHub profile

# called by frontend right after OAuth login
# checks if user exists in our users table, inserts if not
@app.post("/sync_user")
async def sync_user(request: UserSyncRequest):
    db = Session()

    # check if user already exists by email
    existing = db.query(User).filter(User.email == request.email).first()

    if not existing:
        # user logging in for the first time — insert into our users table
        # we use the same id as Supabase auth so they stay in sync
        user = User(
            id=uuid.UUID(request.id),  # convert string to UUID
            email=request.email,
            name=request.name
        )
        db.add(user)
        db.commit()

    db.close()
    return {"status": "ok"}

# existing endpoint — no changes here
@app.post("/deductra_ask")
async def deductra_ask(request: QueryRequest):
    # 2 get the query from user
    query = request.query

    # check for if user has enough tokens/credits

    # check web search for similar query

    # 3 web search to gather resources, the R of RAG, Retrieval part
    search_response = client.search(query, search_depth="advanced")
    web_results = search_response["results"]

    # 4 context engineering + web search
    prompt = PROMPT_TEMPLATE.format(
        web_search_results=web_results,
        user_query=query
    )

    # hit LLM for the response
    # .chat.completions.create is used because it's more universal for other LLM api calls as well
    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    return {
        "answer": completion.choices[0].message.content,
        "sources": [{"url": r["url"]} for r in web_results]
    }