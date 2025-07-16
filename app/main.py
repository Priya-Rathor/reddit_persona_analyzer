from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.reddit_routes import router as reddit_router

app = FastAPI(title="Reddit Persona Analyzer", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(reddit_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
