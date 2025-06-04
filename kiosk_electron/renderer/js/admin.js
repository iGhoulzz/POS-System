/**
 * Admin Module for POS-V2 Electron Kiosk
 * Handles admin panel functionality, reporting, menu management, and system settings
 */

class AdminManager {
    constructor() {
        this.currentTab = 'dashboard';
        this.reports = {};
        this.settings = {};
        this.init();
    }

    async init() {
        try {
            await this.loadSettings();
            this.setupEventListeners();
            this.showTab('dashboard');
            await this.loadDashboard();
        } catch (error) {
            console.error('Error initializing admin panel:', error);
            showToast('Failed to initialize admin panel', 'error');
        }
    }

    async loadSettings() {
        try {
            this.settings = {
                restaurant_name: await dbManager.getSetting('restaurant_name', 'POS-V2 Restaurant'),
                tax_rate: await dbManager.getSetting('tax_rate', 0.08),
                currency_symbol: await dbManager.getSetting('currency_symbol', '$'),
                receipt_footer: await dbManager.getSetting('receipt_footer', 'Thank you for your visit!'),
                auto_logout_minutes: await dbManager.getSetting('auto_logout_minutes', 30)
            };
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }

    setupEventListeners() {
        // Tab navigation
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('admin-tab')) {
                const tabName = e.target.dataset.tab;
                this.showTab(tabName);
            }
        });

        // Menu management
        document.addEventListener('click', async (e) => {
            if (e.target.classList.contains('add-category-btn')) {
                await this.showAddCategoryForm();
            }
            if (e.target.classList.contains('add-item-btn')) {
                await this.showAddItemForm();
            }
            if (e.target.classList.contains('edit-category-btn')) {
                const categoryId = parseInt(e.target.dataset.categoryId);
                await this.editCategory(categoryId);
            }
            if (e.target.classList.contains('edit-item-btn')) {
                const itemId = parseInt(e.target.dataset.itemId);
                await this.editMenuItem(itemId);
            }
            if (e.target.classList.contains('delete-category-btn')) {
                const categoryId = parseInt(e.target.dataset.categoryId);
                await this.deleteCategory(categoryId);
            }
            if (e.target.classList.contains('delete-item-btn')) {
                const itemId = parseInt(e.target.dataset.itemId);
                await this.deleteMenuItem(itemId);
            }
        });

        // User management
        document.addEventListener('click', async (e) => {
            if (e.target.classList.contains('add-user-btn')) {
                await this.showAddUserForm();
            }
            if (e.target.classList.contains('edit-user-btn')) {
                const userId = parseInt(e.target.dataset.userId);
                await this.editUser(userId);
            }
            if (e.target.classList.contains('toggle-user-btn')) {
                const userId = parseInt(e.target.dataset.userId);
                await this.toggleUserStatus(userId);
            }
            if (e.target.classList.contains('delete-user-btn')) {
                const userId = parseInt(e.target.dataset.userId);
                await this.deleteUser(userId);
            }
        });

        // Reports
        document.addEventListener('click', async (e) => {
            if (e.target.classList.contains('generate-report-btn')) {
                const reportType = e.target.dataset.reportType;
                await this.generateReport(reportType);
            }
            if (e.target.classList.contains('export-report-btn')) {
                const reportType = e.target.dataset.reportType;
                await this.exportReport(reportType);
            }
        });

        // Settings
        const settingsForm = document.getElementById('settings-form');
        if (settingsForm) {
            settingsForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.saveSettings();
            });
        }

        // Expenses
        document.addEventListener('click', async (e) => {
            if (e.target.classList.contains('add-expense-btn')) {
                await this.showAddExpenseForm();
            }
            if (e.target.classList.contains('edit-expense-btn')) {
                const expenseId = parseInt(e.target.dataset.expenseId);
                await this.editExpense(expenseId);
            }
            if (e.target.classList.contains('delete-expense-btn')) {
                const expenseId = parseInt(e.target.dataset.expenseId);
                await this.deleteExpense(expenseId);
            }
        });
    }

    showTab(tabName) {
        // Update active tab
        document.querySelectorAll('.admin-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Hide all tab contents
        document.querySelectorAll('.admin-tab-content').forEach(content => {
            content.classList.add('hidden');
        });

        // Show selected tab content
        const tabContent = document.getElementById(`${tabName}-tab`);
        if (tabContent) {
            tabContent.classList.remove('hidden');
            this.currentTab = tabName;
            this.initializeTab(tabName);
        }
    }

    async initializeTab(tabName) {
        switch (tabName) {
            case 'dashboard':
                await this.loadDashboard();
                break;
            case 'menu':
                await this.loadMenuManagement();
                break;
            case 'users':
                await this.loadUserManagement();
                break;
            case 'reports':
                await this.loadReports();
                break;
            case 'expenses':
                await this.loadExpenses();
                break;
            case 'settings':
                await this.loadSettingsTab();
                break;
        }
    }

    async loadDashboard() {
        try {
            showLoading('Loading dashboard...');

            // Get today's statistics
            const today = new Date();
            const startOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate());
            const endOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate(), 23, 59, 59);

            const todayReport = await dbManager.getSalesReport(startOfDay, endOfDay);
            const allOrders = await dbManager.getOrdersWithItems();
            const pendingOrders = allOrders.filter(o => ['pending', 'preparing'].includes(o.status));

            // Update dashboard widgets
            this.updateDashboardWidget('total-sales-today', formatCurrency(todayReport.totalSales));
            this.updateDashboardWidget('orders-today', todayReport.totalOrders);
            this.updateDashboardWidget('pending-orders', pendingOrders.length);
            this.updateDashboardWidget('avg-order-value', formatCurrency(todayReport.averageOrderValue));

            // Load recent orders
            await this.loadRecentOrders();

            // Load top selling items
            await this.loadTopSellingItems(todayReport.itemsSold);

            hideLoading();
        } catch (error) {
            hideLoading();
            console.error('Error loading dashboard:', error);
            showToast('Failed to load dashboard', 'error');
        }
    }

    updateDashboardWidget(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    async loadRecentOrders() {
        try {
            const orders = await dbManager.getOrdersWithItems();
            const recentOrders = orders
                .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                .slice(0, 10);

            const container = document.getElementById('recent-orders-list');
            if (!container) return;

            container.innerHTML = '';

            recentOrders.forEach(order => {
                const orderElement = document.createElement('div');
                orderElement.className = 'recent-order-item';
                orderElement.innerHTML = `
                    <div class="order-info">
                        <span class="order-number">#${order.order_number || order.id}</span>
                        <span class="order-customer">${order.customer_name || 'Walk-in'}</span>
                    </div>
                    <div class="order-meta">
                        <span class="order-total">${formatCurrency(order.total)}</span>
                        <span class="order-status status-${order.status}">${order.status}</span>
                    </div>
                `;
                container.appendChild(orderElement);
            });
        } catch (error) {
            console.error('Error loading recent orders:', error);
        }
    }

    async loadTopSellingItems(itemsSold) {
        try {
            const container = document.getElementById('top-items-list');
            if (!container) return;

            container.innerHTML = '';

            const sortedItems = Object.entries(itemsSold)
                .sort((a, b) => b[1].quantity - a[1].quantity)
                .slice(0, 5);

            sortedItems.forEach(([itemName, data]) => {
                const itemElement = document.createElement('div');
                itemElement.className = 'top-item';
                itemElement.innerHTML = `
                    <div class="item-info">
                        <span class="item-name">${itemName}</span>
                        <span class="item-quantity">×${data.quantity}</span>
                    </div>
                    <div class="item-revenue">${formatCurrency(data.revenue)}</div>
                `;
                container.appendChild(itemElement);
            });
        } catch (error) {
            console.error('Error loading top selling items:', error);
        }
    }

    async loadMenuManagement() {
        try {
            authManager.requirePermission('manage_menu');
            
            showLoading('Loading menu...');

            const categories = await dbManager.getAll('categories');
            const menuItems = await dbManager.getAll('menu_items');

            this.renderCategories(categories);
            this.renderMenuItems(menuItems, categories);

            hideLoading();
        } catch (error) {
            hideLoading();
            console.error('Error loading menu management:', error);
            showToast('Failed to load menu', 'error');
        }
    }

    renderCategories(categories) {
        const container = document.getElementById('categories-list');
        if (!container) return;

        container.innerHTML = '';

        categories.forEach(category => {
            const categoryElement = document.createElement('div');
            categoryElement.className = 'category-item';
            categoryElement.innerHTML = `
                <div class="category-info">
                    <h4>${category.name}</h4>
                    <p>${category.description || ''}</p>
                </div>
                <div class="category-actions">
                    <button class="btn-primary edit-category-btn" data-category-id="${category.id}">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn-danger delete-category-btn" data-category-id="${category.id}">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            `;
            container.appendChild(categoryElement);
        });
    }

    renderMenuItems(menuItems, categories) {
        const container = document.getElementById('menu-items-list');
        if (!container) return;

        container.innerHTML = '';

        menuItems.forEach(item => {
            const category = categories.find(c => c.id === item.category_id);
            const itemElement = document.createElement('div');
            itemElement.className = `menu-item ${item.available ? 'available' : 'unavailable'}`;
            itemElement.innerHTML = `
                <div class="item-image">
                    ${item.image_path ? 
                        `<img src="${item.image_path}" alt="${item.name}">` : 
                        '<i class="fas fa-utensils"></i>'
                    }
                </div>
                <div class="item-info">
                    <h4>${item.name}</h4>
                    <p>${item.description || ''}</p>
                    <div class="item-meta">
                        <span class="item-category">${category ? category.name : 'Unknown'}</span>
                        <span class="item-price">${formatCurrency(item.price)}</span>
                        <span class="item-status ${item.available ? 'available' : 'unavailable'}">
                            ${item.available ? 'Available' : 'Unavailable'}
                        </span>
                    </div>
                </div>
                <div class="item-actions">
                    <button class="btn-primary edit-item-btn" data-item-id="${item.id}">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn-danger delete-item-btn" data-item-id="${item.id}">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            `;
            container.appendChild(itemElement);
        });
    }

    async loadUserManagement() {
        try {
            authManager.requirePermission('manage_users');
            
            showLoading('Loading users...');

            const users = await authManager.getAllUsers();
            this.renderUsers(users);

            hideLoading();
        } catch (error) {
            hideLoading();
            console.error('Error loading user management:', error);
            showToast('Failed to load users', 'error');
        }
    }

    renderUsers(users) {
        const container = document.getElementById('users-list');
        if (!container) return;

        container.innerHTML = '';

        users.forEach(user => {
            const userElement = document.createElement('div');
            userElement.className = `user-item ${user.active ? 'active' : 'inactive'}`;
            userElement.innerHTML = `
                <div class="user-info">
                    <h4>${user.full_name}</h4>
                    <p>@${user.username}</p>
                    <div class="user-meta">
                        <span class="user-role role-${user.role}">${user.role.toUpperCase()}</span>
                        <span class="user-status ${user.active ? 'active' : 'inactive'}">
                            ${user.active ? 'Active' : 'Inactive'}
                        </span>
                    </div>
                </div>
                <div class="user-actions">
                    <button class="btn-primary edit-user-btn" data-user-id="${user.id}">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn-secondary toggle-user-btn" data-user-id="${user.id}">
                        <i class="fas fa-power-off"></i> 
                        ${user.active ? 'Deactivate' : 'Activate'}
                    </button>
                    <button class="btn-danger delete-user-btn" data-user-id="${user.id}">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            `;
            container.appendChild(userElement);
        });
    }

    async loadReports() {
        try {
            authManager.requirePermission('view_reports');
            
            // Load default reports for current month
            const now = new Date();
            const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
            const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0);

            await this.generateReport('monthly', startOfMonth, endOfMonth);
        } catch (error) {
            console.error('Error loading reports:', error);
            showToast('Failed to load reports', 'error');
        }
    }

    async generateReport(type, startDate = null, endDate = null) {
        try {
            showLoading('Generating report...');

            // Set default date ranges if not provided
            const now = new Date();
            if (!startDate || !endDate) {
                switch (type) {
                    case 'daily':
                        startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                        endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);
                        break;
                    case 'weekly':
                        const weekStart = new Date(now);
                        weekStart.setDate(now.getDate() - now.getDay());
                        startDate = weekStart;
                        endDate = new Date(weekStart);
                        endDate.setDate(weekStart.getDate() + 6);
                        break;
                    case 'monthly':
                        startDate = new Date(now.getFullYear(), now.getMonth(), 1);
                        endDate = new Date(now.getFullYear(), now.getMonth() + 1, 0);
                        break;
                }
            }

            const report = await dbManager.getSalesReport(startDate, endDate);
            this.reports[type] = { ...report, startDate, endDate };

            this.renderReport(type, this.reports[type]);
            hideLoading();
            showToast('Report generated successfully', 'success');

        } catch (error) {
            hideLoading();
            console.error('Error generating report:', error);
            showToast('Failed to generate report', 'error');
        }
    }

    renderReport(type, report) {
        const container = document.getElementById(`${type}-report-content`);
        if (!container) return;

        container.innerHTML = `
            <div class="report-summary">
                <div class="report-stat">
                    <h3>Total Sales</h3>
                    <div class="stat-value">${formatCurrency(report.totalSales)}</div>
                </div>
                <div class="report-stat">
                    <h3>Total Orders</h3>
                    <div class="stat-value">${report.totalOrders}</div>
                </div>
                <div class="report-stat">
                    <h3>Average Order</h3>
                    <div class="stat-value">${formatCurrency(report.averageOrderValue)}</div>
                </div>
            </div>

            <div class="report-details">
                <h3>Top Selling Items</h3>
                <div class="top-items-report">
                    ${Object.entries(report.itemsSold)
                        .sort((a, b) => b[1].quantity - a[1].quantity)
                        .slice(0, 10)
                        .map(([itemName, data]) => `
                            <div class="report-item">
                                <span class="item-name">${itemName}</span>
                                <span class="item-qty">×${data.quantity}</span>
                                <span class="item-revenue">${formatCurrency(data.revenue)}</span>
                            </div>
                        `).join('')}
                </div>
            </div>

            <div class="report-actions">
                <button class="btn-primary export-report-btn" data-report-type="${type}">
                    <i class="fas fa-download"></i> Export CSV
                </button>
            </div>
        `;
    }

    async exportReport(type) {
        try {
            const report = this.reports[type];
            if (!report) {
                showToast('No report data to export', 'error');
                return;
            }

            // Create CSV content
            let csvContent = 'Item Name,Quantity Sold,Revenue\n';
            Object.entries(report.itemsSold).forEach(([itemName, data]) => {
                csvContent += `"${itemName}",${data.quantity},${data.revenue}\n`;
            });

            // Download CSV
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${type}-report-${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            showToast('Report exported successfully', 'success');

        } catch (error) {
            console.error('Error exporting report:', error);
            showToast('Failed to export report', 'error');
        }
    }

    async loadExpenses() {
        try {
            authManager.requirePermission('manage_expenses');
            
            showLoading('Loading expenses...');

            const expenses = await dbManager.getAll('expenses');
            this.renderExpenses(expenses);

            hideLoading();
        } catch (error) {
            hideLoading();
            console.error('Error loading expenses:', error);
            showToast('Failed to load expenses', 'error');
        }
    }

    renderExpenses(expenses) {
        const container = document.getElementById('expenses-list');
        if (!container) return;

        container.innerHTML = '';

        expenses
            .sort((a, b) => new Date(b.date) - new Date(a.date))
            .forEach(expense => {
                const expenseElement = document.createElement('div');
                expenseElement.className = 'expense-item';
                expenseElement.innerHTML = `
                    <div class="expense-info">
                        <h4>${expense.description}</h4>
                        <div class="expense-meta">
                            <span class="expense-category">${expense.category}</span>
                            <span class="expense-date">${new Date(expense.date).toLocaleDateString()}</span>
                        </div>
                    </div>
                    <div class="expense-amount">${formatCurrency(expense.amount)}</div>
                    <div class="expense-actions">
                        <button class="btn-primary edit-expense-btn" data-expense-id="${expense.id}">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="btn-danger delete-expense-btn" data-expense-id="${expense.id}">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                `;
                container.appendChild(expenseElement);
            });
    }

    async loadSettingsTab() {
        try {
            const form = document.getElementById('settings-form');
            if (!form) return;

            // Populate form with current settings
            form.querySelector('[name="restaurant_name"]').value = this.settings.restaurant_name;
            form.querySelector('[name="tax_rate"]').value = this.settings.tax_rate;
            form.querySelector('[name="currency_symbol"]').value = this.settings.currency_symbol;
            form.querySelector('[name="receipt_footer"]').value = this.settings.receipt_footer;
            form.querySelector('[name="auto_logout_minutes"]').value = this.settings.auto_logout_minutes;

        } catch (error) {
            console.error('Error loading settings tab:', error);
        }
    }

    async saveSettings() {
        try {
            showLoading('Saving settings...');

            const form = document.getElementById('settings-form');
            const formData = new FormData(form);

            for (const [key, value] of formData.entries()) {
                await dbManager.setSetting(key, value);
                this.settings[key] = value;
            }

            hideLoading();
            showToast('Settings saved successfully', 'success');

        } catch (error) {
            hideLoading();
            console.error('Error saving settings:', error);
            showToast('Failed to save settings', 'error');
        }
    }

    // Form handlers for adding/editing entities
    async showAddCategoryForm() {
        // Implementation would show a modal form for adding categories
        showModal('add-category-modal');
    }

    async showAddItemForm() {
        // Implementation would show a modal form for adding menu items
        showModal('add-item-modal');
    }

    async showAddUserForm() {
        // Implementation would show a modal form for adding users
        showModal('add-user-modal');
    }

    async showAddExpenseForm() {
        // Implementation would show a modal form for adding expenses
        showModal('add-expense-modal');
    }

    // Get admin statistics
    getAdminStats() {
        return {
            currentTab: this.currentTab,
            hasPermissions: {
                manageMenu: authManager.hasPermission('manage_menu'),
                manageUsers: authManager.hasPermission('manage_users'),
                viewReports: authManager.hasPermission('view_reports'),
                manageExpenses: authManager.hasPermission('manage_expenses')
            }
        };
    }
}

// Initialize admin manager
const adminManager = new AdminManager();

// Export admin manager
window.adminManager = adminManager;
