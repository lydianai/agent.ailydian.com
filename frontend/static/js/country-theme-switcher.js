/**
 * ============================================================================
 * LYDIAN MEDI - COUNTRY-SPECIFIC THEME SWITCHER
 * Automatically switches between Turkey (RED NEON) and USA (PURPLE NEON)
 * ============================================================================
 */

// Theme definitions
const themes = {
    turkey: {
        name: 'Turkey Red Neon',
        colors: {
            '--lydian-primary': '#ff0033',
            '--lydian-secondary': '#ff3366',
            '--lydian-accent': '#ff6699',
            '--lydian-gold': '#ffaa00',
            '--neon-red': '#ff0033',
            '--neon-red-bright': '#ff3366',
            '--neon-pink': '#ff6699',
            '--neon-orange': '#ff6600',
            '--dark-bg': '#0a0a0f',
            '--dark-card': '#131318',
            '--dark-border': '#1f1f28',
            '--text-primary': '#ffffff',
            '--text-secondary': '#e0e0e8',
            '--text-muted': '#a0a0b8',
            '--gradient-lydian': 'linear-gradient(135deg, #ff0033 0%, #ff3366 50%, #ff6699 100%)',
            '--gradient-neon': 'linear-gradient(135deg, #ff0033 0%, #ff6600 100%)',
            '--gradient-medical': 'linear-gradient(135deg, #ff0033 0%, #ff6699 100%)',
            '--gradient-health': 'linear-gradient(135deg, #ff3366 0%, #ff6699 100%)',
            '--gradient-premium': 'linear-gradient(135deg, #ff0033 0%, #ff6600 100%)'
        },
        gridColors: {
            primary: 'rgba(255, 0, 51, 0.05)',
            secondary: 'rgba(255, 51, 102, 0.05)'
        },
        borderColor: 'rgba(255, 0, 51, 0.2)',
        shadowColor: 'rgba(255, 0, 51, 0.4)',
        glowColor: 'rgba(255, 0, 51, 0.6)'
    },
    usa: {
        name: 'USA Purple Neon',
        colors: {
            '--lydian-primary': '#9933ff',
            '--lydian-secondary': '#aa66ff',
            '--lydian-accent': '#cc99ff',
            '--lydian-gold': '#ffaa00',
            '--neon-purple': '#9933ff',
            '--neon-purple-bright': '#aa66ff',
            '--neon-violet': '#cc99ff',
            '--neon-magenta': '#ff00ff',
            '--dark-bg': '#0a0a0f',
            '--dark-card': '#131318',
            '--dark-border': '#1f1f28',
            '--text-primary': '#ffffff',
            '--text-secondary': '#e0e0e8',
            '--text-muted': '#a0a0b8',
            '--gradient-lydian': 'linear-gradient(135deg, #9933ff 0%, #aa66ff 50%, #cc99ff 100%)',
            '--gradient-neon': 'linear-gradient(135deg, #9933ff 0%, #ff00ff 100%)',
            '--gradient-medical': 'linear-gradient(135deg, #9933ff 0%, #cc99ff 100%)',
            '--gradient-health': 'linear-gradient(135deg, #aa66ff 0%, #cc99ff 100%)',
            '--gradient-premium': 'linear-gradient(135deg, #9933ff 0%, #ff00ff 100%)'
        },
        gridColors: {
            primary: 'rgba(153, 51, 255, 0.05)',
            secondary: 'rgba(170, 102, 255, 0.05)'
        },
        borderColor: 'rgba(153, 51, 255, 0.2)',
        shadowColor: 'rgba(153, 51, 255, 0.4)',
        glowColor: 'rgba(153, 51, 255, 0.6)'
    }
};

/**
 * Detects country based on language and content
 */
function detectCountry() {
    // Check HTML lang attribute
    const htmlLang = document.documentElement.lang;
    if (htmlLang === 'tr') {
        return 'turkey';
    } else if (htmlLang === 'en') {
        return 'usa';
    }

    // Check page content for Turkish keywords
    const bodyText = document.body.textContent || '';
    const turkishKeywords = ['Türkiye', 'Türk', 'hasta', 'sağlık', 'hastane', 'doktor'];
    const hasTurkishContent = turkishKeywords.some(keyword => bodyText.includes(keyword));

    if (hasTurkishContent) {
        return 'turkey';
    }

    // Check for USA-specific content
    const usaKeywords = ['United States', 'USA', 'American', 'patient', 'hospital', 'doctor'];
    const hasUsaContent = usaKeywords.some(keyword => bodyText.includes(keyword));

    if (hasUsaContent) {
        return 'usa';
    }

    // Default to Turkey (since most content is Turkey-focused)
    return 'turkey';
}

/**
 * Applies the theme to the page
 */
function applyTheme(themeName) {
    const theme = themes[themeName];
    if (!theme) {
        console.error('Theme not found:', themeName);
        return;
    }

    console.log(`Applying ${theme.name} theme...`);

    // Apply CSS variables
    const root = document.documentElement;
    Object.entries(theme.colors).forEach(([property, value]) => {
        root.style.setProperty(property, value);
    });

    // Update grid background
    const gridBg = document.querySelector('.grid-bg');
    if (gridBg) {
        gridBg.style.background = `
            linear-gradient(90deg, ${theme.gridColors.primary} 1px, transparent 1px),
            linear-gradient(${theme.gridColors.secondary} 1px, transparent 1px)
        `;
    }

    // Update navigation borders
    const nav = document.querySelector('nav');
    if (nav) {
        nav.style.borderBottomColor = theme.borderColor;
    }

    // Update footer borders
    const footer = document.querySelector('footer');
    if (footer) {
        footer.style.borderTopColor = theme.borderColor;
    }

    // Update all elements with border colors
    document.querySelectorAll('.lang-switch, .social-link, .footer-bottom').forEach(el => {
        el.style.borderColor = theme.borderColor;
    });

    // Update button shadows
    document.querySelectorAll('.btn-primary').forEach(btn => {
        btn.style.boxShadow = `0 10px 40px ${theme.shadowColor}`;
        btn.addEventListener('mouseenter', function() {
            this.style.boxShadow = `0 15px 50px ${theme.glowColor}`;
        });
        btn.addEventListener('mouseleave', function() {
            this.style.boxShadow = `0 10px 40px ${theme.shadowColor}`;
        });
    });

    // Store theme preference
    localStorage.setItem('lydian-theme', themeName);

    // Add theme class to body
    document.body.classList.remove('theme-turkey', 'theme-usa');
    document.body.classList.add(`theme-${themeName}`);

    console.log(`${theme.name} theme applied successfully!`);
}

/**
 * Manual theme switcher (for user override)
 */
function switchTheme(themeName) {
    if (themes[themeName]) {
        applyTheme(themeName);
    }
}

/**
 * Initialize theme on page load
 */
function initializeTheme() {
    // Check for stored preference first
    const storedTheme = localStorage.getItem('lydian-theme');
    if (storedTheme && themes[storedTheme]) {
        applyTheme(storedTheme);
        return;
    }

    // Auto-detect based on content
    const detectedCountry = detectCountry();
    applyTheme(detectedCountry);
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTheme);
} else {
    initializeTheme();
}

// Expose functions globally for manual control
window.LydianTheme = {
    switch: switchTheme,
    current: () => localStorage.getItem('lydian-theme') || 'turkey',
    themes: Object.keys(themes)
};

// Add theme toggle button (optional - can be enabled if needed)
function addThemeToggle() {
    const toggleBtn = document.createElement('button');
    toggleBtn.id = 'theme-toggle';
    toggleBtn.innerHTML = '<i class="fas fa-palette"></i>';
    toggleBtn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: var(--gradient-lydian);
        border: none;
        color: white;
        cursor: pointer;
        z-index: 9999;
        box-shadow: 0 5px 20px var(--lydian-primary);
        transition: all 0.3s;
    `;

    toggleBtn.addEventListener('click', () => {
        const current = window.LydianTheme.current();
        const next = current === 'turkey' ? 'usa' : 'turkey';
        switchTheme(next);
    });

    toggleBtn.addEventListener('mouseenter', () => {
        toggleBtn.style.transform = 'scale(1.1)';
    });

    toggleBtn.addEventListener('mouseleave', () => {
        toggleBtn.style.transform = 'scale(1)';
    });

    document.body.appendChild(toggleBtn);
}

// Uncomment to enable theme toggle button
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', addThemeToggle);
// } else {
//     addThemeToggle();
// }
