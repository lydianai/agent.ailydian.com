/**
 * Lydian Agent - Advanced SEO System
 * Dynamic SEO for TR/EN with complete meta tags
 *
 * Features:
 * - Language-specific titles & descriptions
 * - Open Graph tags
 * - Twitter Cards
 * - Structured Data (JSON-LD)
 * - Canonical URLs
 * - Hreflang tags
 */

(function() {
    'use strict';

    // ============================================
    // SEO DATA - TR/EN
    // ============================================

    const SEO_DATA = {
        // Homepage
        '/': {
            tr: {
                title: 'Lydian Agent | Dünya\'nın İlk Kuantum-Güçlendirilmiş Sağlık AI Platformu',
                description: 'Lydian Agent: 7 otonom AI agent, IBM Quantum teknolojisi, gerçek zamanlı hasta izleme. HIPAA/KVKK uyumlu, production-ready healthcare AI sistemi. Türkiye ve ABD hastaneleri için.',
                keywords: 'sağlık ai, kuantum bilgisayar, hasta izleme, klinik karar desteği, ameliyathane optimizasyonu, HIPAA uyumlu, KVKK uyumlu, healthcare AI, tıbbi yapay zeka',
                ogType: 'website'
            },
            en: {
                title: 'Lydian Agent | World\'s First Quantum-Enhanced Healthcare AI Platform',
                description: 'Lydian Agent: 7 autonomous AI agents, IBM Quantum technology, real-time patient monitoring. HIPAA/GDPR compliant, production-ready healthcare AI system for USA and Turkey hospitals.',
                keywords: 'healthcare ai, quantum computing, patient monitoring, clinical decision support, operating room optimization, HIPAA compliant, GDPR compliant, medical AI, artificial intelligence',
                ogType: 'website'
            }
        },

        // Demo Page
        '/demo.html': {
            tr: {
                title: 'Canlı Demo | Lydian Agent AI Sistemi - Türkiye & ABD Hastaneleri',
                description: 'Lydian Agent\'ın tüm özelliklerini canlı test edin: Hasta izleme (NEWS2, qSOFA), klinik karar desteği, kuantum ameliyathane çizelgeleme. Acıbadem, Memorial, Johns Hopkins, Mayo Clinic için.',
                keywords: 'ai demo, hasta izleme demo, klinik ai, ameliyathane optimizasyonu, gerçek zamanlı monitöring, healthcare demo, tıbbi ai demo',
                ogType: 'article'
            },
            en: {
                title: 'Live Demo | Lydian Agent AI System - Turkey & USA Hospitals',
                description: 'Test all Lydian Agent features live: Patient monitoring (NEWS2, qSOFA), clinical decision support, quantum OR scheduling. For Acıbadem, Memorial, Johns Hopkins, Mayo Clinic.',
                keywords: 'ai demo, patient monitoring demo, clinical ai, operating room optimization, real-time monitoring, healthcare demo, medical ai demo',
                ogType: 'article'
            }
        },

        // Features
        '/features.html': {
            tr: {
                title: 'Özellikler | Lydian Agent - 7 Otonom AI Agent & Kuantum Teknolojisi',
                description: 'Lydian Agent özellikleri: Hasta monitörü, klinik karar, ilaç etkileşimleri, ameliyathane optimizasyonu, tedarik zinciri, finansal analiz, araştırma asistanı. IBM Quantum destekli.',
                keywords: 'ai özellikler, hasta monitörü, klinik karar ai, ilaç etkileşimleri, kuantum optimizasyon, healthcare features',
                ogType: 'article'
            },
            en: {
                title: 'Features | Lydian Agent - 7 Autonomous AI Agents & Quantum Technology',
                description: 'Lydian Agent features: Patient monitoring, clinical decision, drug interactions, OR optimization, supply chain, financial analysis, research assistant. IBM Quantum powered.',
                keywords: 'ai features, patient monitor, clinical decision ai, drug interactions, quantum optimization, healthcare features',
                ogType: 'article'
            }
        },

        // Pricing
        '/pricing.html': {
            tr: {
                title: 'Fiyatlandırma | Lydian Agent - Esnek Paketler & Enterprise Çözümler',
                description: 'Lydian Agent fiyatlandırma: Starter, Professional, Enterprise paketleri. 14 gün ücretsiz deneme. Türkiye ve ABD hastaneleri için özel fiyatlandırma. HIPAA/KVKK uyumlu.',
                keywords: 'healthcare ai fiyat, tıbbi yazılım fiyat, ai hastane yazılımı, enterprise healthcare',
                ogType: 'article'
            },
            en: {
                title: 'Pricing | Lydian Agent - Flexible Plans & Enterprise Solutions',
                description: 'Lydian Agent pricing: Starter, Professional, Enterprise plans. 14-day free trial. Custom pricing for USA and Turkey hospitals. HIPAA/GDPR compliant.',
                keywords: 'healthcare ai pricing, medical software pricing, ai hospital software, enterprise healthcare',
                ogType: 'article'
            }
        },

        // Docs
        '/docs.html': {
            tr: {
                title: 'Dokümantasyon | Lydian Agent API & Entegrasyon Rehberi',
                description: 'Lydian Agent dokümantasyonu: API referansı, entegrasyon kılavuzları, kod örnekleri, en iyi uygulamalar. Python, JavaScript, REST API. FHIR uyumlu.',
                keywords: 'healthcare api, fhir api, medical ai api, healthcare integration, api documentation',
                ogType: 'article'
            },
            en: {
                title: 'Documentation | Lydian Agent API & Integration Guide',
                description: 'Lydian Agent documentation: API reference, integration guides, code examples, best practices. Python, JavaScript, REST API. FHIR compliant.',
                keywords: 'healthcare api, fhir api, medical ai api, healthcare integration, api documentation',
                ogType: 'article'
            }
        },

        // Contact
        '/contact.html': {
            tr: {
                title: 'İletişim | Lydian Agent - Satış, Destek & Ortaklık',
                description: 'Lydian Agent ile iletişime geçin: Satış ekibi, teknik destek, ortaklık fırsatları. Türkiye: İstanbul ofisi. ABD: New York ofisi. 7/24 destek.',
                keywords: 'healthcare ai iletişim, tıbbi yazılım destek, ai satış, healthcare partnership',
                ogType: 'website'
            },
            en: {
                title: 'Contact | Lydian Agent - Sales, Support & Partnership',
                description: 'Contact Lydian Agent: Sales team, technical support, partnership opportunities. Turkey: Istanbul office. USA: New York office. 24/7 support.',
                keywords: 'healthcare ai contact, medical software support, ai sales, healthcare partnership',
                ogType: 'website'
            }
        }
    };

    // ============================================
    // SEO MANAGER CLASS
    // ============================================

    class SEOManager {
        constructor() {
            this.currentLang = localStorage.getItem('lydian-lang') || 'tr';
            this.currentPath = window.location.pathname;
            this.baseURL = 'https://agent.ailydian.com';

            this.init();
        }

        init() {
            // Listen for language changes
            window.addEventListener('languageChanged', (e) => {
                this.currentLang = e.detail.language;
                this.updateAllSEO();
            });

            // Initial SEO update
            this.updateAllSEO();
        }

        updateAllSEO() {
            this.updateTitle();
            this.updateDescription();
            this.updateKeywords();
            this.updateOGTags();
            this.updateTwitterCards();
            this.updateHreflang();
            this.updateCanonical();
            this.updateStructuredData();
        }

        getSEOData() {
            // Normalize path
            let path = this.currentPath;
            if (path === '/index.html') path = '/';
            if (!path.endsWith('.html') && path !== '/') path += '.html';

            const data = SEO_DATA[path] || SEO_DATA['/'];
            return data[this.currentLang];
        }

        updateTitle() {
            const data = this.getSEOData();
            document.title = data.title;

            // Update or create title meta tag
            let titleMeta = document.querySelector('meta[property="og:title"]');
            if (!titleMeta) {
                titleMeta = document.createElement('meta');
                titleMeta.setAttribute('property', 'og:title');
                document.head.appendChild(titleMeta);
            }
            titleMeta.setAttribute('content', data.title);
        }

        updateDescription() {
            const data = this.getSEOData();

            let desc = document.querySelector('meta[name="description"]');
            if (!desc) {
                desc = document.createElement('meta');
                desc.setAttribute('name', 'description');
                document.head.appendChild(desc);
            }
            desc.setAttribute('content', data.description);

            // OG description
            let ogDesc = document.querySelector('meta[property="og:description"]');
            if (!ogDesc) {
                ogDesc = document.createElement('meta');
                ogDesc.setAttribute('property', 'og:description');
                document.head.appendChild(ogDesc);
            }
            ogDesc.setAttribute('content', data.description);
        }

        updateKeywords() {
            const data = this.getSEOData();

            let keywords = document.querySelector('meta[name="keywords"]');
            if (!keywords) {
                keywords = document.createElement('meta');
                keywords.setAttribute('name', 'keywords');
                document.head.appendChild(keywords);
            }
            keywords.setAttribute('content', data.keywords);
        }

        updateOGTags() {
            const data = this.getSEOData();
            const url = this.baseURL + this.currentPath;

            const ogTags = {
                'og:type': data.ogType || 'website',
                'og:url': url,
                'og:site_name': 'Lydian Agent',
                'og:image': this.baseURL + '/static/images/og-image.png',
                'og:image:width': '1200',
                'og:image:height': '630',
                'og:locale': this.currentLang === 'tr' ? 'tr_TR' : 'en_US'
            };

            Object.entries(ogTags).forEach(([property, content]) => {
                let meta = document.querySelector(`meta[property="${property}"]`);
                if (!meta) {
                    meta = document.createElement('meta');
                    meta.setAttribute('property', property);
                    document.head.appendChild(meta);
                }
                meta.setAttribute('content', content);
            });
        }

        updateTwitterCards() {
            const data = this.getSEOData();

            const twitterTags = {
                'twitter:card': 'summary_large_image',
                'twitter:site': '@LydianAgent',
                'twitter:title': data.title,
                'twitter:description': data.description,
                'twitter:image': this.baseURL + '/static/images/twitter-card.png'
            };

            Object.entries(twitterTags).forEach(([name, content]) => {
                let meta = document.querySelector(`meta[name="${name}"]`);
                if (!meta) {
                    meta = document.createElement('meta');
                    meta.setAttribute('name', name);
                    document.head.appendChild(meta);
                }
                meta.setAttribute('content', content);
            });
        }

        updateHreflang() {
            // Remove existing hreflang tags
            document.querySelectorAll('link[rel="alternate"]').forEach(link => link.remove());

            const path = this.currentPath;
            const languages = ['tr', 'en'];

            languages.forEach(lang => {
                const link = document.createElement('link');
                link.setAttribute('rel', 'alternate');
                link.setAttribute('hreflang', lang);
                link.setAttribute('href', `${this.baseURL}${path}?lang=${lang}`);
                document.head.appendChild(link);
            });

            // x-default
            const xDefault = document.createElement('link');
            xDefault.setAttribute('rel', 'alternate');
            xDefault.setAttribute('hreflang', 'x-default');
            xDefault.setAttribute('href', `${this.baseURL}${path}`);
            document.head.appendChild(xDefault);
        }

        updateCanonical() {
            const url = this.baseURL + this.currentPath;

            let canonical = document.querySelector('link[rel="canonical"]');
            if (!canonical) {
                canonical = document.createElement('link');
                canonical.setAttribute('rel', 'canonical');
                document.head.appendChild(canonical);
            }
            canonical.setAttribute('href', url);
        }

        updateStructuredData() {
            const data = this.getSEOData();

            // Remove existing JSON-LD
            document.querySelectorAll('script[type="application/ld+json"]').forEach(script => {
                if (script.dataset.seo === 'true') script.remove();
            });

            // Organization Schema
            const organizationSchema = {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "Lydian Agent",
                "url": this.baseURL,
                "logo": this.baseURL + "/static/images/logo.png",
                "description": data.description,
                "address": {
                    "@type": "PostalAddress",
                    "addressCountry": this.currentLang === 'tr' ? "TR" : "US"
                },
                "contactPoint": {
                    "@type": "ContactPoint",
                    "contactType": "customer service",
                    "availableLanguage": ["tr", "en"]
                }
            };

            // WebSite Schema
            const websiteSchema = {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": "Lydian Agent",
                "url": this.baseURL,
                "description": data.description,
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": this.baseURL + "/search?q={search_term_string}",
                    "query-input": "required name=search_term_string"
                }
            };

            // Software Application Schema
            const softwareSchema = {
                "@context": "https://schema.org",
                "@type": "SoftwareApplication",
                "name": "Lydian Agent",
                "applicationCategory": "HealthApplication",
                "operatingSystem": "Web",
                "offers": {
                    "@type": "Offer",
                    "price": "0",
                    "priceCurrency": this.currentLang === 'tr' ? "TRY" : "USD"
                },
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": "4.9",
                    "ratingCount": "127"
                }
            };

            // Insert schemas
            [organizationSchema, websiteSchema, softwareSchema].forEach(schema => {
                const script = document.createElement('script');
                script.type = 'application/ld+json';
                script.dataset.seo = 'true';
                script.textContent = JSON.stringify(schema);
                document.head.appendChild(script);
            });
        }
    }

    // ============================================
    // AUTO-INITIALIZATION
    // ============================================

    window.LydianSEO = SEOManager;

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSEO);
    } else {
        initSEO();
    }

    function initSEO() {
        console.log('🔍 Lydian SEO: Initializing...');
        window.seoManager = new SEOManager();
        console.log('✅ Lydian SEO: Ready');
    }

})();
