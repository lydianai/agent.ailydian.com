/**
 * Lydian Agent - Language Switcher
 * Seamless Turkish/English language switching without URL changes
 */

(function() {
    'use strict';

    // Get current language from localStorage or default to Turkish
    let currentLang = localStorage.getItem('lydian-lang') || 'tr';

    // Initialize language on page load
    document.addEventListener('DOMContentLoaded', function() {
        setLanguage(currentLang);
        updateLanguageButtons();
        attachEventListeners();
    });

    /**
     * Set the language for all elements with data-tr and data-en attributes
     */
    function setLanguage(lang) {
        currentLang = lang;
        localStorage.setItem('lydian-lang', lang);

        // Update all elements with language attributes
        const elements = document.querySelectorAll('[data-tr][data-en]');
        elements.forEach(element => {
            if (lang === 'tr') {
                element.textContent = element.getAttribute('data-tr');
            } else {
                element.textContent = element.getAttribute('data-en');
            }
        });

        // Update HTML lang attribute
        document.documentElement.lang = lang;

        // Update active button state
        updateLanguageButtons();
    }

    /**
     * Update active state of language buttons
     */
    function updateLanguageButtons() {
        const langButtons = document.querySelectorAll('.lang-btn');
        langButtons.forEach(btn => {
            const btnLang = btn.getAttribute('data-lang');
            if (btnLang === currentLang) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    /**
     * Attach click event listeners to language buttons
     */
    function attachEventListeners() {
        const langButtons = document.querySelectorAll('.lang-btn');
        langButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const selectedLang = this.getAttribute('data-lang');
                if (selectedLang !== currentLang) {
                    setLanguage(selectedLang);

                    // Add smooth transition effect
                    document.body.style.opacity = '0.8';
                    setTimeout(() => {
                        document.body.style.opacity = '1';
                    }, 150);
                }
            });
        });
    }

    // Expose setLanguage function globally for potential external use
    window.LydianLang = {
        set: setLanguage,
        get: () => currentLang
    };
})();
