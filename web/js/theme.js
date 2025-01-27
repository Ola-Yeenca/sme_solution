// Theme Switcher
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.querySelector('.theme-toggle');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Load saved theme or use system preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.className = savedTheme;
        themeToggle.checked = savedTheme === 'dark-theme';
    } else {
        document.body.className = prefersDarkScheme.matches ? 'dark-theme' : 'light-theme';
        themeToggle.checked = prefersDarkScheme.matches;
    }
    
    // Handle theme toggle
    themeToggle.addEventListener('change', (e) => {
        const newTheme = e.target.checked ? 'dark-theme' : 'light-theme';
        document.body.className = newTheme;
        localStorage.setItem('theme', newTheme);
        
        // Trigger a smooth transition
        document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        setTimeout(() => {
            document.body.style.transition = '';
        }, 300);
    });
    
    // Listen for system theme changes
    prefersDarkScheme.addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            const newTheme = e.matches ? 'dark-theme' : 'light-theme';
            document.body.className = newTheme;
            themeToggle.checked = e.matches;
        }
    });
}); 