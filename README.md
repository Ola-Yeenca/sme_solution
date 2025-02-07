# SME Analytica

A business analytics platform that provides AI-powered insights for SMEs.

## Features

- Dynamic pricing analysis using XGBoost
- Competitor analysis
- Sentiment analysis from customer reviews
- Market positioning insights
- Restaurant data analysis
- Hotel data analysis

## Quick Start

1. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export GOOGLE_PLACES_API_KEY="your_key_here"
export OPENROUTER_API_KEY="your_key_here"
export YELP_API_KEY="your_key_here"
```

3. Run the development server:
```bash
python -m smeanalytica.api.app
```

## API Endpoints

- `POST /api/v1/analyze`
  - Analyze business data and provide recommendations
  - Parameters:
    - `business_name`: Name of the business
    - `business_type`: Type of business (e.g., "restaurant", "hotel")
    - `analysis_type`: Type of analysis (e.g., "dynamic_pricing", "sentiment")
    - `location`: Business location (default: "Valencia, Spain")

## Frontend Development

```bash
cd smeanalytica-web
npm install
npm run dev
```

## Deployment

The frontend is deployed on GitHub Pages and the backend on Render.com.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
