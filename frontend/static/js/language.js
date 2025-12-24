// Language Switcher - TR/EN
let currentLang = localStorage.getItem('language') || 'tr';

document.addEventListener('DOMContentLoaded', () => {
    setLanguage(currentLang);
    
    // Update active button on page load
    const langButtons = document.querySelectorAll('.lang-btn');
    langButtons.forEach(btn => {
        if (btn.dataset.lang === currentLang) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Add click event listeners to language buttons
    langButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const lang = btn.dataset.lang;
            setLanguage(lang);
            
            // Update active state
            langButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
});

function setLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('language', lang);
    
    // Update all elements with data-tr and data-en attributes
    document.querySelectorAll('[data-tr]').forEach(element => {
        if (lang === 'tr' && element.dataset.tr) {
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = element.dataset.trPlaceholder || element.dataset.tr;
            } else {
                element.textContent = element.dataset.tr;
            }
        } else if (lang === 'en' && element.dataset.en) {
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = element.dataset.enPlaceholder || element.dataset.en;
            } else {
                element.textContent = element.dataset.en;
            }
        }
    });
    
    // Update HTML lang attribute
    document.documentElement.lang = lang;
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { setLanguage, currentLang };
}
