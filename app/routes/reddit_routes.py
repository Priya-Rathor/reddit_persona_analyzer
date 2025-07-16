from fastapi import APIRouter, HTTPException
from app.models.request_response import UserRequest, PersonaResponse
from app.services.reddit_scraper import EnhancedRedditUserScraper
from app.services.persona_generator import generate_enhanced_persona

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Reddit Persona Analyzer API"}

@router.post("/analyze_user", response_model=PersonaResponse)
async def analyze_user(request: UserRequest):
    scraper = EnhancedRedditUserScraper()
    
    username = request.username.strip("/").split("/")[-1] if "reddit.com/user/" in request.username else request.username
    data = scraper.scrape_user_profile(username, limit=request.limit)
    
    if not data:
        raise HTTPException(status_code=404, detail=f"User {username} not found")
    
    persona = generate_enhanced_persona(data)
    
    if not persona:
        raise HTTPException(status_code=500, detail="Failed to generate persona")
    
    return PersonaResponse(success=True, message="Analysis complete", persona=persona, raw_data=data)
