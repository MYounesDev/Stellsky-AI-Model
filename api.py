from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Any
import logging
import motor.motor_asyncio
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import httpx 
from model import get_response
from bson import ObjectId
from datetime import datetime

# Load env variables
load_dotenv()

# Logger config
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client["Stellsky"]  

# FastAPI setup
app = FastAPI(
    title="Hach-Pera AI API",
    description="AI-powered analysis API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #-
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/")
async def root():
    return {"status": "ok", "message": "AI API is running"}

# DB test
@app.get("/test-db-connection")
async def test_db_connection():
    try:
        await client.admin.command('ping')
        collections = await db.list_collection_names()
        return {"status": "success", "collections": collections}
    except Exception as e:
        logger.error(f"DB error: {e}")
        raise HTTPException(status_code=500, detail="DB connection failed")

def fix_mongo_types(results):
    fixed = []
    for doc in results:
        if not isinstance(doc, dict):
            fixed.append(doc) 
            continue
        
        fixed_doc = {}
        for k, v in doc.items():
            if isinstance(v, ObjectId):
                fixed_doc[k] = str(v)
            elif isinstance(v, datetime):
                fixed_doc[k] = v.isoformat()
            else:
                fixed_doc[k] = v
        fixed.append(fixed_doc)
    
    string_response = ""
    for i in fixed:
        string_response += i
    return string_response

# Request model
class PromptRequest(BaseModel):
    prompt: str

# POST endpoint
@app.post("/prompt-analyze")
async def prompt_analyze(request: PromptRequest):
    """
    Receives a prompt from the frontend (in JSON body),
    sends it to the external LLM API, and returns the LLM's response.
    """
    response = await get_response(request.prompt)
    
    fixed_results = fix_mongo_types(response)


    return {
        "status": "success",
        "llm_response": fixed_results

    }

# Request model
class AnalyzeRequest(BaseModel):
    user_id: str
    prompt: str

# Analyze profile
@app.post("/analyze-profile")
async def analyze_profile(request: AnalyzeRequest):
    try:
        user_data = await db["users"].find_one({"_id": request.user_id})
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")

        full_prompt = f"Prompt:\n{request.prompt}\n\nUser Info:\n{user_data}"
        #result = await call_llm(full_prompt)

        #return {"analysis": result}
    except Exception as e:
        logger.error(f"Error analyzing profile: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")
