search_mongodb_function = {
    "name": "search_mongodb",
    "description": "Searches the MongoDB database with the given query.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "object",
                "description": "MongoDB query as a JSON object to search the database."
            }
        },
        "required": ["query"],
    },
}