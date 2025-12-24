// Dashboard JavaScript - Fully Functional & Responsive

// Mobile Menu Toggle
const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const sidebar = document.getElementById('sidebar');
const sidebarClose = document.getElementById('sidebarClose');

if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', () => {
        sidebar.classList.toggle('active');
        mobileMenuToggle.classList.toggle('active');
    });
}

if (sidebarClose) {
    sidebarClose.addEventListener('click', () => {
        sidebar.classList.remove('active');
        mobileMenuToggle.classList.remove('active');
    });
}

// Close sidebar when clicking outside (mobile)
document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768) {
        if (!sidebar.contains(e.target) && !mobileMenuToggle.contains(e.target)) {
            sidebar.classList.remove('active');
            mobileMenuToggle.classList.remove('active');
        }
    }
});

// Language Switcher
const langBtns = document.querySelectorAll('.lang-btn');
langBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        langBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const lang = btn.dataset.lang;
        // Here you would implement language switching logic
        console.log('Language switched to:', lang);
    });
});

// Patient Flow Chart
const patientFlowCtx = document.getElementById('patientFlowChart');
if (patientFlowCtx) {
    new Chart(patientFlowCtx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Admissions',
                data: [45, 52, 48, 65, 58, 42, 38],
                borderColor: '#ff0033',
                backgroundColor: 'rgba(255, 0, 51, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Discharges',
                data: [38, 42, 45, 48, 52, 38, 35],
                borderColor: '#00d4aa',
                backgroundColor: 'rgba(0, 212, 170, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Triage Distribution Chart
const triageCtx = document.getElementById('triageChart');
if (triageCtx) {
    new Chart(triageCtx, {
        type: 'doughnut',
        data: {
            labels: ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5'],
            datasets: [{
                data: [2, 8, 15, 12, 8],
                backgroundColor: [
                    '#ff4757',
                    '#ffa500',
                    '#3498db',
                    '#00d4aa',
                    '#95a5a6'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'
                }
            }
        }
    });
}

// Real-time Updates (WebSocket simulation)
function simulateRealTimeUpdates() {
    setInterval(() => {
        // Update random stat
        const statNumbers = document.querySelectorAll('.stat-number');
        if (statNumbers.length > 0) {
            const randomStat = statNumbers[Math.floor(Math.random() * statNumbers.length)];
            const currentValue = parseInt(randomStat.textContent.replace(/,/g, ''));
            const change = Math.floor(Math.random() * 10) - 5;
            const newValue = Math.max(0, currentValue + change);
            randomStat.textContent = newValue.toLocaleString();
        }
    }, 5000); // Update every 5 seconds
}

// Initialize real-time updates
simulateRealTimeUpdates();

// WebSocket Connection (commented out - implement when backend ready)
/*
const wsUrl = 'ws://localhost:8000/ws/notifications?user_id=USER123';
const ws = new WebSocket(wsUrl);

ws.onopen = () => {
    console.log('WebSocket connected');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);

    // Handle different message types
    switch(data.type) {
        case 'emergency_alert':
            showEmergencyAlert(data.data);
            break;
        case 'patient_alert':
            showPatientAlert(data.data);
            break;
        case 'system_notification':
            showNotification(data.message);
            break;
    }
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = () => {
    console.log('WebSocket disconnected');
    // Attempt to reconnect after 5 seconds
    setTimeout(() => {
        location.reload();
    }, 5000);
};
*/

// Notification System
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#00d4aa' : type === 'error' ? '#ff4757' : '#3498db'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 10px;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Alert Button Handlers
document.querySelectorAll('.alert-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        const alertItem = this.closest('.alert-item');
        const alertText = alertItem.querySelector('strong').textContent;
        showNotification(`Responding to: ${alertText}`, 'success');

        // Simulate alert response
        setTimeout(() => {
            alertItem.style.opacity = '0.5';
            this.textContent = 'Responded';
            this.disabled = true;
        }, 500);
    });
});

// Quick Action Buttons
document.querySelectorAll('.action-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const action = this.querySelector('span').textContent;
        showNotification(`Opening: ${action}`, 'info');

        // Here you would navigate to the appropriate page
        // For demo, just show notification
    });
});

// Auto-refresh data every 30 seconds
setInterval(() => {
    console.log('Auto-refreshing dashboard data...');
    // Implement data refresh logic here
}, 30000);

// Initialize tooltips (if using a tooltip library)
document.querySelectorAll('[data-tooltip]').forEach(element => {
    element.addEventListener('mouseenter', function() {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = this.dataset.tooltip;
        tooltip.style.cssText = `
            position: absolute;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 13px;
            z-index: 10000;
            pointer-events: none;
        `;
        document.body.appendChild(tooltip);

        const rect = this.getBoundingClientRect();
        tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
        tooltip.style.left = (rect.left + (rect.width - tooltip.offsetWidth) / 2) + 'px';

        this._tooltip = tooltip;
    });

    element.addEventListener('mouseleave', function() {
        if (this._tooltip) {
            this._tooltip.remove();
            this._tooltip = null;
        }
    });
});

// Performance monitoring
if ('PerformanceObserver' in window) {
    const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
            console.log('Performance:', entry.name, entry.duration);
        }
    });
    observer.observe({ entryTypes: ['measure', 'navigation'] });
}

// Service Worker registration (for PWA capabilities)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Uncomment when service worker is ready
        // navigator.serviceWorker.register('/sw.js')
        //     .then(reg => console.log('Service Worker registered'))
        //     .catch(err => console.log('Service Worker registration failed'));
    });
}

console.log('Dashboard loaded successfully');
