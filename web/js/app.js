document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS animations
    AOS.init({
        duration: 800,
        once: true,
        offset: 100
    });

    // Get user's location
    function getUserLocation() {
        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(
                position => {
                    const { latitude, longitude } = position.coords;
                    // Store coordinates in localStorage for use across the app
                    localStorage.setItem('userLocation', JSON.stringify({ latitude, longitude }));
                    // Get city name from coordinates using reverse geocoding
                    fetch(`https://api.opencagedata.com/geocode/v1/json?q=${latitude}+${longitude}&key=YOUR_OPENCAGE_API_KEY`)
                        .then(response => response.json())
                        .then(data => {
                            if (data.results && data.results[0]) {
                                const city = data.results[0].components.city || 
                                           data.results[0].components.town || 
                                           data.results[0].components.state;
                                localStorage.setItem('userCity', city);
                                updateLocationBasedContent(city);
                            }
                        })
                        .catch(error => console.error('Error getting city name:', error));
                },
                error => {
                    console.warn('Error getting location:', error);
                    // Fallback to IP-based location
                    fetch('https://ipapi.co/json/')
                        .then(response => response.json())
                        .then(data => {
                            localStorage.setItem('userCity', data.city);
                            localStorage.setItem('userLocation', JSON.stringify({
                                latitude: data.latitude,
                                longitude: data.longitude
                            }));
                            updateLocationBasedContent(data.city);
                        })
                        .catch(error => console.error('Error getting IP location:', error));
                }
            );
        } else {
            console.warn('Geolocation not supported');
            // Fallback to IP-based location
            fetch('https://ipapi.co/json/')
                .then(response => response.json())
                .then(data => {
                    localStorage.setItem('userCity', data.city);
                    localStorage.setItem('userLocation', JSON.stringify({
                        latitude: data.latitude,
                        longitude: data.longitude
                    }));
                    updateLocationBasedContent(data.city);
                })
                .catch(error => console.error('Error getting IP location:', error));
        }
    }

    // Update content based on user's location
    function updateLocationBasedContent(city) {
        // Update hero section text
        const heroTitle = document.querySelector('.hero-title');
        if (heroTitle) {
            heroTitle.innerHTML = `Transform Your Business in ${city}<span class="hero-subtitle">with AI-Powered Analytics</span>`;
        }

        // Update stats section with local data
        updateLocalStats(city);

        // Update demo form to include location
        const locationInput = document.getElementById('businessLocation');
        if (locationInput) {
            locationInput.value = city;
        }
    }

    // Update statistics based on location
    function updateLocalStats(city) {
        // Here you would typically fetch location-specific stats from your backend
        fetch(`/api/stats/${encodeURIComponent(city)}`)
            .then(response => response.json())
            .then(data => {
                // Update stats in the UI
                const statsElements = document.querySelectorAll('.stat-value');
                if (data.stats && statsElements.length) {
                    Object.keys(data.stats).forEach((key, index) => {
                        if (statsElements[index]) {
                            statsElements[index].textContent = data.stats[key];
                        }
                    });
                }
            })
            .catch(error => console.error('Error updating local stats:', error));
    }

    // Theme toggle functionality
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;

    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        body.classList.toggle('dark-theme', savedTheme === 'dark');
        themeToggle.checked = savedTheme === 'dark';
    }

    themeToggle.addEventListener('change', function() {
        body.classList.toggle('dark-theme');
        localStorage.setItem('theme', body.classList.contains('dark-theme') ? 'dark' : 'light');
    });

    // Demo form submission
    const demoForm = document.getElementById('demoForm');
    if (demoForm) {
        demoForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(demoForm);
            const data = Object.fromEntries(formData.entries());
            
            // Add location data
            const userLocation = localStorage.getItem('userLocation');
            if (userLocation) {
                data.location = JSON.parse(userLocation);
            }

            // Here you would typically send this data to your backend
            console.log('Demo requested for:', data);

            // Show success message
            alert('Thanks for your interest! We\'ll be in touch soon.');
            demoForm.reset();
        });
    }

    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Navbar scroll behavior
    const navbar = document.getElementById('dynamicIsland');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll <= 0) {
            navbar.classList.remove('scroll-up');
            return;
        }

        if (currentScroll > lastScroll && !navbar.classList.contains('scroll-down')) {
            // Scroll down
            navbar.classList.remove('scroll-up');
            navbar.classList.add('scroll-down');
        } else if (currentScroll < lastScroll && navbar.classList.contains('scroll-down')) {
            // Scroll up
            navbar.classList.remove('scroll-down');
            navbar.classList.add('scroll-up');
        }

        lastScroll = currentScroll;
    });

    // Initialize location-based features
    getUserLocation();
});
