// Main Application JavaScript
class POSApp {
    constructor() {
        this.currentUser = null;
        this.currentScreen = 'login-screen';
        this.autoRefreshInterval = null;
        this.isKioskMode = false;
        this.idleTimer = null;
        this.settings = {};
        
        this.init();
    }
    
    async init() {
        try {
            // Get app info
            const appInfo = await window.electronAPI.getAppInfo();
            this.isKioskMode = appInfo.isKioskMode;
            
            // Load settings
            this.settings = await window.electronAPI.settings.get();
            
            // Initialize components
            this.initializeEventListeners();
            this.initializeTimeDisplay();
            this.checkDatabaseConnection();
            
            // Apply theme
            this.applyTheme(this.settings.theme || 'light');
            
            // Hide loading screen and show app
            setTimeout(() => {
                document.getElementById('loading-screen').classList.add('hidden');
                document.getElementById('app').classList.remove('hidden');
                
                // Show version in login screen
                this.updateVersionDisplay(appInfo.version);
                
                // Hide window controls in kiosk mode
                if (this.isKioskMode) {
                    document.getElementById('window-controls').style.display = 'none';
                }
                
                // Initialize idle timer
                this.initializeIdleTimer();
                
            }, 2000);
            
        } catch (error) {
            console.error('Failed to initialize app:', error);
            this.showToast('Error', 'Failed to initialize application', 'error');
        }
    }
    
    initializeEventListeners() {
        // Window controls
        document.getElementById('minimize-btn')?.addEventListener('click', () => {
            window.electronAPI.window.minimize();
        });
        
        document.getElementById('maximize-btn')?.addEventListener('click', () => {
            window.electronAPI.window.maximize();
        });
        
        document.getElementById('close-btn')?.addEventListener('click', () => {
            window.electronAPI.window.close();
        });
        
        // Navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const screen = e.currentTarget.dataset.screen;
                this.navigateToScreen(screen);
            });
        });
        
        // Login form
        document.getElementById('login-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });
        
        // Logout button
        document.getElementById('logout-btn')?.addEventListener('click', () => {
            this.handleLogout();
        });
        
        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
        
        // Reset idle timer on user activity
        ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'].forEach(event => {
            document.addEventListener(event, () => {
                this.resetIdleTimer();
            }, { passive: true });
        });
    }
    
    initializeTimeDisplay() {
        const updateTime = () => {
            const now = new Date();
            const timeString = now.toLocaleTimeString('en-US', {
                hour12: true,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            const dateString = now.toLocaleDateString('en-US', {
                weekday: 'short',
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
            
            const timeElement = document.getElementById('current-time');
            if (timeElement) {
                timeElement.innerHTML = `${timeString}<br><small>${dateString}</small>`;
            }
        };
        
        updateTime();
        setInterval(updateTime, 1000);
    }
    
    async checkDatabaseConnection() {
        try {
            const dbPath = await window.electronAPI.database.getPath();
            console.log('Database path:', dbPath);
            
            // Initialize database if needed
            if (window.posDatabase) {
                await window.posDatabase.initialize();
            }
        } catch (error) {
            console.error('Database connection error:', error);
            this.showToast('Database Error', 'Failed to connect to database', 'error');
        }
    }
    
    updateVersionDisplay(version) {
        const versionElement = document.getElementById('app-version');
        if (versionElement) {
            versionElement.textContent = `Version ${version}`;
        }
    }
    
    applyTheme(themeName) {
        document.body.className = document.body.className.replace(/theme-\w+/, '');
        document.body.classList.add(`theme-${themeName}`);
        this.settings.theme = themeName;
    }
    
    navigateToScreen(screenId) {
        // Check permissions
        if (!this.hasPermissionForScreen(screenId)) {
            this.showToast('Access Denied', 'You do not have permission to access this screen', 'error');
            return;
        }
        
        // Hide current screen
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        
        // Show new screen
        const newScreen = document.getElementById(screenId);
        if (newScreen) {
            newScreen.classList.add('active');
            this.currentScreen = screenId;
            
            // Update navigation
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            const activeBtn = document.querySelector(`[data-screen="${screenId}"]`);
            if (activeBtn) {
                activeBtn.classList.add('active');
            }
            
            // Load screen data
            this.loadScreenData(screenId);
        }
    }
    
    hasPermissionForScreen(screenId) {
        if (!this.currentUser) {
            return screenId === 'login-screen';
        }
        
        const userRole = this.currentUser.role;
        
        switch (screenId) {
            case 'pos-screen':
                return ['admin', 'cashier'].includes(userRole);
            case 'kitchen-screen':
                return ['admin', 'kitchen', 'cashier'].includes(userRole);
            case 'admin-screen':
                return userRole === 'admin';
            default:
                return true;
        }
    }
    
    loadScreenData(screenId) {
        switch (screenId) {
            case 'pos-screen':
                if (window.posScreen) {
                    window.posScreen.loadData();
                }
                break;
            case 'kitchen-screen':
                if (window.kitchenDisplay) {
                    window.kitchenDisplay.loadOrders();
                    window.kitchenDisplay.startAutoRefresh();
                }
                break;
            case 'admin-screen':
                if (window.adminPanel) {
                    window.adminPanel.loadData();
                }
                break;
        }
    }
    
    async handleLogin() {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();
        
        if (!username || !password) {
            this.showToast('Login Error', 'Please enter username and password', 'error');
            return;
        }
        
        try {
            // Show loading state
            const loginBtn = document.querySelector('#login-form button[type="submit"]');
            const originalText = loginBtn.innerHTML;
            loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging in...';
            loginBtn.disabled = true;
            
            // Authenticate user
            if (window.posAuth) {
                const user = await window.posAuth.login(username, password);
                
                if (user) {
                    this.currentUser = user;
                    this.updateUserDisplay();
                    this.showUserInterface();
                    this.navigateToScreen('pos-screen');
                    
                    this.showToast('Login Successful', `Welcome back, ${user.full_name || user.username}!`, 'success');
                    
                    // Clear form
                    document.getElementById('login-form').reset();
                } else {
                    this.showToast('Login Failed', 'Invalid username or password', 'error');
                }
            } else {
                this.showToast('Error', 'Authentication system not available', 'error');
            }
            
            // Restore button state
            loginBtn.innerHTML = originalText;
            loginBtn.disabled = false;
            
        } catch (error) {
            console.error('Login error:', error);
            this.showToast('Login Error', 'An error occurred during login', 'error');
            
            // Restore button state
            const loginBtn = document.querySelector('#login-form button[type="submit"]');
            loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
            loginBtn.disabled = false;
        }
    }
    
    handleLogout() {
        if (this.isKioskMode) {
            // In kiosk mode, require confirmation
            this.showModal({
                title: 'Logout Confirmation',
                message: 'Are you sure you want to logout?',
                type: 'confirm',
                onConfirm: () => {
                    this.performLogout();
                }
            });
        } else {
            this.performLogout();
        }
    }
    
    performLogout() {
        this.currentUser = null;
        this.hideUserInterface();
        this.navigateToScreen('login-screen');
        
        // Clear any auto-refresh intervals
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
        
        // Stop kitchen display auto-refresh
        if (window.kitchenDisplay) {
            window.kitchenDisplay.stopAutoRefresh();
        }
        
        this.showToast('Logged Out', 'You have been logged out successfully', 'info');
    }
    
    updateUserDisplay() {
        const userElement = document.getElementById('current-user');
        const logoutBtn = document.getElementById('logout-btn');
        
        if (this.currentUser && userElement) {
            userElement.textContent = this.currentUser.full_name || this.currentUser.username;
            if (logoutBtn) {
                logoutBtn.style.display = 'inline-flex';
            }
        }
    }
    
    showUserInterface() {
        // Show navigation based on user role
        const adminBtns = document.querySelectorAll('.admin-only');
        if (this.currentUser && this.currentUser.role === 'admin') {
            adminBtns.forEach(btn => btn.style.display = 'flex');
        } else {
            adminBtns.forEach(btn => btn.style.display = 'none');
        }
    }
    
    hideUserInterface() {
        const userElement = document.getElementById('current-user');
        const logoutBtn = document.getElementById('logout-btn');
        
        if (userElement) {
            userElement.textContent = 'Not logged in';
        }
        if (logoutBtn) {
            logoutBtn.style.display = 'none';
        }
        
        // Hide all role-specific elements
        document.querySelectorAll('.admin-only').forEach(btn => {
            btn.style.display = 'none';
        });
    }
    
    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + L: Logout
        if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
            e.preventDefault();
            if (this.currentUser) {
                this.handleLogout();
            }
        }
        
        // Ctrl/Cmd + R: Refresh current screen
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            this.loadScreenData(this.currentScreen);
        }
        
        // F11: Toggle fullscreen (dev mode only)
        if (e.key === 'F11' && !this.isKioskMode) {
            e.preventDefault();
            window.electronAPI.window.toggleFullscreen();
        }
        
        // Escape: Clear cart or go back
        if (e.key === 'Escape') {
            if (this.currentScreen === 'pos-screen' && window.posScreen) {
                window.posScreen.clearCart();
            }
        }
        
        // Alt + 1-3: Quick screen navigation
        if (e.altKey) {
            switch (e.key) {
                case '1':
                    e.preventDefault();
                    this.navigateToScreen('pos-screen');
                    break;
                case '2':
                    e.preventDefault();
                    this.navigateToScreen('kitchen-screen');
                    break;
                case '3':
                    e.preventDefault();
                    if (this.currentUser && this.currentUser.role === 'admin') {
                        this.navigateToScreen('admin-screen');
                    }
                    break;
            }
        }
    }
    
    initializeIdleTimer() {
        const idleTimeout = this.settings.kioskSettings?.idleTimeout || 300; // 5 minutes default
        
        if (this.isKioskMode && this.settings.kioskSettings?.autoLogout) {
            this.resetIdleTimer();
        }
    }
    
    resetIdleTimer() {
        if (this.idleTimer) {
            clearTimeout(this.idleTimer);
        }
        
        const idleTimeout = this.settings.kioskSettings?.idleTimeout || 300; // 5 minutes default
        
        if (this.isKioskMode && this.currentUser && this.settings.kioskSettings?.autoLogout) {
            this.idleTimer = setTimeout(() => {
                this.showToast('Session Timeout', 'Logging out due to inactivity...', 'warning');
                setTimeout(() => {
                    this.performLogout();
                }, 3000);
            }, idleTimeout * 1000);
        }
    }
    
    // Utility methods
    showToast(title, message, type = 'info') {
        if (window.Utils) {
            window.Utils.showToast(title, message, type);
        }
    }
    
    showModal(options) {
        if (window.Utils) {
            window.Utils.showModal(options);
        }
    }
    
    async saveSettings() {
        try {
            await window.electronAPI.settings.save(this.settings);
        } catch (error) {
            console.error('Failed to save settings:', error);
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.posApp = new POSApp();
});
