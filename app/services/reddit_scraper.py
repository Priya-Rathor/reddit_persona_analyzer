import re
from datetime import datetime
from collections import Counter
import praw
from app.config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT


class EnhancedRedditUserScraper:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )

    def extract_age_indicators(self, text):
        patterns = [
            r'(?:i\'?m|am|age)\s*(\d{1,2})',
            r'(\d{1,2})\s*(?:years?\s*old|yo|y/o)',
            r'born\s*in\s*(\d{4})',
            r'graduated\s*in\s*(\d{4})',
            r'class\s*of\s*(\d{4})'
        ]
        ages = []
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                if pattern.endswith('(\d{4})'):
                    age = datetime.now().year - int(match)
                    if 10 <= age <= 80:
                        ages.append(age)
                else:
                    age = int(match)
                    if 10 <= age <= 80:
                        ages.append(age)
        return ages

    def extract_location_indicators(self, text):
        patterns = [
            r'(?:from|in|live in|based in|located in)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(?:NYC|LA|SF|DC|UK|US|USA|Canada|Australia|Germany|France|Italy|Spain)',
            r'(?:New York|Los Angeles|San Francisco|London|Toronto|Sydney|Berlin|Paris|Madrid)'
        ]
        locations = []
        for pattern in patterns:
            locations += re.findall(pattern, text, re.IGNORECASE)
        return locations

    def extract_occupation_indicators(self, text):
        patterns = [
            r'(?:i\'?m a|work as|job as|profession|career)\s*([a-zA-Z\s]+)',
            r'(?:developer|engineer|teacher|doctor|nurse|student|manager|designer|analyst|consultant|lawyer|chef|writer|artist)',
            r'(?:software|web|data|product|project|marketing|sales|finance|HR|IT|tech)'
        ]
        occupations = []
        for pattern in patterns:
            occupations += re.findall(pattern, text.lower())
        return occupations

    def analyze_personality_traits(self, texts):
        traits = {
            'introversion': 0, 'extroversion': 0, 'analytical': 0, 'creative': 0,
            'optimistic': 0, 'pessimistic': 0, 'helpful': 0, 'critical': 0
        }
        patterns = {
            'introversion': [r'introvert', r'shy', r'quiet'],
            'extroversion': [r'extrovert', r'outgoing', r'social'],
            'analytical': [r'analyze', r'data', r'logic'],
            'creative': [r'creative', r'art', r'design'],
            'optimistic': [r'positive', r'hope', r'great'],
            'pessimistic': [r'negative', r'worst', r'hate'],
            'helpful': [r'help', r'support', r'assist'],
            'critical': [r'wrong', r'bad', r'disagree']
        }
        full_text = ' '.join(texts).lower()
        for trait, pats in patterns.items():
            for p in pats:
                traits[trait] += len(re.findall(p, full_text))
        return traits

    def scrape_user_profile(self, username, limit=100):
        try:
            user = self.reddit.redditor(username)
            user_created = user.created_utc
            data = {
                "username": username,
                "created_date": datetime.fromtimestamp(user_created).strftime('%Y-%m-%d'),
                "account_age_days": (datetime.now() - datetime.fromtimestamp(user_created)).days,
                "comment_karma": user.comment_karma,
                "link_karma": user.link_karma,
                "total_karma": user.comment_karma + user.link_karma,
                "posts": [],
                "comments": [],
                "posting_times": [],
                "subreddit_activity": {},
                "content_analysis": {
                    "age_indicators": [],
                    "location_indicators": [],
                    "occupation_indicators": [],
                    "personality_traits": {},
                    "common_words": [],
                }
            }

            # Collect posts
            for post in user.submissions.new(limit=limit):
                data["posts"].append({
                    "title": post.title,
                    "selftext": post.selftext,
                    "subreddit": str(post.subreddit),
                    "created_utc": post.created_utc,
                })
                data["posting_times"].append(datetime.fromtimestamp(post.created_utc).hour)

            # Collect comments
            for comment in user.comments.new(limit=limit):
                if comment.body and comment.body != '[deleted]':
                    data["comments"].append({
                        "body": comment.body,
                        "subreddit": str(comment.subreddit),
                        "created_utc": comment.created_utc,
                    })
                    data["posting_times"].append(datetime.fromtimestamp(comment.created_utc).hour)

            # Combine all text
            all_texts = [p["title"] + " " + p.get("selftext", "") for p in data["posts"]] + \
                        [c["body"] for c in data["comments"]]
            full_text = ' '.join(all_texts)

            # Content analysis
            data["content_analysis"]["age_indicators"] = self.extract_age_indicators(full_text)
            data["content_analysis"]["location_indicators"] = self.extract_location_indicators(full_text)
            data["content_analysis"]["occupation_indicators"] = self.extract_occupation_indicators(full_text)
            data["content_analysis"]["personality_traits"] = self.analyze_personality_traits(all_texts)

            # Common words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                          'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
                          'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she',
                          'it', 'we', 'they', 'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'its',
                          'our', 'their'}
            words = re.findall(r'\b[a-z]{4,}\b', full_text.lower())
            word_counts = Counter([word for word in words if word not in stop_words])
            data["content_analysis"]["common_words"] = word_counts.most_common(20)

            # === NEW METRICS FIX ===
            age_days = max(data["account_age_days"], 1)
            data["avg_posts_per_day"] = len(data["posts"]) / age_days
            data["avg_comments_per_day"] = len(data["comments"]) / age_days

            subreddit_counts = Counter([item["subreddit"] for item in data["posts"] + data["comments"]])
            data["subreddit_activity"] = dict(subreddit_counts)
            data["top_subreddits"] = subreddit_counts.most_common(10)

            if data["posting_times"]:
                hour_counts = Counter(data["posting_times"])
                data["most_active_hours"] = hour_counts.most_common(5)

            return data

        except Exception as e:
            print(f"Error scraping {username}: {e}")
            return None
