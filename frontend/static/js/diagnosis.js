// Diagnosis Page JavaScript - AI-Powered Diagnostic Analysis

const API_BASE_URL = 'http://localhost:8000/api/v1';
let uploadedFiles = [];

// ============================================================================
// IMAGE UPLOAD HANDLING
// ============================================================================

const uploadArea = document.getElementById('uploadArea');
const imageUpload = document.getElementById('imageUpload');
const browseBtn = document.getElementById('browseBtn');
const uploadedImagesContainer = document.getElementById('uploadedImages');

// Click to browse
if (browseBtn) {
    browseBtn.addEventListener('click', () => imageUpload.click());
}

// File input change
if (imageUpload) {
    imageUpload.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });
}

// Drag & Drop
if (uploadArea) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.add('drag-over');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.remove('drag-over');
        }, false);
    });

    uploadArea.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        handleFiles(files);
    }, false);
}

function handleFiles(files) {
    [...files].forEach(file => {
        if (file.type.startsWith('image/') || file.name.endsWith('.dcm')) {
            uploadedFiles.push(file);
            displayUploadedImage(file);
        } else {
            showNotification('Please upload image files only', 'error');
        }
    });
}

function displayUploadedImage(file) {
    const reader = new FileReader();

    reader.onload = (e) => {
        const div = document.createElement('div');
        div.className = 'uploaded-image-item';
        div.innerHTML = `
            <img src="${e.target.result}" alt="${file.name}">
            <button class="image-remove-btn" onclick="removeImage('${file.name}')">
                <i class="fas fa-times"></i>
            </button>
            <div class="image-info">${file.name}</div>
        `;
        uploadedImagesContainer.appendChild(div);
    };

    reader.readAsDataURL(file);
}

function removeImage(fileName) {
    uploadedFiles = uploadedFiles.filter(f => f.name !== fileName);
    const items = uploadedImagesContainer.querySelectorAll('.uploaded-image-item');
    items.forEach(item => {
        if (item.querySelector('.image-info').textContent === fileName) {
            item.remove();
        }
    });
}

// ============================================================================
// DIAGNOSIS FORM HANDLING
// ============================================================================

const diagnosisForm = document.getElementById('diagnosisForm');
const diagnosisResult = document.getElementById('diagnosisResult');
const loadingOverlay = document.getElementById('loadingOverlay');

if (diagnosisForm) {
    diagnosisForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await performDiagnosisAnalysis();
    });
}

async function performDiagnosisAnalysis() {
    loadingOverlay.classList.add('active');

    const formData = new FormData(diagnosisForm);

    const diagnosisRequest = {
        patient_id: formData.get('patientId'),
        imaging_data: {
            modality: formData.get('imagingType') || 'x_ray',
            body_region: formData.get('bodyRegion') || 'chest',
            acquisition_date: formData.get('imagingDate') || new Date().toISOString().split('T')[0],
            image_count: uploadedFiles.length
        },
        clinical_data: {
            age: parseInt(formData.get('patientAge')) || 0,
            gender: formData.get('patientGender') || 'unknown',
            presenting_symptoms: formData.get('clinicalSymptoms'),
            medical_history: formData.get('medicalHistory') || null
        },
        lab_results: collectLabResults(formData)
    };

    try {
        await simulateDiagnosisAPI(diagnosisRequest);

        // In production:
        // const response = await fetch(`${API_BASE_URL}/diagnosis/analyze`, {
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json',
        //         'Authorization': `Bearer ${localStorage.getItem('token')}`
        //     },
        //     body: JSON.stringify(diagnosisRequest)
        // });
        // const result = await response.json();
        // displayDiagnosisResult(result);

    } catch (error) {
        console.error('Diagnosis error:', error);
        showNotification('Diagnosis analysis failed', 'error');
    } finally {
        loadingOverlay.classList.remove('active');
    }
}

function collectLabResults(formData) {
    const labs = {};
    const labFields = ['wbc', 'hemoglobin', 'platelets', 'glucose', 'creatinine', 'troponin'];

    labFields.forEach(field => {
        const value = formData.get(field);
        if (value) {
            labs[field] = parseFloat(value);
        }
    });

    return Object.keys(labs).length > 0 ? labs : null;
}

// Simulate diagnosis API
async function simulateDiagnosisAPI(request) {
    return new Promise((resolve) => {
        setTimeout(() => {
            const result = generateDiagnosisResult(request);
            displayDiagnosisResult(result);
            resolve(result);
        }, 3000);
    });
}

function generateDiagnosisResult(request) {
    const symptoms = request.clinical_data.presenting_symptoms.toLowerCase();

    let primaryDiagnosis, icdCode, differentials;

    // Simple keyword-based diagnosis simulation
    if (symptoms.includes('chest pain') || symptoms.includes('cardiac')) {
        primaryDiagnosis = {
            name: 'Acute Myocardial Infarction',
            icd_code: 'I21.9',
            description: 'ST-elevation myocardial infarction (STEMI) based on clinical presentation and elevated cardiac markers.',
            severity: 'Critical',
            confidence: 0.947
        };
        differentials = [
            { name: 'Unstable Angina', icd_code: 'I20.0', confidence: 0.823 },
            { name: 'Pulmonary Embolism', icd_code: 'I26.9', confidence: 0.712 },
            { name: 'Aortic Dissection', icd_code: 'I71.00', confidence: 0.645 },
            { name: 'Pericarditis', icd_code: 'I30.9', confidence: 0.589 }
        ];
    } else if (symptoms.includes('cough') || symptoms.includes('pneumonia') || symptoms.includes('respiratory')) {
        primaryDiagnosis = {
            name: 'Community-Acquired Pneumonia',
            icd_code: 'J18.9',
            description: 'Bacterial pneumonia with consolidation visible on chest imaging and elevated inflammatory markers.',
            severity: 'Moderate',
            confidence: 0.923
        };
        differentials = [
            { name: 'Bronchitis', icd_code: 'J20.9', confidence: 0.785 },
            { name: 'COVID-19 Pneumonia', icd_code: 'U07.1', confidence: 0.734 },
            { name: 'Pulmonary Edema', icd_code: 'J81.0', confidence: 0.656 },
            { name: 'Tuberculosis', icd_code: 'A15.9', confidence: 0.512 }
        ];
    } else if (symptoms.includes('stroke') || symptoms.includes('neurological') || symptoms.includes('weakness')) {
        primaryDiagnosis = {
            name: 'Ischemic Stroke',
            icd_code: 'I63.9',
            description: 'Acute ischemic stroke affecting middle cerebral artery territory with neurological deficits.',
            severity: 'Critical',
            confidence: 0.962
        };
        differentials = [
            { name: 'Hemorrhagic Stroke', icd_code: 'I61.9', confidence: 0.712 },
            { name: 'Transient Ischemic Attack', icd_code: 'G45.9', confidence: 0.698 },
            { name: 'Brain Tumor', icd_code: 'C71.9', confidence: 0.534 },
            { name: 'Multiple Sclerosis', icd_code: 'G35', confidence: 0.445 }
        ];
    } else {
        primaryDiagnosis = {
            name: 'Undifferentiated Diagnosis',
            icd_code: 'R69',
            description: 'Further clinical evaluation and diagnostic testing required for definitive diagnosis.',
            severity: 'Moderate',
            confidence: 0.678
        };
        differentials = [
            { name: 'Viral Syndrome', icd_code: 'B34.9', confidence: 0.567 },
            { name: 'Gastroenteritis', icd_code: 'K52.9', confidence: 0.523 },
            { name: 'Anxiety Disorder', icd_code: 'F41.9', confidence: 0.489 }
        ];
    }

    return {
        patient_id: request.patient_id,
        confidence_score: primaryDiagnosis.confidence,
        primary_diagnosis: primaryDiagnosis,
        differential_diagnosis: differentials,
        imaging_findings: request.imaging_data.image_count > 0 ? [
            'Bilateral infiltrates present',
            'No pneumothorax identified',
            'Heart size within normal limits',
            'No pleural effusion'
        ] : null,
        clinical_reasoning: `Based on the clinical presentation of ${request.clinical_data.presenting_symptoms.toLowerCase()}, combined with available imaging and laboratory data, the most likely diagnosis is ${primaryDiagnosis.name}. The patient's age (${request.clinical_data.age}), gender (${request.clinical_data.gender}), and medical history were considered in this assessment.`,
        recommendations: {
            tests: ['Complete Blood Count', 'Comprehensive Metabolic Panel', 'Chest X-Ray PA/Lateral'],
            specialists: ['Cardiology', 'Internal Medicine'],
            followup: ['24-hour monitoring', 'Repeat imaging in 48 hours', 'Medication compliance check']
        },
        risk_stratification: {
            mortality: 'Moderate',
            complications: 'Moderate',
            urgency: 'High'
        },
        timestamp: new Date().toISOString()
    };
}

function displayDiagnosisResult(result) {
    document.querySelector('.diagnosis-form-container').style.display = 'none';
    diagnosisResult.style.display = 'block';

    // Confidence Score
    const confidence = (result.confidence_score * 100).toFixed(1);
    document.getElementById('confidenceValue').textContent = `${confidence}%`;
    document.getElementById('confidenceFill').style.width = `${confidence}%`;

    // Primary Diagnosis
    document.getElementById('primaryDiagnosisName').textContent = result.primary_diagnosis.name;
    document.getElementById('primaryICD').textContent = result.primary_diagnosis.icd_code;
    document.getElementById('primaryDescription').textContent = result.primary_diagnosis.description;
    document.getElementById('primarySeverity').textContent = `Severity: ${result.primary_diagnosis.severity}`;
    document.getElementById('primaryConfidence').textContent = `${(result.primary_diagnosis.confidence * 100).toFixed(1)}% confidence`;

    // Differential Diagnosis
    const diffList = document.getElementById('differentialList');
    diffList.innerHTML = '';
    result.differential_diagnosis.forEach((diff, index) => {
        const div = document.createElement('div');
        div.className = 'differential-item';
        div.innerHTML = `
            <div class="differential-info">
                <h5>${index + 1}. ${diff.name}</h5>
                <p>ICD-10: ${diff.icd_code}</p>
            </div>
            <div class="differential-confidence">${(diff.confidence * 100).toFixed(1)}%</div>
        `;
        diffList.appendChild(div);
    });

    // Imaging Findings
    if (result.imaging_findings && uploadedFiles.length > 0) {
        const imagingAnalysis = document.getElementById('imagingAnalysis');
        imagingAnalysis.style.display = 'block';

        const preview = document.getElementById('analyzedImagePreview');
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.innerHTML = `<img src="${e.target.result}" alt="Analyzed Image">`;
        };
        reader.readAsDataURL(uploadedFiles[0]);

        const findings = document.getElementById('imagingFindings');
        findings.innerHTML = '<h4>Key Findings</h4><ul></ul>';
        const ul = findings.querySelector('ul');
        result.imaging_findings.forEach(finding => {
            const li = document.createElement('li');
            li.textContent = finding;
            ul.appendChild(li);
        });
    }

    // Clinical Reasoning
    document.getElementById('reasoningContent').innerHTML = `<p>${result.clinical_reasoning}</p>`;

    // Recommendations
    const testsUl = document.getElementById('recommendedTests');
    testsUl.innerHTML = '';
    result.recommendations.tests.forEach(test => {
        const li = document.createElement('li');
        li.textContent = test;
        testsUl.appendChild(li);
    });

    const specialistsUl = document.getElementById('specialistReferrals');
    specialistsUl.innerHTML = '';
    result.recommendations.specialists.forEach(spec => {
        const li = document.createElement('li');
        li.textContent = spec;
        specialistsUl.appendChild(li);
    });

    const followupUl = document.getElementById('followupActions');
    followupUl.innerHTML = '';
    result.recommendations.followup.forEach(action => {
        const li = document.createElement('li');
        li.textContent = action;
        followupUl.appendChild(li);
    });

    // Risk Stratification
    document.getElementById('mortalityRisk').textContent = result.risk_stratification.mortality;
    document.getElementById('mortalityRisk').className = `risk-value ${result.risk_stratification.mortality.toLowerCase()}`;
    document.getElementById('complicationRisk').textContent = result.risk_stratification.complications;
    document.getElementById('complicationRisk').className = `risk-value ${result.risk_stratification.complications.toLowerCase()}`;
    document.getElementById('urgencyLevel').textContent = result.risk_stratification.urgency;
    document.getElementById('urgencyLevel').className = `risk-value ${result.risk_stratification.urgency.toLowerCase()}`;

    showNotification('AI diagnosis completed successfully', 'success');
    diagnosisResult.scrollIntoView({ behavior: 'smooth' });
}

// ============================================================================
// FORM CONTROLS
// ============================================================================

document.getElementById('clearDiagnosisForm')?.addEventListener('click', () => {
    diagnosisForm.reset();
    uploadedFiles = [];
    uploadedImagesContainer.innerHTML = '';
    showNotification('Form cleared', 'info');
});

document.getElementById('newDiagnosis')?.addEventListener('click', () => {
    diagnosisResult.style.display = 'none';
    document.querySelector('.diagnosis-form-container').style.display = 'block';
    diagnosisForm.reset();
    uploadedFiles = [];
    uploadedImagesContainer.innerHTML = '';
    document.querySelector('.diagnosis-form-container').scrollIntoView({ behavior: 'smooth' });
});

document.getElementById('exportPDF')?.addEventListener('click', () => {
    showNotification('Exporting diagnosis report to PDF...', 'info');
    // Implement PDF export functionality
});

// ============================================================================
// TABLE ACTIONS
// ============================================================================

document.querySelectorAll('.btn-table-action').forEach(btn => {
    btn.addEventListener('click', function() {
        const row = this.closest('tr');
        const patientId = row.querySelector('strong').textContent;
        const icon = this.querySelector('i').classList.contains('fa-eye') ? 'View' : 'Download';
        showNotification(`${icon} diagnosis for ${patientId}`, 'info');
    });
});

// ============================================================================
// NOTIFICATION SYSTEM
// ============================================================================

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#00d4aa' : type === 'error' ? '#ff4757' : type === 'warning' ? '#ffa500' : '#3498db'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10001;
        display: flex;
        align-items: center;
        gap: 10px;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

console.log('Diagnosis page loaded successfully');
