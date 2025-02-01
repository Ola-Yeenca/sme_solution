"""Sentiment analysis for business reviews."""

import os
from typing import Dict, Any, List
import requests
import json
from shared.business_data_fetcher import BusinessDataFetcher
from shared.ai_model_config import AIModel, ModelConfig
from openai import OpenAI

class SentimentAnalyzer:
    """Analyzer for customer sentiment and feedback."""
    
    def __init__(self, data_fetcher: BusinessDataFetcher, business_type=None):
        """Initialize with a data fetcher and optional business type."""
        self.data_fetcher = data_fetcher
        self.business_type = business_type
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
            
        # Get the recommended model config for sentiment analysis
        self.model = ModelConfig.get_recommended_model("sentiment_analysis")
        self.model_config = ModelConfig.get_model_config(self.model)

    def analyze(self, business_name: str) -> Dict[str, Any]:
        """Analyze sentiment for a business using multiple data sources.
        
        Args:
            business_name: Name of the business to analyze
            
        Returns:
            Dictionary containing sentiment analysis results
        """
        # Fetch reviews from all available sources
        reviews = self.data_fetcher.get_reviews(business_name, limit=50)
        
        if not reviews:
            return {
                "error": "No reviews found for the business",
                "sentiment_score": 0,
                "strengths": [],
                "improvements": [],
                "themes": {"positive": [], "negative": []},
                "recommendations": [],
                "sources": []
            }
            
        # Get business data for context
        business_data = self.data_fetcher.get_business_data(business_name)
        
        # Perform AI analysis
        analysis = self._get_ai_analysis(business_data, reviews)
        
        # Add source information
        analysis["sources"] = business_data.get("sources", [])
        analysis["total_reviews_analyzed"] = len(reviews)
        
        return analysis
        
    def _get_ai_analysis(self, business_data: Dict[str, Any], reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get AI-powered sentiment analysis using Claude-3.
        
        Args:
            business_data: Business information for context
            reviews: List of reviews to analyze
            
        Returns:
            Dictionary containing detailed sentiment analysis
        """
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
        
        # Prepare review text with source and time context
        review_texts = []
        for review in reviews:
            source = review.get("source", "unknown")
            time = review.get("time", "unknown date")
            rating = review.get("rating", "no rating")
            text = review.get("text", "").strip()
            if text:
                review_texts.append("[Source: {}, Time: {}, Rating: {}]\n{}".format(source, time, rating, text))
        
        reviews_joined = "\n\n".join(review_texts[:50])
        prompt = (
            "Analyze these customer reviews for {}:\n\n"
            "Business Context:\n"
            "- Overall Rating: {}\n"
            "- Total Reviews: {}\n"
            "- Price Level: {}\n\n"
            "Reviews:\n"
            "{}  # Limit to 50 reviews for token limit\n\n"
            "Please provide a comprehensive analysis including:\n"
            "1. Overall sentiment score (1-10)\n"
            "2. Key strengths (top 3-5)\n"
            "3. Areas for improvement (top 3-5)\n"
            "4. Common themes in positive reviews\n"
            "5. Common themes in negative reviews\n"
            "6. Specific actionable recommendations\n"
            "7. Time-based trends (if noticeable)\n"
            "8. Price-value perception\n\n"
            "Format as JSON with these keys:\n"
            "{{\n"
            "    \"sentiment_score\": float,\n"
            "    \"strengths\": [str],\n"
            "    \"improvements\": [str],\n"
            "    \"themes\": {{\n"
            "        \"positive\": [str],\n"
            "        \"negative\": [str]\n"
            "    }},\n"
            "    \"recommendations\": [str],\n"
            "    \"trends\": {{\n"
            "        \"recent\": str,\n"
            "        \"price_perception\": str\n"
            "    }}\n"
            "}}\n"
        ).format(
            business_data.get('name', 'the business'),
            business_data.get('rating', 'N/A'),
            business_data.get('total_ratings', 'N/A'),
            business_data.get('price_level', 'N/A'),
            reviews_joined
        )
        
        try:
            response = client.chat.completions.create(
                model=self.model_config["model"],
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return {
                "error": str(e),
                "sentiment_score": 0,
                "strengths": [],
                "improvements": [],
                "themes": {"positive": [], "negative": []},
                "recommendations": [],
                "trends": {"recent": "", "price_perception": ""}
            }

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