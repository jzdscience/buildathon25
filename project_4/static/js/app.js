// Main JavaScript for Codebase Time Machine Web Interface

// Initialize Socket.IO connection
const socket = io();

// Global variables
let analysisInProgress = false;
let currentAnalysisId = null;

// DOM ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize form handlers
    initializeFormHandlers();
    
    // Initialize socket event listeners
    initializeSocketHandlers();
    
    // Check for existing analysis status
    checkAnalysisStatus();
}

function initializeFormHandlers() {
    // Main analysis form
    const analysisForm = document.getElementById('analysisForm');
    if (analysisForm) {
        analysisForm.addEventListener('submit', handleAnalysisSubmit);
    }
    
    // Demo analysis forms
    const demoForms = document.querySelectorAll('[id*="analysisForm"]');
    demoForms.forEach(form => {
        if (form.id !== 'analysisForm') {
            form.addEventListener('submit', handleAnalysisSubmit);
        }
    });
    
    // Query form handlers
    setupQueryHandlers();
}

function initializeSocketHandlers() {
    // Socket connection events
    socket.on('connect', function() {
        console.log('Connected to server');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        updateConnectionStatus(false);
    });
    
    // Analysis progress events
    socket.on('progress_update', function(data) {
        console.log('Progress update:', data);
        updateProgress(data.message, data.progress);
    });
    
    socket.on('analysis_complete', function(data) {
        console.log('Analysis complete:', data);
        handleAnalysisComplete(data);
    });
    
    socket.on('analysis_error', function(data) {
        console.log('Analysis error:', data);
        handleAnalysisError(data.error);
    });
    
    socket.on('status_update', function(data) {
        console.log('Status update:', data);
        updateAnalysisStatus(data);
    });
}

function handleAnalysisSubmit(event) {
    event.preventDefault();
    
    if (analysisInProgress) {
        showAlert('Analysis already in progress', 'warning');
        return;
    }
    
    const form = event.target;
    const formData = new FormData(form);
    
    // Try to get URL from different possible field names
    let repoUrl = formData.get('repoUrl') || 
                  formData.get('customRepoUrl') || 
                  document.getElementById('repoUrl')?.value ||
                  document.getElementById('customRepoUrl')?.value;
    
    // Check for full analysis checkbox
    let fullAnalysis = formData.get('fullAnalysis') === 'on' || 
                      formData.get('customFullAnalysis') === 'on' ||
                      document.getElementById('fullAnalysis')?.checked ||
                      document.getElementById('customFullAnalysis')?.checked;
    
    console.log('Form submission:', { repoUrl, fullAnalysis, formData: Object.fromEntries(formData) });
    
    if (!repoUrl || repoUrl.trim() === '') {
        showAlert('Please enter a repository URL', 'danger');
        return;
    }
    
    startAnalysis(repoUrl.trim(), null, fullAnalysis);
}

function startAnalysis(repoUrl, repoPath, fullAnalysis = false) {
    if (analysisInProgress) {
        showAlert('Analysis already in progress', 'warning');
        return;
    }
    
    // Validate input
    if (!repoUrl && !repoPath) {
        showAlert('Please provide a repository URL or path', 'danger');
        return;
    }
    
    console.log('Starting analysis with:', { repoUrl, repoPath, fullAnalysis });
    
    analysisInProgress = true;
    
    // Show progress modal
    showProgressModal();
    
    // Send analysis request
    fetch('/api/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            repo_url: repoUrl,
            repo_path: repoPath,
            full_analysis: fullAnalysis
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        console.log('Analysis started:', data.message);
        showAlert('Analysis started successfully!', 'success');
        
        // Start polling for status updates as fallback
        startStatusPolling();
    })
    .catch(error => {
        console.error('Error starting analysis:', error);
        hideProgressModal();
        showAlert(`Error starting analysis: ${error.message}`, 'danger');
        analysisInProgress = false;
    });
}

function updateProgress(message, progress) {
    const progressBar = document.getElementById('analysisProgress') || document.getElementById('demoProgress');
    const progressMessage = document.getElementById('progressMessage') || document.getElementById('demoProgressMessage');
    
    if (progressBar && progress !== undefined) {
        progressBar.style.width = progress + '%';
        progressBar.setAttribute('aria-valuenow', progress);
        progressBar.textContent = progress + '%';
    }
    
    if (progressMessage) {
        progressMessage.textContent = message;
    }
    
    // Update demo progress if on demo page
    updateDemoProgress(message, progress);
}

function updateDemoProgress(message, progress) {
    const demoProgressBar = document.getElementById('demoProgress');
    const demoProgressMessage = document.getElementById('demoProgressMessage');
    
    if (demoProgressBar && progress !== undefined) {
        demoProgressBar.style.width = progress + '%';
        demoProgressBar.setAttribute('aria-valuenow', progress);
        demoProgressBar.textContent = progress + '%';
    }
    
    if (demoProgressMessage) {
        demoProgressMessage.textContent = message;
    }
}

function handleAnalysisComplete(data) {
    console.log('Handling analysis complete...', data);
    analysisInProgress = false;
    
    // Update progress to 100% first
    updateProgress('Analysis completed!', 100);
    
    // Hide modal after a short delay to show completion
    setTimeout(() => {
        hideProgressModal();
        
        // Hide demo progress section
        const demoStatus = document.getElementById('analysisStatus');
        if (demoStatus) {
            demoStatus.style.display = 'none';
        }
        
        showAlert('Analysis completed successfully!', 'success');
        
        // Redirect to results page after showing success message
        setTimeout(() => {
            window.location.href = '/results';
        }, 1500);
    }, 1000);
}

function handleAnalysisError(error) {
    analysisInProgress = false;
    hideProgressModal();
    
    // Hide demo progress section
    const demoStatus = document.getElementById('analysisStatus');
    if (demoStatus) {
        demoStatus.style.display = 'none';
    }
    
    showAlert(`Analysis failed: ${error}`, 'danger');
}

let progressModalInstance = null;

function showProgressModal() {
    const modal = document.getElementById('progressModal');
    if (modal) {
        if (!progressModalInstance) {
            progressModalInstance = new bootstrap.Modal(modal, {
                backdrop: 'static',
                keyboard: false
            });
        }
        progressModalInstance.show();
        console.log('Progress modal shown');
    }
}

function hideProgressModal() {
    if (progressModalInstance) {
        progressModalInstance.hide();
        console.log('Progress modal hidden');
    } else {
        // Fallback method
        const modal = document.getElementById('progressModal');
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
    }
}

function setupQueryHandlers() {
    // Main query input
    const queryInput = document.getElementById('queryInput');
    if (queryInput) {
        queryInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                submitQuery();
            }
        });
    }
    
    // Demo query input
    const demoQueryInput = document.getElementById('demoQueryInput');
    if (demoQueryInput) {
        demoQueryInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                customDemoQuery();
            }
        });
    }
}

function submitQuery() {
    const queryInput = document.getElementById('queryInput');
    const query = queryInput.value.trim();
    
    if (!query) {
        showAlert('Please enter a query', 'warning');
        return;
    }
    
    const responseDiv = document.getElementById('queryResponse');
    const resultDiv = document.getElementById('queryResult');
    
    if (responseDiv) responseDiv.style.display = 'block';
    if (resultDiv) resultDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing query...';
    
    fetch('/api/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            if (resultDiv) resultDiv.innerHTML = `<div class="text-danger">Error: ${data.error}</div>`;
        } else {
            if (resultDiv) resultDiv.innerHTML = `<pre class="mb-0">${data.response}</pre>`;
        }
        if (responseDiv) {
            responseDiv.scrollIntoView({ behavior: 'smooth' });
        }
    })
    .catch(error => {
        if (resultDiv) resultDiv.innerHTML = `<div class="text-danger">Error: ${error.message}</div>`;
    });
}

function checkAnalysisStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            updateAnalysisStatus(data);
        })
        .catch(error => {
            console.error('Error checking status:', error);
        });
}

let statusPollingInterval = null;
let analysisTimeout = null;

function startStatusPolling() {
    console.log('Starting status polling...');
    
    // Clear any existing interval
    if (statusPollingInterval) {
        clearInterval(statusPollingInterval);
    }
    
    // Set a timeout for the analysis (5 minutes max)
    if (analysisTimeout) {
        clearTimeout(analysisTimeout);
    }
    
    analysisTimeout = setTimeout(() => {
        console.log('Analysis timeout reached - forcing completion');
        analysisInProgress = false;
        hideProgressModal();
        showAlert('Analysis timed out. Please try again with a smaller repository.', 'warning');
        
        if (statusPollingInterval) {
            clearInterval(statusPollingInterval);
            statusPollingInterval = null;
        }
    }, 300000); // 5 minutes
    
    statusPollingInterval = setInterval(() => {
        if (!analysisInProgress) {
            clearInterval(statusPollingInterval);
            statusPollingInterval = null;
            return;
        }
        
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                console.log('Polling status:', data);
                updateAnalysisStatus(data);
                
                if (data.status === 'completed') {
                    clearInterval(statusPollingInterval);
                    statusPollingInterval = null;
                    if (analysisTimeout) {
                        clearTimeout(analysisTimeout);
                        analysisTimeout = null;
                    }
                    handleAnalysisComplete(data.results || {});
                } else if (data.status === 'error') {
                    clearInterval(statusPollingInterval);
                    statusPollingInterval = null;
                    if (analysisTimeout) {
                        clearTimeout(analysisTimeout);
                        analysisTimeout = null;
                    }
                    handleAnalysisError(data.error || 'Unknown error');
                } else if (data.status === 'running' && data.message) {
                    updateProgress(data.message, data.progress);
                }
            })
            .catch(error => {
                console.error('Error polling status:', error);
            });
    }, 2000); // Poll every 2 seconds
}

function updateAnalysisStatus(status) {
    if (status.status === 'running') {
        analysisInProgress = true;
        if (status.progress !== undefined) {
            updateProgress(status.message, status.progress);
        }
    } else if (status.status === 'completed') {
        analysisInProgress = false;
        if (status.results) {
            // Could redirect to results or show completion message
        }
    } else if (status.status === 'error') {
        analysisInProgress = false;
        if (status.error) {
            showAlert(`Analysis error: ${status.error}`, 'danger');
        }
    }
}

function updateConnectionStatus(connected) {
    // Add connection status indicator if needed
    const statusIndicator = document.getElementById('connectionStatus');
    if (statusIndicator) {
        statusIndicator.className = connected ? 
            'status-indicator status-connected' : 
            'status-indicator status-disconnected';
    }
}

function showAlert(message, type = 'info', duration = 5000) {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    alertDiv.innerHTML = `
        <strong>${type.charAt(0).toUpperCase() + type.slice(1)}:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, duration);
}

// Utility functions
function setExampleQuery(query) {
    const queryInput = document.getElementById('queryInput');
    if (queryInput) {
        queryInput.value = query;
    }
}

function setExampleRepo(url) {
    const repoInput = document.getElementById('repoUrl');
    if (repoInput) {
        repoInput.value = url;
    }
}

// Demo-specific functions
function startDemoAnalysis(repoUrl, fullAnalysis) {
    console.log(`Starting demo analysis for: ${repoUrl}, full: ${fullAnalysis}`);
    
    // Show analysis status section
    const statusSection = document.getElementById('analysisStatus');
    if (statusSection) {
        statusSection.style.display = 'block';
        statusSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Start the analysis
    startAnalysis(repoUrl, null, fullAnalysis);
}

// Export functions for global access
window.startAnalysis = startAnalysis;
window.submitQuery = submitQuery;
window.setExampleQuery = setExampleQuery;
window.setExampleRepo = setExampleRepo;
window.showAlert = showAlert;
window.startDemoAnalysis = startDemoAnalysis;

// Additional demo-specific functions
window.customDemoQuery = function() {
    const demoQueryInput = document.getElementById('demoQueryInput');
    if (!demoQueryInput) return;
    
    const query = demoQueryInput.value.trim();
    if (!query) return;
    
    const responseDiv = document.getElementById('demoQueryResponse');
    const resultDiv = document.getElementById('demoQueryResult');
    
    if (responseDiv) responseDiv.style.display = 'block';
    if (resultDiv) resultDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing query...';
    
    fetch('/api/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            if (resultDiv) resultDiv.innerHTML = `<div class="text-danger">Error: ${data.error}</div>`;
        } else {
            if (resultDiv) resultDiv.innerHTML = `<pre class="mb-0">${data.response}</pre>`;
        }
    })
    .catch(error => {
        if (resultDiv) resultDiv.innerHTML = `<div class="text-danger">Error: ${error.message}</div>`;
    });
};

window.demoQuery = function(query) {
    const demoQueryInput = document.getElementById('demoQueryInput');
    if (demoQueryInput) {
        demoQueryInput.value = query;
        window.customDemoQuery();
    }
};

// Show documentation modal
window.showDocumentation = function() {
    const docModal = document.getElementById('docModal');
    if (docModal) {
        new bootstrap.Modal(docModal).show();
    }
};