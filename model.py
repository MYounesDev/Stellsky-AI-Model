import json
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import Tool, FunctionDeclaration
import os
import asyncio
import motor.motor_asyncio
from search_mongodb import search_mongodb_function

load_dotenv()

async def fetch_results(mongo_query: dict):
    MONGO_URI = os.getenv("MONGO_URI")
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client["Stellsky"]
    collection = db["users"]
    cursor = collection.find(mongo_query)
    results = await cursor.to_list(length=100)
    return results

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

tools = [
    Tool(function_declarations=[
        FunctionDeclaration(**search_mongodb_function)
    ])
]

model = genai.GenerativeModel(
    model_name="gemini-2.5-pro",
    tools=tools
)

def prepare_prompt(user_input: str) -> str:
    if "profile" in user_input.lower() or "analyze" in user_input.lower():
        return (
           "Search the database for user information. "
            "If a name is provided, query MongoDB using the 'full_name' field.\n\n"
            f"User query: {user_input}"
        )
    else:
        return user_input


async def get_response(user_input: str):
    user_input = (
        "You are an assistant that answers user questions.\n"
        "If the question requires user profile data, call the MongoDB search function with the appropriate query.\n"
        "Otherwise, answer directly.\n\n"
        f"User query: {user_input}"
    )
    prompt = prepare_prompt(user_input)
    response = model.generate_content(prompt)

    candidate = response.candidates[0]
    part = candidate.content.parts[0]

    if part.function_call:
        function_call = part.function_call
        print(f"Function to call: {function_call.name}")
        print(f"Arguments: {function_call.args}")

        mongo_query = function_call.args["query"]
        results = await fetch_results(mongo_query)
        print("MongoDB Results:", results)

        results_str = json.dumps(results, default=str, indent=2)  # default=str ile datetime vs çevrilir

        analysis_prompt = (
            f"User data found from the query results:\n{results_str}\n"
            "This data is based on, can you provide a brief analysis about the user?"
        )

        analysis_response = model.generate_content(analysis_prompt)
        analysis_text = analysis_response.candidates[0].content.parts[0].text

        return analysis_text
    else:
        print("No function call found.")
        direct_text = part.text
        print(direct_text)
        return direct_text

