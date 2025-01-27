"""Sentiment analysis for business reviews."""

import os
from typing import Dict, Any, List
import requests

from shared.business_data_fetcher import BusinessDataFetcher
from shared.ai_model_config import AIModel, ModelConfig

class SentimentAnalyzer:
    """Analyzer for customer sentiment and feedback."""
    
    def __init__(self, data_fetcher: BusinessDataFetcher):
        """Initialize with a data fetcher."""
        self.data_fetcher = data_fetcher
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
            
        # Get the recommended model config for sentiment analysis
        self.model = ModelConfig.get_recommended_model("sentiment_analysis")
        self.model_config = ModelConfig.get_model_config(self.model)

    def analyze(self, business_name: str) -> Dict[str, Any]:
        """Analyze sentiment for a business."""
        try:
            # Get business details and reviews
            business_data = self.data_fetcher.get_business_details(business_name)
            
            # Get AI analysis using Claude-3
            analysis = self._get_ai_analysis(business_data)
            
            return {
                'business_info': {
                    'name': business_name,
                    'rating': business_data['rating'],
                    'reviews_count': business_data['reviews_count']
                },
                'sentiment_analysis': analysis
            }
            
        except Exception as e:
            raise Exception(f"Error in sentiment analysis: {str(e)}")

    def _get_ai_analysis(self, business_data: Dict[str, Any]) -> str:
        """Get AI-powered sentiment analysis using Claude-3."""
        try:
            # Create detailed prompt
            prompt = f"""
            As a sentiment analysis expert, provide a comprehensive analysis of this business's customer feedback:
            
            BUSINESS INFO:
            - Name: {business_data.get('name', 'Unknown')}
            - Rating: {business_data.get('rating', 0)}/5.0
            - Reviews: {business_data.get('reviews_count', 0)}
            
            Please provide a detailed analysis including:
            1. SENTIMENT OVERVIEW
            - Overall customer sentiment trend
            - Key emotional patterns in feedback
            - Sentiment comparison with industry standards
            
            2. CUSTOMER EXPERIENCE
            - Key positive experiences
            - Common pain points
            - Service quality assessment
            
            3. SPECIFIC STRENGTHS
            - Standout positive features
            - Consistent praise points
            - Unique selling propositions
            
            4. IMPROVEMENT OPPORTUNITIES
            - Critical areas for enhancement
            - Customer suggestions
            - Service gaps identified
            
            5. ACTIONABLE RECOMMENDATIONS
            - Short-term improvements
            - Long-term strategic changes
            - Customer satisfaction metrics to track
            
            Format the response in clear sections with bullet points.
            Focus on actionable insights and specific examples where possible.
            """
            
            # Make API request with the configured model
            response = requests.post(
                url=self.model_config["url"],
                headers={
                    **self.model_config["headers"],
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "model": self.model_config["model"],
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error connecting to AI service: {str(e)}")
        except Exception as e:
            raise Exception(f"Error generating sentiment analysis: {str(e)}")

def analyze_sentiment(api_key, reviews):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )
    prompt = f"""
    Analyze these customer reviews and provide a detailed breakdown:

    Reviews:
    {reviews}

    Please provide:
    1. Overall sentiment score (1-10)
    2. Key strengths (top 3)
    3. Areas for improvement (top 3)
    4. Common themes in positive reviews
    5. Common themes in negative reviews
    6. Specific actionable recommendations
    7. Impact on pricing strategy

    Format the response as:
    SENTIMENT SCORE: [1-10]
    
    STRENGTHS:
    - [strength 1]
    - [strength 2]
    - [strength 3]
    
    IMPROVEMENTS NEEDED:
    - [improvement 1]
    - [improvement 2]
    - [improvement 3]
    
    POSITIVE THEMES:
    - [theme 1]
    - [theme 2]
    
    NEGATIVE THEMES:
    - [theme 1]
    - [theme 2]
    
    RECOMMENDATIONS:
    1. [recommendation 1]
    2. [recommendation 2]
    3. [recommendation 3]
    
    PRICING IMPACT:
    [Analysis of how sentiment affects pricing strategy]
    """
    
    try:
        response = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://github.com/codeusage",
                "X-Title": "Business Auto Optimization"
            },
            model="deepseek/deepseek-r1",
            messages=[
                {"role": "system", "content": "You are an expert restaurant business analyst specializing in customer feedback analysis and business optimization."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return "Error: Unable to analyze sentiment. Please try again later."

def categorize_reviews(reviews):
    categories = defaultdict(list)
    for review in reviews:
        rating = review.get('rating', 0)
        if rating >= 4:
            categories['positive'].append(review)
        elif rating <= 2:
            categories['negative'].append(review)
        else:
            categories['neutral'].append(review)
            
        review_text = review.get('text', '')
        if len(review_text) > 200:
            categories['detailed'].append(review)
            
        if review.get('is_recent', False):
            categories['recent'].append(review)
            
    return categories

def run_sentiment_analysis(reviews):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not reviews:
        print("No reviews found.")
        return
        
    
    categorized_reviews = categorize_reviews(reviews)
    
    
    print("\n=== Review Statistics ===")
    print(f"Total Reviews: {len(reviews)}")
    print(f"Positive Reviews: {len(categorized_reviews['positive'])}")
    print(f"Neutral Reviews: {len(categorized_reviews['neutral'])}")
    print(f"Negative Reviews: {len(categorized_reviews['negative'])}")
    print(f"Recent Reviews: {len(categorized_reviews['recent'])}")
    print(f"Detailed Reviews: {len(categorized_reviews['detailed'])}")
    
    
    print("\n=== Detailed Sentiment Analysis ===")
    sentiment_analysis = analyze_sentiment(api_key, reviews)
    print(sentiment_analysis)
    
    
    if categorized_reviews['recent']:
        print("\n=== Recent Reviews Analysis ===")
        recent_analysis = analyze_sentiment(api_key, categorized_reviews['recent'])
        print("Recent Trends:")
        print(recent_analysis)