// i18n System - Lydian Healthcare AI
// Comprehensive multilingual support with localStorage persistence

const translations = {
    tr: {
        // Navigation
        'Dashboard': 'Dashboard',
        'Emergency': 'Acil Servis',
        'Diagnosis': 'Tanı Asistanı',
        'Treatment': 'Tedavi Planlama',
        'Pharmacy': 'Eczane',
        'Patients': 'Hastalar',
        'Logout': 'Çıkış',
        
        // Page Titles
        'Dashboard | Lydian Healthcare AI': 'Dashboard | Lydian Sağlık AI',
        'Emergency | Lydian Healthcare AI': 'Acil Servis | Lydian Sağlık AI',
        'Diagnosis | Lydian Healthcare AI': 'Tanı | Lydian Sağlık AI',
        'Treatment Planning | Lydian Healthcare AI': 'Tedavi Planlama | Lydian Sağlık AI',
        'Pharmacy | Lydian Healthcare AI': 'Eczane | Lydian Sağlık AI',
        'Patients | Lydian Healthcare AI': 'Hastalar | Lydian Sağlık AI',
        
        // Common
        'Search': 'Ara',
        'Filter': 'Filtrele',
        'View': 'Görüntüle',
        'Edit': 'Düzenle',
        'Delete': 'Sil',
        'Save': 'Kaydet',
        'Cancel': 'İptal',
        'Close': 'Kapat',
        'Submit': 'Gönder',
        'Actions': 'İşlemler',
        'Status': 'Durum',
        'Date': 'Tarih',
        'Time': 'Saat',
        'Active': 'Aktif',
        'Inactive': 'Pasif',
        'Critical': 'Kritik',
        'Discharged': 'Taburcu',
        
        // Development Banner
        'Development Mode - Some features may be in beta': 'Geliştirme Modu - Bazı özellikler beta aşamasında',
        'Development Mode': 'Geliştirme Modu',
        
        // Stats
        'Total Patients': 'Toplam Hastalar',
        'Active Cases': 'Aktif Vakalar',
        'Critical Patients': 'Kritik Hastalar',
        'Admitted Patients': 'Yatan Hastalar',
        'Today': 'Bugün',
        'This Week': 'Bu Hafta',
        'This Month': 'Bu Ay',
        
        // Emergency
        'ESI Triage': 'ESI Triyaj',
        'Vital Signs': 'Vital Bulgular',
        'Chief Complaint': 'Ana Şikayet',
        'Patient ID': 'Hasta ID',
        'Perform Triage': 'Triyaj Yap',
        'Emergency Cases': 'Acil Vakalar',
        
        // Diagnosis
        'AI Diagnosis': 'AI Tanı',
        'Upload Image': 'Görüntü Yükle',
        'Analyze': 'Analiz Et',
        'Diagnosis Result': 'Tanı Sonucu',
        'Confidence': 'Güven Skoru',
        'Recommendations': 'Öneriler',
        
        // Treatment
        'Treatment Plan': 'Tedavi Planı',
        'Medications': 'İlaçlar',
        'Dosage': 'Doz',
        'Duration': 'Süre',
        'Monitoring': 'İzleme',
        
        // Pharmacy
        'Prescription': 'Reçete',
        'Verify': 'Doğrula',
        'Drug Interactions': 'İlaç Etkileşimleri',
        'Safety Checks': 'Güvenlik Kontrolleri',
        
        // Patients
        'Patient List': 'Hasta Listesi',
        'Patient Records': 'Hasta Kayıtları',
        'Medical History': 'Tıbbi Geçmiş',
        'Admission Date': 'Kabul Tarihi',
        
        // Placeholders
        'Search patients by ID, name, diagnosis...': 'Hasta ID, isim veya tanıya göre ara...',
        'Enter patient ID': 'Hasta ID girin',
        'Enter chief complaint': 'Ana şikayeti girin',
        'Select date': 'Tarih seçin'
    },
    en: {
        // Navigation
        'Dashboard': 'Dashboard',
        'Emergency': 'Emergency',
        'Diagnosis': 'Diagnosis',
        'Treatment': 'Treatment',
        'Pharmacy': 'Pharmacy',
        'Patients': 'Patients',
        'Logout': 'Logout',
        
        // Page Titles
        'Dashboard | Lydian Healthcare AI': 'Dashboard | Lydian Healthcare AI',
        'Emergency | Lydian Healthcare AI': 'Emergency | Lydian Healthcare AI',
        'Diagnosis | Lydian Healthcare AI': 'Diagnosis | Lydian Healthcare AI',
        'Treatment Planning | Lydian Healthcare AI': 'Treatment Planning | Lydian Healthcare AI',
        'Pharmacy | Lydian Healthcare AI': 'Pharmacy | Lydian Healthcare AI',
        'Patients | Lydian Healthcare AI': 'Patients | Lydian Healthcare AI',
        
        // Common
        'Search': 'Search',
        'Filter': 'Filter',
        'View': 'View',
        'Edit': 'Edit',
        'Delete': 'Delete',
        'Save': 'Save',
        'Cancel': 'Cancel',
        'Close': 'Close',
        'Submit': 'Submit',
        'Actions': 'Actions',
        'Status': 'Status',
        'Date': 'Date',
        'Time': 'Time',
        'Active': 'Active',
        'Inactive': 'Inactive',
        'Critical': 'Critical',
        'Discharged': 'Discharged',
        
        // Development Banner
        'Development Mode - Some features may be in beta': 'Development Mode - Some features may be in beta',
        'Development Mode': 'Development Mode',
        
        // Stats
        'Total Patients': 'Total Patients',
        'Active Cases': 'Active Cases',
        'Critical Patients': 'Critical Patients',
        'Admitted Patients': 'Admitted Patients',
        'Today': 'Today',
        'This Week': 'This Week',
        'This Month': 'This Month',
        
        // Emergency
        'ESI Triage': 'ESI Triage',
        'Vital Signs': 'Vital Signs',
        'Chief Complaint': 'Chief Complaint',
        'Patient ID': 'Patient ID',
        'Perform Triage': 'Perform Triage',
        'Emergency Cases': 'Emergency Cases',
        
        // Diagnosis
        'AI Diagnosis': 'AI Diagnosis',
        'Upload Image': 'Upload Image',
        'Analyze': 'Analyze',
        'Diagnosis Result': 'Diagnosis Result',
        'Confidence': 'Confidence',
        'Recommendations': 'Recommendations',
        
        // Treatment
        'Treatment Plan': 'Treatment Plan',
        'Medications': 'Medications',
        'Dosage': 'Dosage',
        'Duration': 'Duration',
        'Monitoring': 'Monitoring',
        
        // Pharmacy
        'Prescription': 'Prescription',
        'Verify': 'Verify',
        'Drug Interactions': 'Drug Interactions',
        'Safety Checks': 'Safety Checks',
        
        // Patients
        'Patient List': 'Patient List',
        'Patient Records': 'Patient Records',
        'Medical History': 'Medical History',
        'Admission Date': 'Admission Date',
        
        // Placeholders
        'Search patients by ID, name, diagnosis...': 'Search patients by ID, name, diagnosis...',
        'Enter patient ID': 'Enter patient ID',
        'Enter chief complaint': 'Enter chief complaint',
        'Select date': 'Select date'
    }
};

// Get current language from localStorage or default to Turkish
let currentLang = localStorage.getItem('language') || 'tr';

// Translation function
function t(key) {
    return translations[currentLang][key] || key;
}

// Set language and update all translatable elements
function setLanguage(lang) {
    if (!translations[lang]) {
        console.error(`Language "${lang}" not supported`);
        return;
    }
    
    currentLang = lang;
    localStorage.setItem('language', lang);
    
    // Update HTML lang attribute
    document.documentElement.lang = lang;
    
    // Update page title if it has translation
    const currentTitle = document.title;
    if (translations[lang][currentTitle]) {
        document.title = translations[lang][currentTitle];
    }
    
    // Update all elements with data-tr and data-en attributes
    document.querySelectorAll('[data-tr]').forEach(element => {
        const trText = element.dataset.tr;
        const enText = element.dataset.en;
        
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            // Update placeholder for input/textarea
            element.placeholder = lang === 'tr' ? trText : enText;
        } else {
            // Update text content for other elements
            element.textContent = lang === 'tr' ? trText : enText;
        }
    });
    
    // Update elements with data-i18n attribute (key-based translation)
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.dataset.i18n;
        if (translations[lang][key]) {
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = translations[lang][key];
            } else {
                element.textContent = translations[lang][key];
            }
        }
    });
    
    // Update language button active states
    document.querySelectorAll('.lang-btn').forEach(btn => {
        if (btn.dataset.lang === lang) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Trigger custom event for other scripts to react
    const event = new CustomEvent('languageChanged', { detail: { lang } });
    document.dispatchEvent(event);
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Set initial language
    setLanguage(currentLang);
    
    // Add click event listeners to language buttons
    const langButtons = document.querySelectorAll('.lang-btn');
    langButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const lang = btn.dataset.lang;
            setLanguage(lang);
        });
    });
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { setLanguage, t, currentLang, translations };
}

// Make available globally
window.i18n = { setLanguage, t, currentLang, translations };
