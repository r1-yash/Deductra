from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from tavily import TavilyClient
from prompt import SYSTEM_PROMPT, PROMPT_TEMPLATE
from groq import Groq


import os

load_dotenv()
app = FastAPI()

# initialize tavily client once at startup
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

#initialize groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

#1 defined the shape of my query here
class QueryRequest(BaseModel):
    query: str

@app.post("/deductra_ask")
async def deductra_ask(request: QueryRequest):
    # 2 get the query from user
    query = request.query

    # check for if user has enough tokens/credits

    # check web search for similar query

    # 3 web search to gather resources
    search_response = client.search(query, search_depth="advanced")
    web_results = search_response["results"]

    # 4 context engineering + web search
    prompt = PROMPT_TEMPLATE.format(
        web_search_results = web_results,
        user_query = query
    )

    # hit LLM for the response
    ##this .chat.completions.create is used because it more universal for other LLM api calls as well
    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages = [
            {"role" : "system", "content" : SYSTEM_PROMPT},
            {"role" : "user", "content" : prompt}
        ]
    )
    return {
        "answer" : completion.choices[0].message.content,
        "sources": [{"url": r["url"]} for r in web_results]
    }
