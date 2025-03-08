import fastapi
from fastapi import FastAPI
from routes import router
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app with metadata
app = FastAPI(
    title="PSN API",
    description="API for PSN services",
    version="0.1.0"
)

# Include the router from routes.py
app.include_router(router)

# Add a root endpoint that redirects to docs
@app.get("/", include_in_schema=False)
async def root_redirect():
    return {"message": "API is running."}

# This allows you to run the app with uvicorn
if __name__ == "__main__":
    import uvicorn
    # Use environment variables with defaults for configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host=host, port=port, reload=True)