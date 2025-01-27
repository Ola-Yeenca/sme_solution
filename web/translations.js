const translations = {
    en: {
        title: "Business Analysis",
        businessName: "Business Name",
        businessType: "Business Type",
        analysisType: "Analysis Type",
        restaurant: "Restaurant",
        hotel: "Hotel",
        attraction: "Tourist Attraction",
        pricing: "Dynamic Pricing",
        sentiment: "Sentiment Analysis",
        competitors: "Competitor Analysis",
        forecast: "Sales Forecast",
        analyze: "Analyze",
        results: "Results",
        error: "Error",
        loading: "Analyzing..."
    },
    es: {
        title: "Análisis de Negocio",
        businessName: "Nombre del Negocio",
        businessType: "Tipo de Negocio",
        analysisType: "Tipo de Análisis",
        restaurant: "Restaurante",
        hotel: "Hotel",
        attraction: "Atracción Turística",
        pricing: "Precios Dinámicos",
        sentiment: "Análisis de Sentimiento",
        competitors: "Análisis de Competencia",
        forecast: "Pronóstico de Ventas",
        analyze: "Analizar",
        results: "Resultados",
        error: "Error",
        loading: "Analizando..."
    }
};

// Language switcher functionality
document.addEventListener('DOMContentLoaded', function() {
    const langLinks = document.querySelectorAll('[data-lang]');
    let currentLang = 'en';

    // Function to update all translations
    function updateTranslations(lang) {
        document.querySelectorAll('[data-translate]').forEach(element => {
            const key = element.getAttribute('data-translate');
            if (translations[lang][key]) {
                if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                    element.placeholder = translations[lang][key];
                } else {
                    element.textContent = translations[lang][key];
                }
            }
        });

        // Update language nav links
        langLinks.forEach(link => {
            link.classList.toggle('active', link.getAttribute('data-lang') === lang);
        });

        currentLang = lang;
    }

    // Add click handlers for language switcher
    langLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const lang = link.getAttribute('data-lang');
            updateTranslations(lang);
        });
    });

    // Initial translation
    updateTranslations(currentLang);
});
