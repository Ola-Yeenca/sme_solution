// Chart configurations and rendering
class BusinessCharts {
    constructor() {
        this.charts = {};
        this.theme = 'dark';
    }

    // Initialize all charts
    initCharts() {
        this.initPriceChart();
        this.initCompetitorChart();
        this.initSentimentChart();
        this.initForecastChart();
    }

    // Update charts based on analysis results
    updateCharts(data, analysisType) {
        switch(analysisType) {
            case 'pricing':
                this.updatePriceChart(data);
                break;
            case 'competitors':
                this.updateCompetitorChart(data);
                break;
            case 'sentiment':
                this.updateSentimentChart(data);
                break;
            case 'forecast':
                this.updateForecastChart(data);
                break;
        }
    }

    // Price Analysis Chart
    initPriceChart() {
        const ctx = document.getElementById('priceChart');
        this.charts.price = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Your Price', 'Market Average', 'Premium Segment', 'Budget Segment'],
                datasets: [{
                    label: 'Price Positioning',
                    data: [0, 0, 0, 0],
                    borderColor: 'rgba(99, 102, 241, 1)',
                    backgroundColor: 'rgba(99, 102, 241, 0.2)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                }
            }
        });
    }

    // Competitor Analysis Chart
    initCompetitorChart() {
        const chart = echarts.init(document.getElementById('competitorChart'));
        this.charts.competitor = chart;
        
        const option = {
            tooltip: {
                trigger: 'item'
            },
            series: [{
                type: 'graph',
                layout: 'force',
                data: [],
                links: [],
                categories: [],
                roam: true,
                label: {
                    show: true,
                    position: 'right'
                },
                force: {
                    repulsion: 100
                }
            }]
        };
        
        chart.setOption(option);
    }

    // Sentiment Analysis Chart
    initSentimentChart() {
        const ctx = document.getElementById('sentimentChart');
        this.charts.sentiment = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Sentiment Score',
                    data: [],
                    borderColor: 'rgba(16, 185, 129, 1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1
                    }
                }
            }
        });
    }

    // Forecast Chart
    initForecastChart() {
        const chart = echarts.init(document.getElementById('forecastChart'));
        this.charts.forecast = chart;
        
        const option = {
            tooltip: {
                trigger: 'axis'
            },
            xAxis: {
                type: 'category',
                data: []
            },
            yAxis: {
                type: 'value'
            },
            series: [{
                data: [],
                type: 'line',
                smooth: true,
                areaStyle: {
                    opacity: 0.3
                }
            }]
        };
        
        chart.setOption(option);
    }

    // Update methods for each chart type
    updatePriceChart(data) {
        const { recommended_price_range, market_data } = data;
        this.charts.price.data.datasets[0].data = [
            recommended_price_range.avg,
            market_data.average,
            market_data.premium,
            market_data.budget
        ];
        this.charts.price.update();
    }

    updateCompetitorChart(data) {
        const nodes = data.competitors.map((comp, index) => ({
            name: comp.name,
            value: comp.rating,
            symbolSize: 30 + (comp.reviews_count / 100),
            category: comp.price_level
        }));

        const links = data.competitors.map(comp => ({
            source: 'Your Business',
            target: comp.name,
            value: comp.distance_km
        }));

        const option = {
            series: [{
                data: [
                    { name: 'Your Business', symbolSize: 50, category: 0 },
                    ...nodes
                ],
                links: links
            }]
        };

        this.charts.competitor.setOption(option);
    }

    updateSentimentChart(data) {
        const { sentiment_history } = data;
        this.charts.sentiment.data.labels = sentiment_history.map(item => item.date);
        this.charts.sentiment.data.datasets[0].data = sentiment_history.map(item => item.score);
        this.charts.sentiment.update();
    }

    updateForecastChart(data) {
        const { forecast_data } = data;
        const option = {
            xAxis: {
                data: forecast_data.map(item => item.date)
            },
            series: [{
                data: forecast_data.map(item => item.value)
            }]
        };
        
        this.charts.forecast.setOption(option);
    }

    // Theme handling
    setTheme(theme) {
        this.theme = theme;
        Object.values(this.charts).forEach(chart => {
            if (chart instanceof Chart) {
                // Update Chart.js themes
                chart.options.plugins.legend.labels.color = theme === 'dark' ? '#fff' : '#000';
                chart.update();
            } else {
                // Update ECharts themes
                chart.setTheme(theme === 'dark' ? 'dark' : '');
            }
        });
    }
}

// Extend BusinessCharts to support dynamic theme switching
BusinessCharts.prototype.toggleTheme = function(newTheme) {
    this.theme = newTheme;

    // Update Price Chart colors based on theme
    if(this.charts.price) {
        const darkColors = { border: 'rgba(99,102,241,1)', background: 'rgba(99,102,241,0.2)' };
        const lightColors = { border: 'rgba(37,99,235,1)', background: 'rgba(37,99,235,0.2)' };
        const colors = (newTheme === 'dark') ? darkColors : lightColors;
        this.charts.price.data.datasets[0].borderColor = colors.border;
        this.charts.price.data.datasets[0].backgroundColor = colors.background;
        this.charts.price.update();
    }

    // For competitor chart, and others, a similar update could be applied if needed.
    // This example only updates the Price Chart. Extend as required.
};

// Initialize charts
const businessCharts = new BusinessCharts();
document.addEventListener('DOMContentLoaded', () => businessCharts.initCharts()); 