from openai import OpenAI
from app.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_enhanced_persona(data):
    """Generate a comprehensive persona using enhanced data"""
    
    # Prepare comprehensive data summary
    comments_sample = "\n\n".join([
        f"[{c['subreddit']}] {c['body'][:300]}..." if len(c['body']) > 300 else f"[{c['subreddit']}] {c['body']}"
        for c in data['comments'][:20] if c['body'] and c['body'] != '[deleted]'
    ])
    
    posts_sample = "\n\n".join([
        f"[{p['subreddit']}] {p['title']} - {p['selftext'][:400]}..." if len(p['selftext']) > 400 else f"[{p['subreddit']}] {p['title']} - {p['selftext']}"
        for p in data['posts'][:10] if p['selftext']
    ])
    
    # Activity analysis
    activity_summary = f"""
ACTIVITY ANALYSIS:
- Account Age: {data['account_age_days']} days
- Total Karma: {data['total_karma']} (Comments: {data['comment_karma']}, Posts: {data['link_karma']})
- Posts per day: {data['avg_posts_per_day']:.2f}
- Comments per day: {data['avg_comments_per_day']:.2f}
- Top Subreddits: {', '.join([f"{sub[0]} ({sub[1]})" for sub in data['top_subreddits'][:5]])}
- Most Active Hours: {', '.join([f"{hour[0]}:00 ({hour[1]} posts)" for hour in data.get('most_active_hours', [])[:3]])}
"""
    
    # Content analysis
    content_analysis = f"""
CONTENT ANALYSIS:
- Age Indicators: {data['content_analysis']['age_indicators']}
- Location Indicators: {data['content_analysis']['location_indicators']}
- Occupation Indicators: {data['content_analysis']['occupation_indicators']}
- Personality Traits: {data['content_analysis']['personality_traits']}
- Common Words: {', '.join([f"{word[0]} ({word[1]})" for word in data['content_analysis']['common_words'][:10]])}
"""

    prompt = f"""
You are an expert UX researcher creating detailed user personas. Based on comprehensive Reddit user data, generate a detailed persona profile following this enhanced format:

---ENHANCED PERSONA FORMAT---

USER PERSONA: {data['username']}
Age: [Best estimate based on indicators, or "Unknown"]
Occupation: [Best guess based on content, or "Unknown"]
Location: [Best guess based on content, or "Unknown"]
Status: [Single/Married/Unknown based on content]
Tier: [Early Adopter/Mainstream/Late Adopter based on tech engagement]
Archetype: [The Creator/The Explorer/The Helper/etc. based on behavior]

MOTIVATIONS (rate 1-10):
- Convenience: [score] - [brief explanation]
- Wellness: [score] - [brief explanation]
- Speed: [score] - [brief explanation]
- Guidance: [score] - [brief explanation]
- Comfort: [score] - [brief explanation]
- Social Connection: [score] - [brief explanation]

PERSONALITY TRAITS (position on scale 1-10):
- Introversion (1) ←→ Extroversion (10): [score] - [explanation]
- Intuition (1) ←→ Sensing (10): [score] - [explanation]
- Feeling (1) ←→ Thinking (10): [score] - [explanation]
- Perceiving (1) ←→ Judging (10): [score] - [explanation]

BEHAVIOR & HABITS:
- [Detailed observation about online behavior]
- [Posting patterns and timing]
- [Community engagement style]
- [Content consumption preferences]
- [Communication style and tone]

FRUSTRATIONS:
- [Specific pain points based on complaints/negative comments]
- [Technology or platform frustrations]
- [Social or communication challenges]
- [Time management issues]

GOALS & NEEDS:
- [Primary objectives based on post content]
- [Learning or growth aspirations]
- [Social or community needs]
- [Professional or personal development goals]

QUOTE:
"[Create a realistic quote that captures their voice and main concern/desire]"

SUPPORTING EVIDENCE:
- [Key comments or posts that support the persona]
- [Behavioral patterns observed]
- [Subreddit activity that reveals interests]

---USER DATA---

Username: {data['username']}
Created: {data['created_date']}

{activity_summary}

{content_analysis}

Recent Comments Sample:
{comments_sample}

Recent Posts Sample:
{posts_sample}

Generate a comprehensive, evidence-based persona that captures this user's digital personality, motivations, and behavioral patterns. Base all insights on the actual data provided and clearly indicate when information is inferred vs. explicitly stated.
"""

    print("🤖 Generating enhanced persona with GPT-4...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert UX researcher specializing in creating detailed, evidence-based user personas from digital behavior data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"❌ Error generating persona: {e}")
        return None
