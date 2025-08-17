class InboxTriageApp {
    constructor() {
        this.isConnected = false;
        this.clusters = [];
        this.currentArchiveCluster = null;
        
        this.initializeElements();
        this.bindEvents();
        this.checkOAuthConfig();
        this.checkConnectionStatus();
    }
    
    initializeElements() {
        // Sections
        this.loginSection = document.getElementById('loginSection');
        this.dashboardSection = document.getElementById('dashboardSection');
        
        // Login elements
        this.loginForm = document.getElementById('loginForm');
        this.connectBtn = document.getElementById('connectBtn');
        this.usernameInput = document.getElementById('username');
        this.passwordInput = document.getElementById('password');
        this.googleSignInBtn = document.getElementById('googleSignInBtn');
        this.oauthHelp = document.getElementById('oauthHelp');
        this.oauthMessage = document.getElementById('oauthMessage');
        
        // Dashboard elements
        this.connectionStatus = document.getElementById('connectionStatus');
        this.refreshBtn = document.getElementById('refreshBtn');
        this.disconnectBtn = document.getElementById('disconnectBtn');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        this.clustersContainer = document.getElementById('clustersContainer');
        
        // Modal elements
        this.modalOverlay = document.getElementById('modalOverlay');
        this.archiveCount = document.getElementById('archiveCount');
        this.archiveClusterName = document.getElementById('archiveClusterName');
        this.cancelArchive = document.getElementById('cancelArchive');
        this.confirmArchive = document.getElementById('confirmArchive');
        
        // Toast container
        this.toastContainer = document.getElementById('toastContainer');
    }
    
    bindEvents() {
        this.loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        this.googleSignInBtn.addEventListener('click', () => this.handleGoogleSignIn());
        this.refreshBtn.addEventListener('click', () => this.loadClusters());
        this.disconnectBtn.addEventListener('click', () => this.handleDisconnect());
        
        // Listen for OAuth callback messages
        window.addEventListener('message', (e) => this.handleOAuthMessage(e));
        
        // Modal events
        this.modalOverlay.addEventListener('click', (e) => {
            if (e.target === this.modalOverlay) this.closeModal();
        });
        this.cancelArchive.addEventListener('click', () => this.closeModal());
        this.confirmArchive.addEventListener('click', () => this.handleArchiveConfirm());
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modalOverlay.style.display !== 'none') {
                this.closeModal();
            }
        });
    }
    
    async checkConnectionStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            if (data.connected) {
                this.showDashboard();
                this.loadClusters();
            } else {
                this.showLogin();
            }
        } catch (error) {
            console.error('Error checking connection status:', error);
            this.showLogin();
        }
    }
    
    async checkOAuthConfig() {
        try {
            const response = await fetch('/api/oauth/config');
            const data = await response.json();
            
            if (data.available) {
                this.googleSignInBtn.style.display = 'flex';
                this.oauthHelp.style.display = 'none';
            } else {
                this.googleSignInBtn.style.display = 'none';
                this.oauthHelp.style.display = 'block';
                this.oauthMessage.textContent = 'OAuth not configured. Using App Password only.';
            }
        } catch (error) {
            console.error('Error checking OAuth config:', error);
            this.googleSignInBtn.style.display = 'none';
        }
    }
    
    async handleGoogleSignIn() {
        try {
            this.setButtonLoading(this.googleSignInBtn, true);
            
            const response = await fetch('/api/oauth/authorize');
            const data = await response.json();
            
            if (data.success) {
                // Open OAuth popup
                const popup = window.open(
                    data.auth_url,
                    'google-oauth',
                    'width=500,height=600,scrollbars=yes,resizable=yes'
                );
                
                // Check if popup was blocked
                if (!popup) {
                    this.showToast('Popup blocked! Please allow popups and try again.', 'error');
                    return;
                }
                
                // Monitor popup for closure
                const checkClosed = setInterval(() => {
                    if (popup.closed) {
                        clearInterval(checkClosed);
                        this.setButtonLoading(this.googleSignInBtn, false);
                    }
                }, 1000);
                
            } else {
                this.showToast(data.error || 'Failed to start OAuth flow', 'error');
            }
        } catch (error) {
            this.showToast('Error starting Google Sign-In', 'error');
            console.error('OAuth error:', error);
        } finally {
            this.setButtonLoading(this.googleSignInBtn, false);
        }
    }
    
    handleOAuthMessage(event) {
        if (event.data.type === 'oauth_success') {
            const user = event.data.user;
            this.showToast(`Welcome ${user.name}! You can now enter your App Password.`, 'success');
            
            // Pre-fill the email field
            if (this.usernameInput && user.email) {
                this.usernameInput.value = user.email;
                this.passwordInput.focus();
            }
            
            // Show helpful message
            this.oauthHelp.style.display = 'block';
            this.oauthMessage.innerHTML = `
                <strong>Almost there!</strong> Now enter your Gmail App Password below to complete the connection.
                <a href="https://myaccount.google.com/apppasswords" target="_blank">Generate App Password</a>
            `;
        }
    }
    
    async handleLogin(e) {
        e.preventDefault();
        
        const username = this.usernameInput.value.trim();
        const password = this.passwordInput.value.trim();
        
        if (!username || !password) {
            this.showToast('Please enter both username and password', 'error');
            return;
        }
        
        this.setButtonLoading(this.connectBtn, true);
        
        try {
            const response = await fetch('/api/connect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showToast('Successfully connected to Gmail!', 'success');
                this.showDashboard();
                this.loadClusters();
            } else {
                this.showToast(data.error || 'Failed to connect to Gmail', 'error');
            }
        } catch (error) {
            this.showToast('Connection error. Please try again.', 'error');
            console.error('Login error:', error);
        } finally {
            this.setButtonLoading(this.connectBtn, false);
        }
    }
    
    async handleDisconnect() {
        try {
            await fetch('/api/disconnect', { method: 'POST' });
            this.showLogin();
            this.showToast('Disconnected from Gmail', 'success');
        } catch (error) {
            console.error('Disconnect error:', error);
        }
    }
    
    async loadClusters() {
        this.showLoading(true);
        this.clustersContainer.innerHTML = '';
        
        try {
            const response = await fetch('/api/clusters');
            const data = await response.json();
            
            if (data.success) {
                this.clusters = data.clusters;
                this.renderClusters();
                this.showToast(`Found ${this.clusters.length} email clusters`, 'success');
            } else {
                this.showToast(data.error || 'Failed to load clusters', 'error');
            }
        } catch (error) {
            this.showToast('Error loading clusters. Please try again.', 'error');
            console.error('Load clusters error:', error);
        } finally {
            this.showLoading(false);
        }
    }
    
    renderClusters() {
        if (this.clusters.length === 0) {
            this.clustersContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <h3>No emails found</h3>
                    <p>Your inbox appears to be empty or all emails are already processed.</p>
                </div>
            `;
            return;
        }
        
        this.clustersContainer.innerHTML = this.clusters.map((cluster, index) => `
            <div class="cluster-card" data-cluster-id="${cluster.id}">
                <div class="cluster-header">
                    <div class="cluster-title">
                        <div class="cluster-icon">
                            ${this.getClusterIcon(cluster.name)}
                        </div>
                        <div>
                            <div class="cluster-name">${cluster.name}</div>
                        </div>
                    </div>
                    <div class="cluster-count">${cluster.count} emails</div>
                </div>
                
                <div class="emails-preview">
                    ${cluster.emails.slice(0, 3).map(email => `
                        <div class="email-item">
                            <div class="email-subject">${this.escapeHtml(email.subject)}</div>
                            <div class="email-sender">${this.escapeHtml(this.extractSenderName(email.sender))}</div>
                            <div class="email-preview">${this.escapeHtml(email.body_preview)}</div>
                        </div>
                    `).join('')}
                    ${cluster.emails.length > 3 ? `
                        <div class="email-item" style="text-align: center; font-style: italic; color: #666;">
                            ... and ${cluster.emails.length - 3} more emails
                        </div>
                    ` : ''}
                </div>
                
                <div class="cluster-actions">
                    <button class="btn btn-danger archive-btn" onclick="app.showArchiveModal(${cluster.id})">
                        <i class="fas fa-archive"></i>
                        Archive All
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    getClusterIcon(clusterName) {
        const name = clusterName.toLowerCase();
        
        if (name.includes('promotional') || name.includes('deal') || name.includes('sale')) {
            return '<i class="fas fa-tags"></i>';
        } else if (name.includes('meeting') || name.includes('event') || name.includes('calendar')) {
            return '<i class="fas fa-calendar"></i>';
        } else if (name.includes('notification') || name.includes('alert') || name.includes('update')) {
            return '<i class="fas fa-bell"></i>';
        } else if (name.includes('from')) {
            return '<i class="fas fa-user"></i>';
        } else if (name.includes('social') || name.includes('linkedin') || name.includes('facebook')) {
            return '<i class="fas fa-share-alt"></i>';
        } else if (name.includes('news') || name.includes('newsletter')) {
            return '<i class="fas fa-newspaper"></i>';
        } else {
            return '<i class="fas fa-folder"></i>';
        }
    }
    
    extractSenderName(sender) {
        // Extract name from email format "Name <email@domain.com>"
        const match = sender.match(/^"?([^"<]+)"?\s*</);
        if (match) {
            return match[1].trim();
        }
        
        // If no name found, return the email part before @
        const emailMatch = sender.match(/([^@]+)@/);
        if (emailMatch) {
            return emailMatch[1].replace(/[._]/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        }
        
        return sender;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showArchiveModal(clusterId) {
        const cluster = this.clusters.find(c => c.id === clusterId);
        if (!cluster) return;
        
        this.currentArchiveCluster = cluster;
        this.archiveCount.textContent = cluster.count;
        this.archiveClusterName.textContent = cluster.name;
        this.modalOverlay.style.display = 'flex';
    }
    
    closeModal() {
        this.modalOverlay.style.display = 'none';
        this.currentArchiveCluster = null;
    }
    
    async handleArchiveConfirm() {
        if (!this.currentArchiveCluster) return;
        
        this.setButtonLoading(this.confirmArchive, true);
        
        try {
            const response = await fetch('/api/archive', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ cluster_id: this.currentArchiveCluster.id })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showToast(data.message, 'success');
                this.closeModal();
                // Refresh clusters after successful archive
                setTimeout(() => this.loadClusters(), 1000);
            } else {
                this.showToast(data.error || 'Failed to archive emails', 'error');
            }
        } catch (error) {
            this.showToast('Error archiving emails. Please try again.', 'error');
            console.error('Archive error:', error);
        } finally {
            this.setButtonLoading(this.confirmArchive, false);
        }
    }
    
    showLogin() {
        this.isConnected = false;
        this.loginSection.style.display = 'flex';
        this.dashboardSection.style.display = 'none';
        this.updateConnectionStatus(false);
        
        // Clear login form
        this.usernameInput.value = '';
        this.passwordInput.value = '';
    }
    
    showDashboard() {
        this.isConnected = true;
        this.loginSection.style.display = 'none';
        this.dashboardSection.style.display = 'block';
        this.updateConnectionStatus(true);
    }
    
    updateConnectionStatus(connected) {
        const indicator = this.connectionStatus.querySelector('.status-indicator');
        const text = this.connectionStatus.querySelector('.status-text');
        
        if (connected) {
            indicator.className = 'status-indicator connected';
            text.textContent = 'Connected';
        } else {
            indicator.className = 'status-indicator disconnected';
            text.textContent = 'Disconnected';
        }
    }
    
    showLoading(show) {
        this.loadingSpinner.style.display = show ? 'block' : 'none';
        this.refreshBtn.disabled = show;
    }
    
    setButtonLoading(button, loading) {
        if (loading) {
            button.disabled = true;
            const originalText = button.innerHTML;
            button.dataset.originalText = originalText;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || button.innerHTML;
        }
    }
    
    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
        
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas ${icon} toast-icon"></i>
                <span class="toast-message">${message}</span>
            </div>
        `;
        
        this.toastContainer.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
        
        // Click to remove
        toast.addEventListener('click', () => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        });
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new InboxTriageApp();
});