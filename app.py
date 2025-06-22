import os
import logging
import uvicorn
from dotenv import load_dotenv

from api import app

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")


def main():
    """Main function to start the application."""
    try:
        logger.info("Starting Hach-Pera AI API")
        
        # Start the FastAPI app with Uvicorn
        uvicorn.run(app, host=HOST, port=PORT)
        
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        raise

if __name__ == "__main__":
    main()
