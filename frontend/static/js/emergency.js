// Emergency Page JavaScript - Fully Functional & Responsive

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';
const WS_BASE_URL = 'ws://localhost:8000/ws';

// Initialize current time for arrival time field
document.addEventListener('DOMContentLoaded', () => {
    const arrivalTimeInput = document.getElementById('arrivalTime');
    if (arrivalTimeInput) {
        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        arrivalTimeInput.value = now.toISOString().slice(0, 16);
    }
});

// ============================================================================
// TRIAGE FORM HANDLING
// ============================================================================

const triageForm = document.getElementById('triageForm');
const triageResult = document.getElementById('triageResult');
const loadingOverlay = document.getElementById('loadingOverlay');

if (triageForm) {
    triageForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await performTriageAssessment();
    });
}

async function performTriageAssessment() {
    // Show loading overlay
    loadingOverlay.classList.add('active');

    // Collect form data
    const formData = new FormData(triageForm);
    const symptoms = [];
    document.querySelectorAll('input[name="symptoms"]:checked').forEach(checkbox => {
        symptoms.push(checkbox.value);
    });

    const triageRequest = {
        patient_id: formData.get('patientId'),
        chief_complaint: formData.get('chiefComplaint'),
        vital_signs: {
            blood_pressure_systolic: parseInt(formData.get('bloodPressureSystolic')),
            blood_pressure_diastolic: parseInt(formData.get('bloodPressureDiastolic')),
            heart_rate: parseInt(formData.get('heartRate')),
            respiratory_rate: parseInt(formData.get('respiratoryRate')),
            temperature: parseFloat(formData.get('temperature')),
            oxygen_saturation: parseInt(formData.get('oxygenSaturation')),
            glasgow_coma_scale: parseInt(formData.get('glasgowComaScale')),
            pain_scale: parseInt(formData.get('painScale'))
        },
        symptoms: symptoms,
        onset_time: formData.get('arrivalTime'),
        medical_history: formData.get('medicalHistory') || null
    };

    try {
        // Simulate API call (replace with actual API endpoint when ready)
        await simulateTriageAPI(triageRequest);

        // In production, use actual API:
        // const response = await fetch(`${API_BASE_URL}/emergency/triage`, {
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json',
        //         'Authorization': `Bearer ${localStorage.getItem('token')}`
        //     },
        //     body: JSON.stringify(triageRequest)
        // });
        // const result = await response.json();
        // displayTriageResult(result);

    } catch (error) {
        console.error('Triage assessment error:', error);
        showNotification('Triage assessment failed. Please try again.', 'error');
    } finally {
        loadingOverlay.classList.remove('active');
    }
}

// Simulate triage API response
async function simulateTriageAPI(request) {
    return new Promise((resolve) => {
        setTimeout(() => {
            // Calculate ESI level based on vital signs and symptoms
            let esiLevel = calculateESILevel(request);

            const result = {
                patient_id: request.patient_id,
                esi_level: esiLevel,
                priority: getESIPriority(esiLevel),
                target_time_minutes: getTargetTime(esiLevel),
                confidence_score: 0.92,
                abcde_assessment: generateABCDE(request.vital_signs, request.symptoms),
                immediate_actions: generateImmediateActions(esiLevel, request.symptoms),
                activated_protocols: generateProtocols(esiLevel, request.symptoms, request.chief_complaint),
                timestamp: new Date().toISOString()
            };

            displayTriageResult(result);
            resolve(result);
        }, 2000); // 2 second delay to simulate API
    });
}

// Calculate ESI Level based on vital signs and symptoms
function calculateESILevel(request) {
    const vs = request.vital_signs;
    const symptoms = request.symptoms;

    // ESI Level 1 - Immediate life-threatening
    if (vs.heart_rate < 40 || vs.heart_rate > 150 ||
        vs.respiratory_rate < 8 || vs.respiratory_rate > 35 ||
        vs.oxygen_saturation < 88 ||
        vs.glasgow_coma_scale < 10 ||
        symptoms.includes('severe_bleeding') ||
        symptoms.includes('altered_consciousness')) {
        return 1;
    }

    // ESI Level 2 - Emergent (high risk or severe pain/distress)
    if (vs.heart_rate > 120 || vs.heart_rate < 50 ||
        vs.blood_pressure_systolic > 180 || vs.blood_pressure_systolic < 90 ||
        vs.oxygen_saturation < 92 ||
        vs.pain_scale >= 8 ||
        symptoms.includes('chest_pain') ||
        symptoms.includes('stroke_symptoms') ||
        symptoms.includes('difficulty_breathing') ||
        symptoms.includes('seizure')) {
        return 2;
    }

    // ESI Level 3 - Urgent (may require multiple resources)
    if (vs.heart_rate > 100 ||
        vs.temperature > 38.5 || vs.temperature < 36.0 ||
        vs.pain_scale >= 5 ||
        symptoms.includes('severe_pain') ||
        symptoms.includes('trauma')) {
        return 3;
    }

    // ESI Level 4 - Less urgent (1 resource needed)
    if (symptoms.length > 0 && symptoms.length <= 2) {
        return 4;
    }

    // ESI Level 5 - Non-urgent (no resources needed)
    return 5;
}

function getESIPriority(level) {
    const priorities = {
        1: 'CRITICAL - Resuscitation',
        2: 'EMERGENT - High Priority',
        3: 'URGENT - Moderate Priority',
        4: 'LESS URGENT - Low Priority',
        5: 'NON-URGENT - Minimal Priority'
    };
    return priorities[level];
}

function getTargetTime(level) {
    const times = {
        1: 0,
        2: 10,
        3: 30,
        4: 60,
        5: 120
    };
    return times[level];
}

function generateABCDE(vitalSigns, symptoms) {
    return {
        airway: vitalSigns.glasgow_coma_scale >= 13 ?
            'Patent airway, able to speak' :
            'COMPROMISED - Consider airway protection',
        breathing: vitalSigns.respiratory_rate >= 12 && vitalSigns.respiratory_rate <= 20 && vitalSigns.oxygen_saturation >= 95 ?
            `Normal respiratory rate (${vitalSigns.respiratory_rate}/min), O2 sat ${vitalSigns.oxygen_saturation}%` :
            `ABNORMAL - RR: ${vitalSigns.respiratory_rate}/min, O2 sat: ${vitalSigns.oxygen_saturation}%`,
        circulation: vitalSigns.heart_rate >= 60 && vitalSigns.heart_rate <= 100 && vitalSigns.blood_pressure_systolic >= 100 ?
            `Stable - HR: ${vitalSigns.heart_rate} bpm, BP: ${vitalSigns.blood_pressure_systolic}/${vitalSigns.blood_pressure_diastolic} mmHg` :
            `UNSTABLE - HR: ${vitalSigns.heart_rate} bpm, BP: ${vitalSigns.blood_pressure_systolic}/${vitalSigns.blood_pressure_diastolic} mmHg`,
        disability: vitalSigns.glasgow_coma_scale >= 14 ?
            `Alert and oriented, GCS ${vitalSigns.glasgow_coma_scale}` :
            `ALTERED - GCS ${vitalSigns.glasgow_coma_scale}, neurological assessment needed`,
        exposure: vitalSigns.temperature >= 36.0 && vitalSigns.temperature <= 37.5 ?
            `Normothermic (${vitalSigns.temperature}°C), no obvious trauma` :
            `Temperature ${vitalSigns.temperature}°C - Monitor for fever/hypothermia`
    };
}

function generateImmediateActions(esiLevel, symptoms) {
    const actions = [];

    if (esiLevel === 1) {
        actions.push('Activate rapid response team');
        actions.push('Establish IV access (2 large-bore IVs)');
        actions.push('Continuous cardiac monitoring');
        actions.push('Prepare for resuscitation');
        actions.push('Notify attending physician immediately');
    } else if (esiLevel === 2) {
        actions.push('Place on continuous monitoring');
        actions.push('Establish IV access');
        actions.push('ECG within 10 minutes');
        actions.push('Stat laboratory tests (CBC, BMP, Troponin)');
        if (symptoms.includes('chest_pain')) {
            actions.push('Aspirin 325mg PO');
        }
        if (symptoms.includes('stroke_symptoms')) {
            actions.push('Stat non-contrast CT head');
            actions.push('Activate stroke protocol');
        }
    } else if (esiLevel === 3) {
        actions.push('Vital signs monitoring every 30 minutes');
        actions.push('Establish IV access');
        actions.push('Pain management as needed');
        actions.push('Order appropriate imaging/labs');
    } else {
        actions.push('Vital signs on arrival and per protocol');
        actions.push('Physician evaluation within target time');
    }

    return actions;
}

function generateProtocols(esiLevel, symptoms, chiefComplaint) {
    const protocols = [];

    if (symptoms.includes('chest_pain')) {
        protocols.push({
            name: 'STEMI Protocol',
            description: 'Acute coronary syndrome evaluation with 12-lead ECG and cardiac markers'
        });
    }

    if (symptoms.includes('stroke_symptoms')) {
        protocols.push({
            name: 'Stroke Alert',
            description: 'Rapid neurological assessment, CT imaging, and neurology consultation'
        });
    }

    if (symptoms.includes('difficulty_breathing')) {
        protocols.push({
            name: 'Respiratory Distress',
            description: 'Supplemental oxygen, bronchodilators, and chest imaging as indicated'
        });
    }

    if (symptoms.includes('seizure')) {
        protocols.push({
            name: 'Seizure Protocol',
            description: 'Airway protection, anticonvulsant therapy, and neurological evaluation'
        });
    }

    if (symptoms.includes('trauma')) {
        protocols.push({
            name: 'Trauma Activation',
            description: 'ATLS protocol with focused assessment and imaging'
        });
    }

    if (symptoms.includes('severe_bleeding')) {
        protocols.push({
            name: 'Hemorrhage Control',
            description: 'Massive transfusion protocol, surgical consultation'
        });
    }

    if (esiLevel === 1 && protocols.length === 0) {
        protocols.push({
            name: 'ACLS Protocol',
            description: 'Advanced cardiac life support for critical patient'
        });
    }

    return protocols;
}

// Display triage result
function displayTriageResult(result) {
    // Hide form, show result
    document.querySelector('.triage-form-container').style.display = 'none';
    triageResult.style.display = 'block';

    // ESI Badge
    const esiBadge = document.getElementById('esiBadge');
    esiBadge.className = `esi-badge level-${result.esi_level}`;
    document.getElementById('esiLevel').textContent = result.esi_level;
    document.getElementById('esiLabel').textContent = result.priority.split(' - ')[1];

    // Priority & Timing
    document.getElementById('priorityText').textContent = result.priority;
    document.getElementById('targetTime').textContent =
        result.target_time_minutes === 0 ? 'Immediate' : `${result.target_time_minutes} minutes`;
    document.getElementById('confidenceScore').textContent =
        `${(result.confidence_score * 100).toFixed(0)}%`;

    // ABCDE Assessment
    document.getElementById('airwayStatus').textContent = result.abcde_assessment.airway;
    document.getElementById('breathingStatus').textContent = result.abcde_assessment.breathing;
    document.getElementById('circulationStatus').textContent = result.abcde_assessment.circulation;
    document.getElementById('disabilityStatus').textContent = result.abcde_assessment.disability;
    document.getElementById('exposureStatus').textContent = result.abcde_assessment.exposure;

    // Immediate Actions
    const actionsList = document.getElementById('immediateActions');
    actionsList.innerHTML = '';
    result.immediate_actions.forEach(action => {
        const li = document.createElement('li');
        li.textContent = action;
        actionsList.appendChild(li);
    });

    // Activated Protocols
    const protocolsGrid = document.getElementById('activatedProtocols');
    protocolsGrid.innerHTML = '';
    result.activated_protocols.forEach(protocol => {
        const div = document.createElement('div');
        div.className = 'protocol-item';
        div.innerHTML = `
            <h4>${protocol.name}</h4>
            <p>${protocol.description}</p>
        `;
        protocolsGrid.appendChild(div);
    });

    // Show notification
    showNotification(
        `Triage completed: ESI Level ${result.esi_level} - ${result.priority}`,
        result.esi_level <= 2 ? 'error' : result.esi_level === 3 ? 'warning' : 'success'
    );

    // Scroll to result
    triageResult.scrollIntoView({ behavior: 'smooth' });
}

// ============================================================================
// FORM CONTROLS
// ============================================================================

// Clear Form Button
const clearFormBtn = document.getElementById('clearForm');
if (clearFormBtn) {
    clearFormBtn.addEventListener('click', () => {
        triageForm.reset();
        // Reset arrival time to current time
        const arrivalTimeInput = document.getElementById('arrivalTime');
        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        arrivalTimeInput.value = now.toISOString().slice(0, 16);
        showNotification('Form cleared', 'info');
    });
}

// New Triage Button
const newTriageBtn = document.getElementById('newTriage');
if (newTriageBtn) {
    newTriageBtn.addEventListener('click', () => {
        triageResult.style.display = 'none';
        document.querySelector('.triage-form-container').style.display = 'block';
        triageForm.reset();
        // Reset arrival time
        const arrivalTimeInput = document.getElementById('arrivalTime');
        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        arrivalTimeInput.value = now.toISOString().slice(0, 16);
        // Scroll to form
        document.querySelector('.triage-form-container').scrollIntoView({ behavior: 'smooth' });
    });
}

// ============================================================================
// REAL-TIME UPDATES (WebSocket)
// ============================================================================

// WebSocket connection for emergency department updates
/*
const emergencyWS = new WebSocket(`${WS_BASE_URL}/emergency`);

emergencyWS.onopen = () => {
    console.log('Emergency WebSocket connected');
};

emergencyWS.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Emergency update:', data);

    switch(data.type) {
        case 'new_patient':
            handleNewPatient(data.data);
            break;
        case 'esi_update':
            handleESIUpdate(data.data);
            break;
        case 'protocol_activation':
            handleProtocolActivation(data.data);
            break;
    }
};

emergencyWS.onerror = (error) => {
    console.error('Emergency WebSocket error:', error);
};

emergencyWS.onclose = () => {
    console.log('Emergency WebSocket disconnected');
};
*/

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
        max-width: 400px;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

// ============================================================================
// VITAL SIGNS VALIDATION
// ============================================================================

// Real-time validation for vital signs
const vitalSignInputs = {
    bloodPressureSystolic: { min: 60, max: 250, warn: { low: 90, high: 180 } },
    bloodPressureDiastolic: { min: 30, max: 150, warn: { low: 60, high: 100 } },
    heartRate: { min: 30, max: 200, warn: { low: 60, high: 100 } },
    respiratoryRate: { min: 6, max: 50, warn: { low: 12, high: 20 } },
    temperature: { min: 32, max: 42, warn: { low: 36, high: 37.5 } },
    oxygenSaturation: { min: 70, max: 100, warn: { low: 95, high: 100 } },
    glasgowComaScale: { min: 3, max: 15, warn: { low: 14, high: 15 } },
    painScale: { min: 0, max: 10, warn: { low: 0, high: 3 } }
};

Object.keys(vitalSignInputs).forEach(inputId => {
    const input = document.getElementById(inputId);
    if (input) {
        input.addEventListener('blur', function() {
            const value = parseFloat(this.value);
            const limits = vitalSignInputs[inputId];

            if (value < limits.min || value > limits.max) {
                this.style.borderColor = '#ff4757';
                showNotification(`${inputId}: Value out of acceptable range`, 'error');
            } else if (value < limits.warn.low || value > limits.warn.high) {
                this.style.borderColor = '#ffa500';
            } else {
                this.style.borderColor = '#00d4aa';
            }
        });
    }
});

// ============================================================================
// EMERGENCY CASE ACTIONS
// ============================================================================

document.querySelectorAll('.btn-action-critical, .btn-action-high, .btn-action-medium').forEach(btn => {
    btn.addEventListener('click', function() {
        const caseCard = this.closest('.case-card');
        const caseId = caseCard.querySelector('.case-id').textContent;
        const action = this.textContent.trim();

        showNotification(`Initiating: ${action} for ${caseId}`, 'info');

        // In production, trigger actual protocol activation
        // activateProtocol(caseId, action);
    });
});

// ============================================================================
// AUTO-REFRESH STATS
// ============================================================================

function updateEmergencyStats() {
    // Simulate real-time stat updates
    const statNumbers = document.querySelectorAll('.emergency-stats .stat-number');
    statNumbers.forEach(stat => {
        const currentValue = parseInt(stat.textContent);
        const change = Math.floor(Math.random() * 3) - 1; // -1, 0, or 1
        const newValue = Math.max(0, currentValue + change);
        stat.textContent = newValue;
    });
}

// Update stats every 10 seconds
setInterval(updateEmergencyStats, 10000);

console.log('Emergency page loaded successfully');
