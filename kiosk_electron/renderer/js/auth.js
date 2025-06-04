/**
 * Authentication Module for POS-V2 Electron Kiosk
 * Handles user authentication, session management, and role-based access
 */

class AuthManager {
    constructor() {
        this.currentUser = null;
        this.sessionTimeout = null;
        this.idleTimer = null;
        this.idleTimeout = 30 * 60 * 1000; // 30 minutes
        this.init();
    }

    init() {
        this.setupIdleTimer();
        this.loadSession();
    }

    async login(username, password) {
        try {
            showLoading('Authenticating...');
            
            const user = await dbManager.validateUser(username, password);
            
            if (user) {
                if (!user.active) {
                    hideLoading();
                    showToast('Account is deactivated', 'error');
                    return false;
                }

                this.currentUser = user;
                await this.saveSession();
                this.startSessionTimeout();
                this.resetIdleTimer();
                
                hideLoading();
                showToast(`Welcome, ${user.full_name}!`, 'success');
                
                // Navigate to appropriate screen based on role
                this.navigateByRole();
                return true;
            } else {
                hideLoading();
                showToast('Invalid username or password', 'error');
                return false;
            }
        } catch (error) {
            hideLoading();
            console.error('Login error:', error);
            showToast('Login failed. Please try again.', 'error');
            return false;
        }
    }

    async logout() {
        try {
            // Clear session data
            await dbManager.clearSession();
            this.currentUser = null;
            this.clearTimers();
            
            // Clear any temporary data
            await this.clearCart();
            
            showToast('Logged out successfully', 'success');
            
            // Return to login screen
            this.showScreen('login');
        } catch (error) {
            console.error('Logout error:', error);
            showToast('Error during logout', 'error');
        }
    }

    async saveSession() {
        try {
            await dbManager.setSession('currentUser', this.currentUser);
            await dbManager.setSession('loginTime', new Date().toISOString());
        } catch (error) {
            console.error('Error saving session:', error);
        }
    }

    async loadSession() {
        try {
            const user = await dbManager.getSession('currentUser');
            const loginTime = await dbManager.getSession('loginTime');
            
            if (user && loginTime) {
                const timeDiff = Date.now() - new Date(loginTime).getTime();
                const maxSessionTime = 8 * 60 * 60 * 1000; // 8 hours
                
                if (timeDiff < maxSessionTime) {
                    this.currentUser = user;
                    this.startSessionTimeout();
                    this.navigateByRole();
                    return true;
                } else {
                    // Session expired
                    await this.logout();
                    showToast('Session expired. Please login again.', 'warning');
                }
            }
            
            this.showScreen('login');
            return false;
        } catch (error) {
            console.error('Error loading session:', error);
            this.showScreen('login');
            return false;
        }
    }

    navigateByRole() {
        if (!this.currentUser) {
            this.showScreen('login');
            return;
        }

        switch (this.currentUser.role) {
            case 'admin':
                this.showScreen('admin');
                break;
            case 'cashier':
                this.showScreen('pos');
                break;
            case 'kitchen':
                this.showScreen('kitchen');
                break;
            default:
                this.showScreen('pos');
        }
    }

    showScreen(screenName) {
        // Hide all screens
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.add('hidden');
        });

        // Show selected screen
        const targetScreen = document.getElementById(`${screenName}-screen`);
        if (targetScreen) {
            targetScreen.classList.remove('hidden');
            
            // Initialize screen if needed
            this.initializeScreen(screenName);
        }
    }

    initializeScreen(screenName) {
        switch (screenName) {
            case 'pos':
                if (window.posManager) {
                    window.posManager.init();
                }
                break;
            case 'kitchen':
                if (window.kitchenManager) {
                    window.kitchenManager.init();
                }
                break;
            case 'admin':
                if (window.adminManager) {
                    window.adminManager.init();
                }
                break;
        }
    }

    hasPermission(permission) {
        if (!this.currentUser) return false;

        const permissions = {
            admin: [
                'view_admin_panel',
                'manage_users',
                'manage_menu',
                'view_reports',
                'manage_settings',
                'process_orders',
                'view_kitchen',
                'manage_expenses'
            ],
            cashier: [
                'process_orders',
                'view_menu'
            ],
            kitchen: [
                'view_kitchen',
                'update_order_status'
            ]
        };

        const userPermissions = permissions[this.currentUser.role] || [];
        return userPermissions.includes(permission);
    }

    requirePermission(permission) {
        if (!this.hasPermission(permission)) {
            showToast('Access denied. Insufficient permissions.', 'error');
            throw new Error(`Permission denied: ${permission}`);
        }
    }

    startSessionTimeout() {
        this.clearTimers();
        
        // Auto logout after 8 hours
        this.sessionTimeout = setTimeout(() => {
            showToast('Session expired. Please login again.', 'warning');
            this.logout();
        }, 8 * 60 * 60 * 1000);
    }

    setupIdleTimer() {
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        
        const resetTimer = () => {
            this.resetIdleTimer();
        };

        events.forEach(event => {
            document.addEventListener(event, resetTimer, true);
        });
    }

    resetIdleTimer() {
        if (this.idleTimer) {
            clearTimeout(this.idleTimer);
        }

        if (this.currentUser) {
            this.idleTimer = setTimeout(() => {
                this.showIdleWarning();
            }, this.idleTimeout - 60000); // Warning 1 minute before timeout
        }
    }

    showIdleWarning() {
        const result = confirm('You have been idle for a while. Do you want to continue your session?');
        
        if (result) {
            this.resetIdleTimer();
            showToast('Session extended', 'success');
        } else {
            showToast('Logging out due to inactivity', 'warning');
            this.logout();
        }
    }

    clearTimers() {
        if (this.sessionTimeout) {
            clearTimeout(this.sessionTimeout);
            this.sessionTimeout = null;
        }
        
        if (this.idleTimer) {
            clearTimeout(this.idleTimer);
            this.idleTimer = null;
        }
    }

    async clearCart() {
        try {
            await dbManager.setSession('cart', []);
            await dbManager.setSession('cartTotal', 0);
        } catch (error) {
            console.error('Error clearing cart:', error);
        }
    }

    getCurrentUser() {
        return this.currentUser;
    }

    isLoggedIn() {
        return this.currentUser !== null;
    }

    getCurrentUserRole() {
        return this.currentUser ? this.currentUser.role : null;
    }

    getCurrentUserName() {
        return this.currentUser ? this.currentUser.full_name : null;
    }

    // Quick role checks
    isAdmin() {
        return this.getCurrentUserRole() === 'admin';
    }

    isCashier() {
        return this.getCurrentUserRole() === 'cashier';
    }

    isKitchen() {
        return this.getCurrentUserRole() === 'kitchen';
    }

    // User management functions (admin only)
    async createUser(userData) {
        this.requirePermission('manage_users');
        
        try {
            const existingUser = await dbManager.getUserByUsername(userData.username);
            if (existingUser) {
                throw new Error('Username already exists');
            }

            const userId = await dbManager.createUser(userData);
            showToast('User created successfully', 'success');
            return userId;
        } catch (error) {
            console.error('Error creating user:', error);
            showToast('Failed to create user: ' + error.message, 'error');
            throw error;
        }
    }

    async updateUser(userId, userData) {
        this.requirePermission('manage_users');
        
        try {
            if (userData.password) {
                userData.password = await dbManager.hashPassword(userData.password);
            }
            
            await dbManager.update('users', { id: userId, ...userData });
            showToast('User updated successfully', 'success');
        } catch (error) {
            console.error('Error updating user:', error);
            showToast('Failed to update user', 'error');
            throw error;
        }
    }

    async deleteUser(userId) {
        this.requirePermission('manage_users');
        
        try {
            // Don't allow deleting current user
            if (this.currentUser && this.currentUser.id === userId) {
                throw new Error('Cannot delete current user');
            }

            await dbManager.delete('users', userId);
            showToast('User deleted successfully', 'success');
        } catch (error) {
            console.error('Error deleting user:', error);
            showToast('Failed to delete user: ' + error.message, 'error');
            throw error;
        }
    }

    async toggleUserStatus(userId) {
        this.requirePermission('manage_users');
        
        try {
            const user = await dbManager.read('users', userId);
            if (user) {
                user.active = !user.active;
                await dbManager.update('users', user);
                showToast(`User ${user.active ? 'activated' : 'deactivated'}`, 'success');
                return user.active;
            }
        } catch (error) {
            console.error('Error toggling user status:', error);
            showToast('Failed to update user status', 'error');
            throw error;
        }
    }

    async getAllUsers() {
        this.requirePermission('manage_users');
        
        try {
            return await dbManager.getAll('users');
        } catch (error) {
            console.error('Error getting all users:', error);
            throw error;
        }
    }

    // Change password
    async changePassword(oldPassword, newPassword) {
        try {
            if (!this.currentUser) {
                throw new Error('Not logged in');
            }

            // Verify old password
            const isValid = await dbManager.validateUser(this.currentUser.username, oldPassword);
            if (!isValid) {
                throw new Error('Current password is incorrect');
            }

            // Update password
            const hashedPassword = await dbManager.hashPassword(newPassword);
            await dbManager.update('users', {
                ...this.currentUser,
                password: hashedPassword
            });

            showToast('Password changed successfully', 'success');
        } catch (error) {
            console.error('Error changing password:', error);
            showToast('Failed to change password: ' + error.message, 'error');
            throw error;
        }
    }
}

// Initialize authentication manager
const authManager = new AuthManager();

// Login form handler
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            
            if (!username || !password) {
                showToast('Please enter both username and password', 'error');
                return;
            }

            await authManager.login(username, password);
        });
    }

    // Logout buttons
    document.querySelectorAll('.logout-btn').forEach(button => {
        button.addEventListener('click', async () => {
            const result = confirm('Are you sure you want to logout?');
            if (result) {
                await authManager.logout();
            }
        });
    });

    // User info display
    const updateUserInfo = () => {
        const userElements = document.querySelectorAll('.current-user');
        userElements.forEach(element => {
            if (authManager.isLoggedIn()) {
                element.textContent = authManager.getCurrentUserName();
            }
        });

        const roleElements = document.querySelectorAll('.current-role');
        roleElements.forEach(element => {
            if (authManager.isLoggedIn()) {
                element.textContent = authManager.getCurrentUserRole().toUpperCase();
            }
        });
    };

    // Update user info periodically
    setInterval(updateUserInfo, 1000);
});

// Export auth manager
window.authManager = authManager;
