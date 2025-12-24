// Lydian Agent - Advanced Tech Animations

// Floating Particles System
function createParticleField() {
    const particleField = document.createElement('div');
    particleField.className = 'particle-field';
    document.body.appendChild(particleField);

    const colors = ['cyan', 'white', 'red', 'green'];
    const particleCount = 50;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = `particle ${colors[Math.floor(Math.random() * colors.length)]}`;

        // Random positioning
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 15 + 's';
        particle.style.animationDuration = (15 + Math.random() * 10) + 's';

        particleField.appendChild(particle);
    }
}

// Matrix-style Data Rain
function createDataRain() {
    const canvas = document.createElement('canvas');
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.zIndex = '0';
    canvas.style.pointerEvents = 'none';
    canvas.style.opacity = '0.1';
    document.body.insertBefore(canvas, document.body.firstChild);

    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const chars = '01ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const fontSize = 14;
    const columns = canvas.width / fontSize;
    const drops = Array(Math.floor(columns)).fill(1);

    const colors = ['#00ffff', '#ffffff', '#ff0044', '#00ff88'];

    function draw() {
        ctx.fillStyle = 'rgba(10, 14, 26, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        for (let i = 0; i < drops.length; i++) {
            const text = chars[Math.floor(Math.random() * chars.length)];
            const color = colors[Math.floor(Math.random() * colors.length)];

            ctx.fillStyle = color;
            ctx.font = fontSize + 'px JetBrains Mono';
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }

    setInterval(draw, 50);

    // Resize handler
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

// Holographic Card Tilt Effect
function initHoloCards() {
    const cards = document.querySelectorAll('.holo-card');

    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
        });
    });
}

// Quantum Ripple on Click
function initQuantumRipples() {
    const rippleElements = document.querySelectorAll('.quantum-ripple');

    rippleElements.forEach(element => {
        element.addEventListener('click', (e) => {
            const ripple = document.createElement('div');
            ripple.className = 'ripple-effect';

            const rect = element.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            ripple.style.position = 'absolute';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.style.width = '0';
            ripple.style.height = '0';
            ripple.style.borderRadius = '50%';
            ripple.style.border = '2px solid #00ffff';
            ripple.style.pointerEvents = 'none';
            ripple.style.animation = 'rippleExpand 1s ease-out';

            element.appendChild(ripple);

            setTimeout(() => ripple.remove(), 1000);
        });
    });
}

// Tech Corner Brackets Animation
function addTechCorners(selector) {
    const elements = document.querySelectorAll(selector);

    elements.forEach(element => {
        if (!element.classList.contains('tech-corners')) {
            element.classList.add('tech-corners');
        }
    });
}

// Glitch Text Effect
function addGlitchEffect(selector) {
    const elements = document.querySelectorAll(selector);

    elements.forEach(element => {
        const text = element.textContent;
        element.setAttribute('data-text', text);
        element.classList.add('glitch');

        // Random glitch trigger
        setInterval(() => {
            if (Math.random() > 0.95) {
                element.style.animation = 'none';
                setTimeout(() => {
                    element.style.animation = '';
                }, 100);
            }
        }, 2000);
    });
}

// Scanning Line Effect
function initScanLines() {
    const containers = document.querySelectorAll('.scan-line');

    containers.forEach(container => {
        // Add scan effect on hover
        container.addEventListener('mouseenter', () => {
            container.style.animation = 'scanDown 2s ease-in-out';
        });

        container.addEventListener('animationend', () => {
            container.style.animation = '';
        });
    });
}

// Neon Pulse on Scroll
function initScrollEffects() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('neon-glow-cyan');

                // Cycle through colors
                setTimeout(() => {
                    entry.target.classList.remove('neon-glow-cyan');
                    entry.target.classList.add('neon-glow-white');
                }, 1000);

                setTimeout(() => {
                    entry.target.classList.remove('neon-glow-white');
                    entry.target.classList.add('neon-glow-green');
                }, 2000);
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('h1, h2, h3').forEach(heading => {
        observer.observe(heading);
    });
}

// Energy Wave Background
function createEnergyWaves() {
    const wave = document.createElement('div');
    wave.className = 'energy-wave';
    wave.style.position = 'fixed';
    wave.style.top = '0';
    wave.style.left = '0';
    wave.style.width = '100%';
    wave.style.height = '100%';
    wave.style.zIndex = '0';
    wave.style.pointerEvents = 'none';

    document.body.insertBefore(wave, document.body.firstChild);
}

// Initialize All Effects
document.addEventListener('DOMContentLoaded', () => {
    // Create particle field
    createParticleField();

    // Create data rain effect
    createDataRain();

    // Initialize holographic cards
    initHoloCards();

    // Initialize quantum ripples
    initQuantumRipples();

    // Add tech corners to cards
    addTechCorners('.feature-card, .pricing-card, .stat-card');

    // Initialize scan lines
    initScanLines();

    // Initialize scroll effects
    initScrollEffects();

    // Create energy waves
    createEnergyWaves();

    // Add glitch effect to specific titles (optional)
    // addGlitchEffect('.hero-title');

    console.log('🚀 Lydian Agent Tech Animations Initialized');
});

// Button Hover Effect with 2-Tone Gradient
function enhanceButtons() {
    const buttons = document.querySelectorAll('.cta-button, .lang-btn, button');

    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.background = 'linear-gradient(135deg, #00ffff 0%, #ffffff 100%)';
            this.style.boxShadow = '0 0 20px rgba(0, 255, 255, 0.5), 0 0 40px rgba(255, 255, 255, 0.3)';
        });

        button.addEventListener('mouseleave', function() {
            this.style.background = '';
            this.style.boxShadow = '';
        });
    });
}

// Call enhance buttons on load
document.addEventListener('DOMContentLoaded', enhanceButtons);

// Cursor Trail Effect
let cursorTrail = [];
const trailLength = 10;

document.addEventListener('mousemove', (e) => {
    const trail = document.createElement('div');
    trail.className = 'cursor-trail';
    trail.style.position = 'fixed';
    trail.style.left = e.clientX + 'px';
    trail.style.top = e.clientY + 'px';
    trail.style.width = '4px';
    trail.style.height = '4px';
    trail.style.borderRadius = '50%';
    trail.style.background = 'radial-gradient(circle, #00ffff 0%, #ffffff 100%)';
    trail.style.pointerEvents = 'none';
    trail.style.zIndex = '9999';
    trail.style.animation = 'fadeOut 0.5s ease-out';

    document.body.appendChild(trail);
    cursorTrail.push(trail);

    if (cursorTrail.length > trailLength) {
        const old = cursorTrail.shift();
        old.remove();
    }

    setTimeout(() => trail.remove(), 500);
});

// Add fadeOut animation for cursor trail
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        0% { opacity: 1; transform: scale(1); }
        100% { opacity: 0; transform: scale(0); }
    }
`;
document.head.appendChild(style);
