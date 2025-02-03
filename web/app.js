let currentLang = 'en';

// Initialize translations
function updateTranslations() {
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        if (translations[currentLang][key]) {
            element.textContent = translations[currentLang][key];
        }
    });
}

// Format analysis results
function formatAnalysisResults(data, type) {
    // Get the analysis text from the response
    let analysisText = '';
    if (typeof data === 'string') {
        analysisText = data;
    } else if (data.analysis_text) {
        analysisText = data.analysis_text;
    } else if (data.data && data.data.analysis_text) {
        analysisText = data.data.analysis_text;
    } else {
        analysisText = JSON.stringify(data, null, 2);
    }

    // Format the text with proper HTML
    return `
        <div class="result-card" data-aos="fade-up">
            <div class="analysis-content">
                ${analysisText.split('\n').map(line => {
                    line = line.trim();
                    if (!line) return '';
                    if (line.match(/^\d+\./)) {
                        return `<h4 class="section-title mt-4">${line}</h4>`;
                    } else if (line.startsWith('-')) {
                        return `<p class="bullet-point">${line}</p>`;
                    } else {
                        return `<p>${line}</p>`;
                    }
                }).join('')}
            </div>
        </div>
    `;
}

// Show loading state
function showLoading(show) {
    const loadingCard = document.getElementById('loadingCard');
    const submitButton = document.querySelector('button[type="submit"]');
    const form = document.getElementById('analysisForm');

    if (show) {
        loadingCard.style.display = 'block';
        submitButton.disabled = true;
        form.classList.add('opacity-50');
    } else {
        loadingCard.style.display = 'none';
        submitButton.disabled = false;
        form.classList.remove('opacity-50');
    }
}

// Handle rate limit error
function handleRateLimit(retryAfter) {
    const minutes = Math.ceil(retryAfter / 60);
    return `
        <div class="alert alert-warning">
            <h4 class="alert-heading">
                <i class="bi bi-exclamation-triangle"></i> 
                ${translations[currentLang].error}
            </h4>
            <p>${translations[currentLang].rateLimitMessage}</p>
            <hr>
            <p class="mb-0">
                <i class="bi bi-clock"></i> 
                ${translations[currentLang].retryMessage.replace('{minutes}', minutes)}
            </p>
        </div>
    `;
}

// Language switcher
document.querySelectorAll('.nav-link[data-lang]').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const lang = e.target.getAttribute('data-lang');
        currentLang = lang;
        
        // Update active state
        document.querySelectorAll('.nav-link[data-lang]').forEach(l => {
            l.classList.remove('active');
        });
        e.target.classList.add('active');
        
        updateTranslations();
    });
});

// Theme handling
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.className = `${savedTheme}-theme`;
    document.getElementById('theme-toggle').checked = savedTheme === 'light';
    
    // Update charts if they exist
    if (typeof businessCharts !== 'undefined') {
        businessCharts.setTheme(savedTheme);
    }
}

function toggleTheme(e) {
    const theme = e.target.checked ? 'light' : 'dark';
    document.body.className = `${theme}-theme`;
    localStorage.setItem('theme', theme);
    
    // Update charts if they exist
    if (typeof businessCharts !== 'undefined') {
        businessCharts.setTheme(theme);
    }
}

// Dynamic Island behavior
function initializeDynamicIsland() {
    const navbar = document.getElementById('dynamicIsland');
    let lastScrollY = window.scrollY;
    let isExpanded = false;
    let expandTimeout;

    // Handle scroll behavior
    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;
        
        // Determine scroll direction
        if (currentScrollY > lastScrollY) {
            // Scrolling down - contract
            navbar.style.transform = 'translateX(-50%) scale(0.95)';
            navbar.style.opacity = '0.8';
        } else {
            // Scrolling up - expand
            navbar.style.transform = 'translateX(-50%) scale(1)';
            navbar.style.opacity = '1';
        }
        
        lastScrollY = currentScrollY;
    });

    // Handle hover behavior
    navbar.addEventListener('mouseenter', () => {
        clearTimeout(expandTimeout);
        if (!isExpanded) {
            isExpanded = true;
            navbar.style.transform = 'translateX(-50%) scale(1.02)';
            navbar.style.opacity = '1';
        }
    });

    navbar.addEventListener('mouseleave', () => {
        expandTimeout = setTimeout(() => {
            isExpanded = false;
            navbar.style.transform = 'translateX(-50%) scale(1)';
        }, 200);
    });

    // Add subtle animation on page load
    setTimeout(() => {
        navbar.style.transform = 'translateX(-50%) scale(1)';
        navbar.style.opacity = '1';
    }, 500);
}

// Form submission
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analysisForm');
    const resultsDiv = document.getElementById('analysisResults');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const businessName = document.getElementById('businessName').value;
        const businessType = document.getElementById('businessType').value;
        const analysisType = document.getElementById('analysisType').value;
        
        showLoading(true);
        document.getElementById('resultsContainer').classList.add('d-none');

        try {
            const response = await fetch(`/api/v1/analyze/${analysisType}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    business_name: businessName,
                    business_type: businessType
                })
            });

            const responseData = await response.json();
            
            if (response.ok) {
                document.getElementById('resultsContainer').classList.remove('d-none');
                resultsDiv.innerHTML = formatAnalysisResults(responseData.data, analysisType);
            } else {
                resultsDiv.innerHTML = `<div class="alert alert-danger">${responseData.message || 'An error occurred'}</div>`;
            }
        } catch (error) {
            resultsDiv.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        } finally {
            showLoading(false);
        }
    });

    // Initialize Dynamic Island
    initializeDynamicIsland();
    
    // Initialize theme
    initializeTheme();
    
    // Theme toggle
    document.getElementById('theme-toggle').addEventListener('change', toggleTheme);

    // Initialize translations
    updateTranslations();

    // Initialize AOS
    AOS.init({
        duration: 800,
        easing: 'ease-out',
        once: true
    });
});
