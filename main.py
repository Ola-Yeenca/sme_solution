"""Main entry point for the Valencia SME Solutions application."""

import os
from typing import Optional
from dotenv import load_dotenv

from config.business_types import BusinessType
from shared.business_analyzer_factory import BusinessAnalyzerFactory
from solutions.dynamic_pricing import DynamicPricingEngine
from solutions.sentiment_analysis import SentimentAnalyzer
from solutions.competitor_analysis import CompetitorAnalyzer
from solutions.sales_forecasting import SalesForecastingEngine

def validate_environment():
    """Validate required environment variables."""
    required_vars = {
        "RAPIDAPI_KEY": "RapidAPI key for TripAdvisor API",
        "OPENROUTER_API_KEY": "OpenRouter API key for AI analysis"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        print("\nError: Missing required environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        print("\nPlease set these variables in your .env file or environment.")
        return False
    
    return True

def main():
    """Main function to run the business analysis framework."""
    # Load environment variables
    load_dotenv()
    
    # Validate environment
    if not validate_environment():
        return
    
    print("\nWelcome to Valencia SME Solutions!")
    
    # Display available business types
    print("\nAvailable business types:")
    for business_type in BusinessType:
        print(f"- {business_type.value}")
    
    # Get business type from user
    business_type_str = input("\nEnter your business type: ").lower()
    try:
        business_type = BusinessType(business_type_str)
    except ValueError:
        print(f"Error: Invalid business type '{business_type_str}'")
        return
    
    # Get business name from user
    business_name = input("\nEnter your business name: ")
    
    # Create business analyzer
    analyzer = BusinessAnalyzerFactory.create_analyzer(business_type)
    if not analyzer:
        return
    
    # Create analysis engines
    dynamic_pricing = DynamicPricingEngine(analyzer)
    sentiment_analyzer = SentimentAnalyzer(analyzer, os.getenv("OPENROUTER_API_KEY"))
    competitor_analyzer = CompetitorAnalyzer(analyzer)
    sales_forecasting = SalesForecastingEngine(analyzer)  # Only pass the analyzer
    
    while True:
        # Display analysis options
        print("\nAvailable analyses:")
        print("1. Dynamic Pricing Analysis")
        print("2. Sentiment Analysis")
        print("3. Competitor Analysis")
        print("4. Sales Forecasting")
        print("5. Exit")
        
        # Get user choice
        choice = input("\nSelect an analysis (1-5): ")
        
        if choice == "1":
            dynamic_pricing.analyze_pricing(business_name)
        elif choice == "2":
            sentiment_analyzer.analyze_sentiment(business_name)
        elif choice == "3":
            competitor_analyzer.analyze_competitors(business_name)
        elif choice == "4":
            sales_forecasting.forecast_sales(business_name)
        elif choice == "5":
            print("\nThank you for using Valencia SME Solutions!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()