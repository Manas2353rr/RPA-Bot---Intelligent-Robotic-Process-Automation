// RPA Bot Web Interface - Main JavaScript

// Global state
let currentInstructions = [];
let currentSessionId = null;
let logPollingInterval = null;
window.activeBrowserSessions = {}; // Track sessions with open browsers

// DOM Elements
const taskInput = document.getElementById('task-input');
const generateBtn = document.getElementById('generate-btn');
const speechBtn = document.getElementById('speech-btn');
const examplesGrid = document.getElementById('examples-grid');
const instructionsSection = document.getElementById('instructions-section');
const instructionsList = document.getElementById('instructions-list');
const instructionCount = document.getElementById('instruction-count');
const executeBtn = document.getElementById('execute-btn');
const cancelBtn = document.getElementById('cancel-btn');
const logsSection = document.getElementById('logs-section');
const logsContainer = document.getElementById('logs-container');
const executionStatus = document.getElementById('execution-status');
const closeLogsBtn = document.getElementById('close-logs-btn');
const closeBrowserBtn = document.getElementById('close-browser-btn');
const loadingOverlay = document.getElementById('loading-overlay');
const toastContainer = document.getElementById('toast-container');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkSystemStatus();
    loadExamples();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    generateBtn.addEventListener('click', generateInstructions);
    speechBtn.addEventListener('click', useSpeechInput);
    executeBtn.addEventListener('click', executeTask);
    cancelBtn.addEventListener('click', cancelTask);
    closeLogsBtn.addEventListener('click', closeLogs);
    closeBrowserBtn.addEventListener('click', () => {
        if (currentSessionId) {
            closeBrowserForSession(currentSessionId);
            closeBrowserBtn.style.display = 'none';
        }
    });
    
    // Enter key to generate
    taskInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            generateInstructions();
        }
    });
}

// Check system status
async function checkSystemStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Update status indicators
        updateStatusIndicator('ollama-status', data.ollama_connected);
        updateStatusIndicator('selenium-status', data.selenium_available);
        
        // Disable speech button if not available
        if (!data.speech_available) {
            speechBtn.disabled = true;
            speechBtn.title = 'Speech recognition not available';
        }
        
    } catch (error) {
        console.error('Failed to check system status:', error);
        showToast('Failed to connect to server', 'error');
    }
}

// Update status indicator
function updateStatusIndicator(elementId, isActive) {
    const element = document.getElementById(elementId);
    if (isActive) {
        element.classList.add('active');
        element.classList.remove('inactive');
    } else {
        element.classList.add('inactive');
        element.classList.remove('active');
    }
}

// Load examples
async function loadExamples() {
    try {
        const response = await fetch('/api/examples');
        const data = await response.json();
        
        examplesGrid.innerHTML = '';
        data.examples.forEach(example => {
            const card = document.createElement('div');
            card.className = 'example-card';
            card.textContent = example;
            card.addEventListener('click', () => {
                taskInput.value = example;
                taskInput.focus();
            });
            examplesGrid.appendChild(card);
        });
        
    } catch (error) {
        console.error('Failed to load examples:', error);
    }
}

// Generate instructions
async function generateInstructions() {
    const task = taskInput.value.trim();
    
    if (!task) {
        showToast('Please enter a task', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ task })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentInstructions = data.instructions;
            currentSessionId = data.session_id;
            displayInstructions(data.instructions);
            showToast(`Generated ${data.count} instructions`, 'success');
        } else {
            showToast(data.error || 'Failed to generate instructions', 'error');
        }
        
    } catch (error) {
        console.error('Error generating instructions:', error);
        showToast('Failed to generate instructions', 'error');
    } finally {
        showLoading(false);
    }
}

// Display instructions
function displayInstructions(instructions) {
    instructionsList.innerHTML = '';
    instructionCount.textContent = `${instructions.length} steps`;
    
    instructions.forEach((instruction, index) => {
        const item = document.createElement('div');
        item.className = 'instruction-item';
        
        const number = document.createElement('div');
        number.className = 'instruction-number';
        number.textContent = index + 1;
        
        const details = document.createElement('div');
        details.className = 'instruction-details';
        
        const action = document.createElement('div');
        action.className = 'instruction-action';
        action.textContent = getActionDescription(instruction);
        
        const params = document.createElement('div');
        params.className = 'instruction-params';
        params.textContent = getParamsDescription(instruction);
        
        details.appendChild(action);
        details.appendChild(params);
        
        item.appendChild(number);
        item.appendChild(details);
        
        instructionsList.appendChild(item);
    });
    
    instructionsSection.style.display = 'block';
    instructionsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Get action description
function getActionDescription(instruction) {
    const action = instruction.action;
    const params = instruction.params;
    
    const descriptions = {
        'WEB_SEARCH': `Search ${params.site || 'web'} for "${params.query}"`,
        'OPEN_APP': `Open ${params.app}`,
        'OPEN_URL': `Open ${params.url}`,
        'CLICK': 'Click at specified position',
        'TYPE': `Type "${params.text}"`,
        'SCREENSHOT': 'Take screenshot',
        'WAIT': `Wait ${params.seconds} seconds`,
        'COPY': 'Copy to clipboard',
        'PASTE': 'Paste from clipboard',
        'SCROLL': `Scroll ${params.direction}`,
        'PRESS_KEY': `Press ${params.key} key`,
        'HOTKEY': `Press ${params.keys?.join('+')} keys`
    };
    
    return descriptions[action] || action;
}

// Get params description
function getParamsDescription(instruction) {
    const action = instruction.action;
    const params = instruction.params;
    
    if (action === 'WEB_SEARCH') {
        return params.auto_play ? 'Will auto-play first result' : 'Show search results';
    } else if (action === 'OPEN_APP') {
        return `Wait time: ${params.wait_time}s`;
    } else if (action === 'OPEN_URL') {
        return `Wait time: ${params.wait_time}s`;
    } else if (action === 'SCREENSHOT') {
        return `Filename: ${params.filename}`;
    }
    
    return JSON.stringify(params);
}

// Execute task
async function executeTask() {
    if (currentInstructions.length === 0) {
        showToast('No instructions to execute', 'error');
        return;
    }
    
    // Check if there are web actions
    const hasWebActions = currentInstructions.some(inst => 
        inst.action && inst.action.startsWith('WEB_')
    );
    
    // Hide instructions section
    instructionsSection.style.display = 'none';
    
    // Show logs section
    logsSection.style.display = 'block';
    logsContainer.innerHTML = '';
    executionStatus.className = 'execution-status running';
    executionStatus.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Running...</span>';
    logsSection.scrollIntoView({ behavior: 'smooth' });
    
    try {
        const response = await fetch('/api/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                instructions: currentInstructions,
                session_id: currentSessionId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentSessionId = data.session_id;
            
            // Track if this session has a browser open
            if (hasWebActions) {
                window.activeBrowserSessions[currentSessionId] = true;
            }
            
            showToast('Execution started', 'info');
            
            // Start polling for logs
            startLogPolling();
        } else {
            showToast('Failed to start execution', 'error');
            executionStatus.className = 'execution-status failed';
            executionStatus.innerHTML = '<i class="fas fa-times"></i><span>Failed</span>';
        }
        
    } catch (error) {
        console.error('Error executing task:', error);
        showToast('Failed to execute task', 'error');
        executionStatus.className = 'execution-status failed';
        executionStatus.innerHTML = '<i class="fas fa-times"></i><span>Failed</span>';
    }
}

// Start log polling
function startLogPolling() {
    if (logPollingInterval) {
        clearInterval(logPollingInterval);
    }
    
    logPollingInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/logs/${currentSessionId}`);
            const data = await response.json();
            
            // Update logs
            displayLogs(data.logs);
            
            // Update status
            if (data.status === 'completed') {
                executionStatus.className = 'execution-status completed';
                executionStatus.innerHTML = '<i class="fas fa-check"></i><span>Completed</span>';
                clearInterval(logPollingInterval);
                showToast('Task completed successfully!', 'success');
                
                // Show close browser button if there's an active browser session
                if (currentSessionId && window.activeBrowserSessions[currentSessionId]) {
                    closeBrowserBtn.style.display = 'inline-flex';
                }
            } else if (data.status === 'failed') {
                executionStatus.className = 'execution-status failed';
                executionStatus.innerHTML = '<i class="fas fa-times"></i><span>Failed</span>';
                clearInterval(logPollingInterval);
                showToast('Task execution failed', 'error');
            }
            
        } catch (error) {
            console.error('Error polling logs:', error);
        }
    }, 1000); // Poll every second
}

// Display logs
function displayLogs(logs) {
    logsContainer.innerHTML = '';
    
    logs.forEach(log => {
        const entry = document.createElement('div');
        entry.className = `log-entry ${log.level}`;
        
        const timestamp = document.createElement('span');
        timestamp.className = 'log-timestamp';
        timestamp.textContent = log.timestamp;
        
        const message = document.createElement('span');
        message.className = 'log-message';
        message.textContent = log.message;
        
        entry.appendChild(timestamp);
        entry.appendChild(message);
        
        logsContainer.appendChild(entry);
    });
    
    // Auto-scroll to bottom
    logsContainer.scrollTop = logsContainer.scrollHeight;
}

// Cancel task
function cancelTask() {
    instructionsSection.style.display = 'none';
    currentInstructions = [];
    currentSessionId = null;
    taskInput.value = '';
    showToast('Task cancelled', 'info');
}

// Close logs
function closeLogs() {
    // Close browser if it's still open
    if (currentSessionId && currentSessionId in window.activeBrowserSessions) {
        closeBrowserForSession(currentSessionId);
    }
    
    logsSection.style.display = 'none';
    closeBrowserBtn.style.display = 'none';
    
    if (logPollingInterval) {
        clearInterval(logPollingInterval);
    }
    taskInput.value = '';
    currentInstructions = [];
    currentSessionId = null;
}

// Close browser for a session
async function closeBrowserForSession(sessionId) {
    try {
        const response = await fetch(`/api/close-browser/${sessionId}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        if (data.success) {
            delete window.activeBrowserSessions[sessionId];
            showToast('Browser closed', 'info');
        }
    } catch (error) {
        console.error('Error closing browser:', error);
    }
}

// Use speech input
async function useSpeechInput() {
    showToast('Listening... Speak now!', 'info');
    speechBtn.disabled = true;
    
    try {
        const response = await fetch('/api/speech', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            taskInput.value = data.text;
            showToast('Speech recognized successfully', 'success');
        } else {
            showToast(data.error || 'Failed to recognize speech', 'error');
        }
        
    } catch (error) {
        console.error('Error with speech input:', error);
        showToast('Speech recognition failed', 'error');
    } finally {
        speechBtn.disabled = false;
    }
}

// Show/hide loading overlay
function showLoading(show) {
    if (show) {
        loadingOverlay.classList.add('active');
    } else {
        loadingOverlay.classList.remove('active');
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = document.createElement('i');
    if (type === 'success') {
        icon.className = 'fas fa-check-circle';
    } else if (type === 'error') {
        icon.className = 'fas fa-exclamation-circle';
    } else {
        icon.className = 'fas fa-info-circle';
    }
    
    const text = document.createElement('span');
    text.textContent = message;
    
    toast.appendChild(icon);
    toast.appendChild(text);
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'toastSlideIn 0.3s ease-out reverse';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 5000);
}

