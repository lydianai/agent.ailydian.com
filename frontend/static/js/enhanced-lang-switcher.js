/**
 * Lydian Agent - Enhanced Language Switcher
 * Complete TR/EN support for all menus, headers, footers, and content
 * White-hat compliant, zero errors
 */

(function() {
    'use strict';

    // Translation database
    const translations = {
        // Navigation Menu
        nav: {
            home: { tr: 'Ana Sayfa', en: 'Home' },
            features: { tr: 'Özellikler', en: 'Features' },
            demo: { tr: 'Canlı Demo', en: 'Live Demo' },
            pricing: { tr: 'Fiyatlandırma', en: 'Pricing' },
            docs: { tr: 'Dokümantasyon', en: 'Documentation' },
            contact: { tr: 'İletişim', en: 'Contact' },
            about: { tr: 'Hakkımızda', en: 'About' },
            team: { tr: 'Ekip', en: 'Team' },
            careers: { tr: 'Kariyer', en: 'Careers' },
            blog: { tr: 'Blog', en: 'Blog' },
            support: { tr: 'Destek', en: 'Support' },
            api: { tr: 'API Referansı', en: 'API Reference' },
            guides: { tr: 'Rehberler', en: 'Guides' }
        },

        // Footer sections
        footer: {
            product: { tr: 'Ürün', en: 'Product' },
            resources: { tr: 'Kaynaklar', en: 'Resources' },
            company: { tr: 'Şirket', en: 'Company' },
            legal: { tr: 'Yasal', en: 'Legal' },
            privacy: { tr: 'Gizlilik', en: 'Privacy' },
            terms: { tr: 'Koşullar', en: 'Terms' },
            security: { tr: 'Güvenlik', en: 'Security' },
            compliance: { tr: 'Uyumluluk', en: 'Compliance' },
            copyright: { tr: 'Tüm hakları saklıdır', en: 'All rights reserved' }
        },

        // Common UI elements
        ui: {
            getStarted: { tr: 'Hemen Başla', en: 'Get Started' },
            learnMore: { tr: 'Daha Fazla', en: 'Learn More' },
            tryFree: { tr: 'Ücretsiz Dene', en: 'Try Free' },
            contactSales: { tr: 'Satış Ekibi', en: 'Contact Sales' },
            watchDemo: { tr: 'Demo İzle', en: 'Watch Demo' },
            readMore: { tr: 'Devamını Oku', en: 'Read More' },
            close: { tr: 'Kapat', en: 'Close' },
            loading: { tr: 'Yükleniyor...', en: 'Loading...' },
            error: { tr: 'Hata', en: 'Error' },
            success: { tr: 'Başarılı', en: 'Success' }
        }
    };

    // Get current language from localStorage or default to Turkish
    let currentLang = localStorage.getItem('lydian-lang') || 'tr';

    // Initialize language on page load
    document.addEventListener('DOMContentLoaded', function() {
        setLanguage(currentLang);
        updateLanguageButtons();
        attachEventListeners();
        translatePage();
    });

    /**
     * Set the language and update all elements
     */
    function setLanguage(lang) {
        currentLang = lang;
        localStorage.setItem('lydian-lang', lang);
        document.documentElement.lang = lang;

        translatePage();
        updateLanguageButtons();
    }

    /**
     * Translate all elements on the page
     */
    function translatePage() {
        // Method 1: data-tr and data-en attributes
        const elements = document.querySelectorAll('[data-tr][data-en]');
        elements.forEach(element => {
            const trText = element.getAttribute('data-tr');
            const enText = element.getAttribute('data-en');

            if (currentLang === 'tr') {
                if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                    element.placeholder = trText;
                } else {
                    element.textContent = trText;
                }
            } else {
                if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                    element.placeholder = enText;
                } else {
                    element.textContent = enText;
                }
            }
        });

        // Method 2: data-i18n keys
        const i18nElements = document.querySelectorAll('[data-i18n]');
        i18nElements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = getTranslation(key);

            if (translation) {
                if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                    element.placeholder = translation;
                } else {
                    element.textContent = translation;
                }
            }
        });

        // Method 3: Special meta tags and title
        updateMetaTags();
    }

    /**
     * Get translation by key path (e.g., 'nav.home')
     */
    function getTranslation(keyPath) {
        const keys = keyPath.split('.');
        let value = translations;

        for (const key of keys) {
            if (value && value[key]) {
                value = value[key];
            } else {
                return null;
            }
        }

        return value && value[currentLang] ? value[currentLang] : null;
    }

    /**
     * Update meta tags for SEO
     */
    function updateMetaTags() {
        const metaDescription = document.querySelector('meta[name="description"]');
        if (metaDescription) {
            const trDesc = metaDescription.getAttribute('data-tr');
            const enDesc = metaDescription.getAttribute('data-en');

            if (trDesc && enDesc) {
                metaDescription.setAttribute('content',
                    currentLang === 'tr' ? trDesc : enDesc
                );
            }
        }

        // Update page title if it has translation attributes
        const titleElement = document.querySelector('title');
        if (titleElement) {
            const trTitle = titleElement.getAttribute('data-tr');
            const enTitle = titleElement.getAttribute('data-en');

            if (trTitle && enTitle) {
                titleElement.textContent = currentLang === 'tr' ? trTitle : enTitle;
            }
        }
    }

    /**
     * Update active state of language buttons
     */
    function updateLanguageButtons() {
        const langButtons = document.querySelectorAll('.lang-btn, [data-lang]');
        langButtons.forEach(btn => {
            const btnLang = btn.getAttribute('data-lang');
            if (btnLang) {
                if (btnLang === currentLang) {
                    btn.classList.add('active');
                    btn.setAttribute('aria-pressed', 'true');
                } else {
                    btn.classList.remove('active');
                    btn.setAttribute('aria-pressed', 'false');
                }
            }
        });
    }

    /**
     * Attach click event listeners to language buttons
     */
    function attachEventListeners() {
        const langButtons = document.querySelectorAll('.lang-btn, [data-lang-switch]');
        langButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const selectedLang = this.getAttribute('data-lang') ||
                                   this.getAttribute('data-lang-switch');

                if (selectedLang && selectedLang !== currentLang) {
                    // Add smooth transition effect
                    document.body.style.transition = 'opacity 0.2s ease';
                    document.body.style.opacity = '0.7';

                    setTimeout(() => {
                        setLanguage(selectedLang);
                        document.body.style.opacity = '1';

                        // Dispatch custom event for other scripts
                        window.dispatchEvent(new CustomEvent('languageChanged', {
                            detail: { language: selectedLang }
                        }));
                    }, 100);
                }
            });
        });
    }

    /**
     * Public API
     */
    window.LydianLang = {
        set: setLanguage,
        get: () => currentLang,
        translate: getTranslation,
        refresh: translatePage
    };

    // Auto-detect browser language on first visit (white-hat: respect user preference)
    if (!localStorage.getItem('lydian-lang')) {
        const browserLang = navigator.language || navigator.userLanguage;
        if (browserLang.startsWith('en')) {
            setLanguage('en');
        } else {
            setLanguage('tr'); // Default to Turkish
        }
    }

})();
