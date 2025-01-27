# Valencia SME Solutions

An AI-powered business analytics platform that provides comprehensive market intelligence and strategic recommendations for small and medium-sized enterprises (SMEs).

## Features

- **Dynamic Pricing Analysis**: Optimize pricing strategies based on market conditions and competitor data
- **Sentiment Analysis**: Understand customer feedback and improve satisfaction
- **Competitor Analysis**: Track and analyze competitor strategies
- **Sales Forecasting**: Predict future sales trends and opportunities

## Technologies Used

- **AI Models**: Claude-3 (Opus & Sonnet) via OpenRouter API
- **Data Sources**: TripAdvisor API (via RapidAPI)
- **Backend**: Python 3.8+, Flask
- **Frontend**: HTML5, JavaScript, Bootstrap
- **Dependencies**: See requirements.txt

## Getting Started

### Prerequisites

1. Python 3.8 or higher
2. OpenRouter API key (for AI analysis)
3. RapidAPI key (for TripAdvisor data)
4. Modern web browser

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Ola-Yeenca/sme_solution.git
cd valencia_sme_solutions
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys:
# OPENROUTER_API_KEY=your_openrouter_api_key
# RAPIDAPI_KEY=your_rapidapi_key
```

### Running the Application

1. Start the Flask server:
```bash
python api/app.py
```

2. Access the web interface:
```
http://localhost:8001
```

## API Documentation

### Base URL
```
http://localhost:8001/api/v1
```

### Authentication
No authentication required for local development. In production, implement appropriate authentication.

### Endpoints

#### 1. Dynamic Pricing Analysis
```
POST /analyze/pricing
```
Request body:
```json
{
    "business_name": "string",
    "business_type": "restaurant|hotel|attraction"
}
```
Response:
```json
{
    "status": "success",
    "data": {
        "analysis_text": "string"
    }
}
```

#### 2. Sales Forecasting
```
POST /analyze/forecast
```
Request body:
```json
{
    "business_name": "string",
    "business_type": "restaurant|hotel|attraction"
}
```
Response:
```json
{
    "status": "success",
    "data": {
        "analysis_text": "string"
    }
}
```

#### 3. Competitor Analysis
```
POST /analyze/competitors
```
Request body:
```json
{
    "business_name": "string",
    "business_type": "restaurant|hotel|attraction"
}
```
Response:
```json
{
    "status": "success",
    "data": {
        "analysis_text": "string"
    }
}
```

#### 4. Sentiment Analysis
```
POST /analyze/sentiment
```
Request body:
```json
{
    "business_name": "string",
    "business_type": "restaurant|hotel|attraction"
}
```
Response:
```json
{
    "status": "success",
    "data": {
        "analysis_text": "string"
    }
}
```

### Error Responses
```json
{
    "status": "error",
    "error": "error_type",
    "message": "error description"
}
```

Common error types:
- `invalid_request`: Missing or invalid parameters
- `api_error`: External API error
- `rate_limit`: Rate limit exceeded
- `server_error`: Internal server error

## Business Types Supported

- Restaurants
- Hotels
- Tourist Attractions

## Analysis Types

### 1. Dynamic Pricing Analysis
- Market position assessment
- Competitor price analysis
- Revenue optimization recommendations
- Implementation strategies

### 2. Sentiment Analysis
- Customer feedback analysis
- Emotion pattern recognition
- Service improvement suggestions
- Customer satisfaction tracking

### 3. Competitor Analysis
- Market positioning
- Competitive advantages
- Threat assessment
- Strategic recommendations

### 4. Sales Forecasting
- Revenue projections
- Growth opportunities
- Risk assessment
- Optimization strategies

## Environment Variables

Required environment variables:
```
OPENROUTER_API_KEY=your_openrouter_api_key
RAPIDAPI_KEY=your_rapidapi_key
```

## Support

- Documentation: See `/docs` directory
- Issue Tracking: GitHub Issues

## License

This project is proprietary software. All rights reserved.

## Contributing

Currently not accepting external contributions.

## Authors

- Ola Yinka

## Acknowledgments

- OpenRouter for AI model access
- TripAdvisor for business data
- All our beta testers and early adopters.
