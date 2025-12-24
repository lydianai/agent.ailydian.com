// Lydian Agent - Language Switcher
let currentLang = 'tr';

function switchLanguage(lang) {
    currentLang = lang;

    // Store preference
    localStorage.setItem('preferredLanguage', lang);

    // Update active button
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-lang') === lang) {
            btn.classList.add('active');
        }
    });

    // Update all text elements with data-tr and data-en attributes
    document.querySelectorAll('[data-tr][data-en]').forEach(el => {
        const text = lang === 'tr' ? el.getAttribute('data-tr') : el.getAttribute('data-en');
        if (text) {
            if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                el.placeholder = text;
            } else if (el.tagName === 'SELECT') {
                el.title = text;
            } else {
                el.textContent = text;
            }
        }
    });

    // Update document language
    document.documentElement.lang = lang;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Get saved language preference or use default
    const savedLang = localStorage.getItem('preferredLanguage') || 'tr';

    // Apply language
    switchLanguage(savedLang);

    // Add click handlers to language buttons
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const lang = this.getAttribute('data-lang');
            switchLanguage(lang);
        });
    });
});
