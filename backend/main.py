from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from tavily import TavilyClient
import os

load_dotenv()
app = FastAPI()

# initialize tavily client once at startup
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# defined the shape of my query here
class QueryRequest(BaseModel):
    query: str

@app.post("/deductra_ask")
async def deductra_ask(request: QueryRequest):
    # get the query from user
    query = request.query

    # check for if user has enough tokens/credits

    # check web search for similar query

    # web search to gather resources
    search_response = client.search(query, search_depth="advanced")
    web_results = search_response["results"]

    # context engineering + web search

    # hit LLM for the response