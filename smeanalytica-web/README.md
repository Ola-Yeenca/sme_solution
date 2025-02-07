# SMEAnalytica Web Application

SMEAnalytica is a modern web application designed to help small and medium-sized enterprises (SMEs) track their business metrics, analyze performance, and generate insightful reports.

## Features

- **Dashboard**: Get a quick overview of key business metrics
- **Analytics**: Visualize data with interactive charts and graphs
- **Reports**: Generate and export customized business reports
- **Settings**: Manage account preferences and notifications

## Tech Stack

- **Framework**: Next.js
- **UI Library**: Chakra UI
- **Charts**: Chart.js with react-chartjs-2
- **Icons**: React Icons
- **Styling**: Emotion (CSS-in-JS)
- **Type Checking**: TypeScript

## Getting Started

### Prerequisites

- Node.js 18.x or later
- npm or yarn package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/smeanalytica-web.git
cd smeanalytica-web
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Start the development server:
```bash
npm run dev
# or
yarn dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## Project Structure

```
smeanalytica-web/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/         # Next.js pages
│   ├── theme/         # Chakra UI theme customization
│   ├── types/         # TypeScript type definitions
│   └── utils/         # Utility functions
├── public/            # Static assets
└── package.json       # Project dependencies and scripts
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint for code quality

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Next.js](https://nextjs.org/)
- [Chakra UI](https://chakra-ui.com/)
- [Chart.js](https://www.chartjs.org/)
- [React Icons](https://react-icons.github.io/react-icons/)
