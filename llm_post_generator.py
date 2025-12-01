import openai
import os
import json
from datetime import datetime

class LinkedInPostGenerator:
    def __init__(self, api_key=None):
        """Initialize OpenAI API client"""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Please set OPENAI_API_KEY environment variable or pass api_key")
        
        openai.api_key = self.api_key
        
        # Personality mode prompts
        self.personalities = {
            "business_bro": {
                "name": "Ultra Serious Business Bro",
                "prompt": """You are a LinkedIn user who treats everything like a serious business achievement. 
Write a LinkedIn post about a Fortnite victory royale as if it were a major corporate success.
Use business jargon like "strategic initiatives", "KPIs", "synergy", "leveraging core competencies", "optimizing outcomes".
Treat teammates as "stakeholders" and eliminations as "market disruptions".
Be completely serious and professional about the video game win.
Include 3-5 relevant business hashtags at the end.
Keep it to 3-5 short paragraphs with line breaks between each sentence for emphasis."""
            },
            
            "toxic_positivity": {
                "name": "Toxic Positivity Coach",
                "prompt": """You are an overly enthusiastic motivational speaker on LinkedIn.
Write a LinkedIn post about a Fortnite victory that turns it into an inspirational lesson about growth, mindset, and gratitude.
Use phrases like "grateful for the opportunity", "growth mindset", "embracing challenges", "journey not destination".
Everything is a profound life lesson. Be extremely positive and preachy.
End with "Agree?" or "What's your biggest takeaway?" or "Thoughts?"
Include 5-7 motivational hashtags like #GrowthMindset #Gratitude #NeverGiveUp.
Use lots of emojis (🙏 💪 ✨ 🚀).
Keep it to 3-4 paragraphs with dramatic line breaks."""
            },
            
            "fake_story": {
                "name": "Fake Story Teller", 
                "prompt": """You are a LinkedIn user who starts every post with a completely made-up personal story that seems unrelated.
Start with something like "My grandfather once told me..." or "I'll never forget when my mentor said..." or "Three years ago, I was sitting in a coffee shop when..."
Make the story emotional and seemingly profound, then awkwardly connect it to the Fortnite victory.
The connection should feel forced but presented as if it's deeply meaningful.
End with the actual victory mention almost as an afterthought.
Include 4-6 hashtags about leadership, wisdom, or life lessons.
Keep it to 4-6 paragraphs, building up to the reveal."""
            },
            
            "humble_brag": {
                "name": "Humble Brag Master",
                "prompt": """You are someone who disguises bragging as humility on LinkedIn.
Write about the Fortnite victory while constantly saying things like "I'm blessed", "grateful", "honored", "humbled".
Mention how you "couldn't have done it without the team" even though you're clearly bragging.
Act like winning at Fortnite is simultaneously no big deal AND a huge achievement.
Use phrases like "small win", "just trying to improve", "long way to go" while clearly celebrating.
Include 4-5 hashtags like #Blessed #Grateful #TeamWork #HumbleBeginnings.
Keep it to 3-4 paragraphs with false modesty throughout."""
            },
            
            "corporate_jargon": {
                "name": "Corporate Jargon Overlord",
                "prompt": """You are someone who speaks entirely in corporate buzzwords and business jargon.
Write about the Fortnite victory using as many buzzwords as possible: synergy, leverage, paradigm shift, circle back, touch base, move the needle, low-hanging fruit, drill down, take it offline, think outside the box, etc.
Make it almost incomprehensible with business speak.
Treat the victory like a quarterly earnings report or strategic planning session.
Include metrics and percentages even if they don't make sense.
Use 5-7 corporate hashtags like #Innovation #Disruption #Excellence #Strategy.
Keep it to 3-4 paragraphs of pure jargon."""
            },
            
            "self_aware": {
                "name": "Self-Aware Shitposter",
                "prompt": """You are someone who knows LinkedIn culture is ridiculous and leans into it ironically.
Write about the Fortnite victory while making fun of LinkedIn posting conventions.
Reference how absurd it is to post about video games on a professional network.
Use phrases like "Is this the kind of content you came to LinkedIn for?" or "Yes, I'm posting about Fortnite on LinkedIn. We've all lost our minds."
Be funny and self-deprecating while still somehow making it sound semi-professional.
Mock hashtag culture by including obviously silly ones.
Keep it to 3-4 paragraphs with a winking tone throughout."""
            }
        }
    
    def generate_post(self, personality="business_bro", extra_details=None):
        """
        Generate a LinkedIn post about a Fortnite victory
        
        Args:
            personality: One of the personality modes (business_bro, toxic_positivity, etc.)
            extra_details: Optional dict with game stats like {"kills": 7, "placement": 1, "mode": "Squads"}
        
        Returns:
            Generated LinkedIn post text
        """
        
        if personality not in self.personalities:
            personality = "business_bro"
        
        persona = self.personalities[personality]
        
        # Build the prompt
        system_prompt = persona["prompt"]
        
        user_prompt = "I just won a Victory Royale in Fortnite. Generate a LinkedIn post about it."
        
        if extra_details:
            details_text = "\n\nGame details:\n"
            if "kills" in extra_details:
                details_text += f"- Eliminations: {extra_details['kills']}\n"
            if "mode" in extra_details:
                details_text += f"- Game mode: {extra_details['mode']}\n"
            if "placement" in extra_details:
                details_text += f"- Final placement: #{extra_details['placement']}\n"
            user_prompt += details_text
        
        try:
            # Call OpenAI API (ChatGPT)
            response = openai.chat.completions.create(
                model="gpt-4o-mini",  # Super cheap and perfect for this!
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=800,
                temperature=0.9  # Higher temperature for more creative/funny posts
            )
            
            post_text = response.choices[0].message.content
            
            # Add signature with placeholder for hyperlink
            # The LinkedIn poster will convert this to an actual hyperlink
            post_text += "\n\n---\nQuality content brought to you by the Fortnite LinkedIn Auto-Poster"
            post_text += "\nhttps://www.youtube.com/watch?v=dQw4w9WgXcQ"
            
            return post_text
            
        except Exception as e:
            print(f"❌ Error generating post: {e}")
            return None
    
    def list_personalities(self):
        """List all available personality modes"""
        print("\n🎭 Available Personality Modes:\n")
        for key, persona in self.personalities.items():
            print(f"  {key}: {persona['name']}")
        print()

def test_generator():
    """Test the post generator"""
    print("🧪 Testing LinkedIn Post Generator\n")
    
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        print("   Get your API key from: https://platform.openai.com/api-keys")
        return
    
    generator = LinkedInPostGenerator()
    generator.list_personalities()
    
    print("Testing with 'business_bro' personality...\n")
    
    test_details = {
        "kills": 7,
        "mode": "Squads",
        "placement": 1
    }
    
    post = generator.generate_post(personality="business_bro", extra_details=test_details)
    
    if post:
        print("="*60)
        print("GENERATED LINKEDIN POST:")
        print("="*60)
        print(post)
        print("="*60)
    else:
        print("❌ Failed to generate post")

if __name__ == "__main__":
    test_generator()