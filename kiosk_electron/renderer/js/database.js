/**
 * Database Module for POS-V2 Electron Kiosk
 * Handles all database operations and local storage
 */

class DatabaseManager {
    constructor() {
        this.dbName = 'pos_v2_db';
        this.version = 1;
        this.db = null;
        this.init();
    }

    async init() {
        try {
            // Initialize IndexedDB for local storage
            const request = indexedDB.open(this.dbName, this.version);
            
            request.onerror = () => {
                console.error('Database failed to open');
                showToast('Database connection failed', 'error');
            };

            request.onsuccess = () => {
                this.db = request.result;
                console.log('Database opened successfully');
            };

            request.onupgradeneeded = (e) => {
                this.db = e.target.result;
                this.createTables();
            };
        } catch (error) {
            console.error('Database initialization error:', error);
            showToast('Failed to initialize database', 'error');
        }
    }

    createTables() {
        // Users table
        if (!this.db.objectStoreNames.contains('users')) {
            const userStore = this.db.createObjectStore('users', { keyPath: 'id', autoIncrement: true });
            userStore.createIndex('username', 'username', { unique: true });
            userStore.createIndex('role', 'role', { unique: false });
        }

        // Categories table
        if (!this.db.objectStoreNames.contains('categories')) {
            const categoryStore = this.db.createObjectStore('categories', { keyPath: 'id', autoIncrement: true });
            categoryStore.createIndex('name', 'name', { unique: true });
        }

        // Menu items table
        if (!this.db.objectStoreNames.contains('menu_items')) {
            const menuStore = this.db.createObjectStore('menu_items', { keyPath: 'id', autoIncrement: true });
            menuStore.createIndex('category_id', 'category_id', { unique: false });
            menuStore.createIndex('name', 'name', { unique: false });
        }

        // Orders table
        if (!this.db.objectStoreNames.contains('orders')) {
            const orderStore = this.db.createObjectStore('orders', { keyPath: 'id', autoIncrement: true });
            orderStore.createIndex('status', 'status', { unique: false });
            orderStore.createIndex('created_at', 'created_at', { unique: false });
        }

        // Order items table
        if (!this.db.objectStoreNames.contains('order_items')) {
            const orderItemStore = this.db.createObjectStore('order_items', { keyPath: 'id', autoIncrement: true });
            orderItemStore.createIndex('order_id', 'order_id', { unique: false });
        }

        // Expenses table
        if (!this.db.objectStoreNames.contains('expenses')) {
            const expenseStore = this.db.createObjectStore('expenses', { keyPath: 'id', autoIncrement: true });
            expenseStore.createIndex('date', 'date', { unique: false });
            expenseStore.createIndex('category', 'category', { unique: false });
        }

        // Settings table
        if (!this.db.objectStoreNames.contains('settings')) {
            const settingsStore = this.db.createObjectStore('settings', { keyPath: 'key' });
        }

        // Session storage for cart and current user
        if (!this.db.objectStoreNames.contains('session')) {
            this.db.createObjectStore('session', { keyPath: 'key' });
        }
    }

    // Generic CRUD operations
    async create(tableName, data) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([tableName], 'readwrite');
            const store = transaction.objectStore(tableName);
            
            data.created_at = new Date().toISOString();
            data.updated_at = new Date().toISOString();
            
            const request = store.add(data);
            
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async read(tableName, id) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([tableName], 'readonly');
            const store = transaction.objectStore(tableName);
            const request = store.get(id);
            
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async update(tableName, data) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([tableName], 'readwrite');
            const store = transaction.objectStore(tableName);
            
            data.updated_at = new Date().toISOString();
            
            const request = store.put(data);
            
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async delete(tableName, id) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([tableName], 'readwrite');
            const store = transaction.objectStore(tableName);
            const request = store.delete(id);
            
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async getAll(tableName, indexName = null, value = null) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([tableName], 'readonly');
            const store = transaction.objectStore(tableName);
            
            let request;
            if (indexName && value !== null) {
                const index = store.index(indexName);
                request = index.getAll(value);
            } else {
                request = store.getAll();
            }
            
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    // User operations
    async createUser(userData) {
        try {
            userData.password = await this.hashPassword(userData.password);
            return await this.create('users', userData);
        } catch (error) {
            console.error('Error creating user:', error);
            throw error;
        }
    }

    async getUserByUsername(username) {
        try {
            const users = await this.getAll('users', 'username', username);
            return users.length > 0 ? users[0] : null;
        } catch (error) {
            console.error('Error getting user by username:', error);
            throw error;
        }
    }

    async validateUser(username, password) {
        try {
            const user = await this.getUserByUsername(username);
            if (!user) return null;
            
            const hashedPassword = await this.hashPassword(password);
            return user.password === hashedPassword ? user : null;
        } catch (error) {
            console.error('Error validating user:', error);
            throw error;
        }
    }

    async hashPassword(password) {
        const encoder = new TextEncoder();
        const data = encoder.encode(password);
        const hash = await crypto.subtle.digest('SHA-256', data);
        return Array.from(new Uint8Array(hash))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    }

    // Menu operations
    async getMenuByCategory() {
        try {
            const categories = await this.getAll('categories');
            const menuItems = await this.getAll('menu_items');
            
            const menuByCategory = {};
            
            categories.forEach(category => {
                menuByCategory[category.id] = {
                    ...category,
                    items: menuItems.filter(item => item.category_id === category.id && item.available)
                };
            });
            
            return menuByCategory;
        } catch (error) {
            console.error('Error getting menu by category:', error);
            throw error;
        }
    }

    // Order operations
    async createOrder(orderData) {
        try {
            orderData.status = 'pending';
            orderData.order_number = await this.generateOrderNumber();
            const orderId = await this.create('orders', orderData);
            
            // Create order items
            for (const item of orderData.items) {
                await this.create('order_items', {
                    order_id: orderId,
                    menu_item_id: item.id,
                    quantity: item.quantity,
                    price: item.price,
                    notes: item.notes || ''
                });
            }
            
            return orderId;
        } catch (error) {
            console.error('Error creating order:', error);
            throw error;
        }
    }

    async updateOrderStatus(orderId, status) {
        try {
            const order = await this.read('orders', orderId);
            if (order) {
                order.status = status;
                if (status === 'completed') {
                    order.completed_at = new Date().toISOString();
                }
                return await this.update('orders', order);
            }
        } catch (error) {
            console.error('Error updating order status:', error);
            throw error;
        }
    }

    async getOrdersWithItems(status = null) {
        try {
            let orders;
            if (status) {
                orders = await this.getAll('orders', 'status', status);
            } else {
                orders = await this.getAll('orders');
            }
            
            // Get order items for each order
            for (const order of orders) {
                const orderItems = await this.getAll('order_items', 'order_id', order.id);
                
                // Get menu item details for each order item
                for (const item of orderItems) {
                    const menuItem = await this.read('menu_items', item.menu_item_id);
                    item.menu_item = menuItem;
                }
                
                order.items = orderItems;
            }
            
            return orders;
        } catch (error) {
            console.error('Error getting orders with items:', error);
            throw error;
        }
    }

    async generateOrderNumber() {
        try {
            const today = new Date();
            const dateStr = today.toISOString().split('T')[0].replace(/-/g, '');
            
            // Get today's orders to determine next number
            const todayOrders = await this.getOrdersByDate(today);
            const orderCount = todayOrders.length + 1;
            
            return `${dateStr}-${orderCount.toString().padStart(3, '0')}`;
        } catch (error) {
            console.error('Error generating order number:', error);
            return `${Date.now()}`;
        }
    }

    async getOrdersByDate(date) {
        try {
            const orders = await this.getAll('orders');
            const dateStr = date.toISOString().split('T')[0];
            
            return orders.filter(order => {
                const orderDate = new Date(order.created_at).toISOString().split('T')[0];
                return orderDate === dateStr;
            });
        } catch (error) {
            console.error('Error getting orders by date:', error);
            throw error;
        }
    }

    // Settings operations
    async getSetting(key, defaultValue = null) {
        try {
            const setting = await this.read('settings', key);
            return setting ? setting.value : defaultValue;
        } catch (error) {
            console.error('Error getting setting:', error);
            return defaultValue;
        }
    }

    async setSetting(key, value) {
        try {
            return await this.update('settings', { key, value });
        } catch (error) {
            console.error('Error setting value:', error);
            throw error;
        }
    }

    // Session operations
    async setSession(key, value) {
        try {
            return await this.update('session', { key, value });
        } catch (error) {
            console.error('Error setting session:', error);
            throw error;
        }
    }

    async getSession(key) {
        try {
            const session = await this.read('session', key);
            return session ? session.value : null;
        } catch (error) {
            console.error('Error getting session:', error);
            return null;
        }
    }

    async clearSession() {
        try {
            const transaction = this.db.transaction(['session'], 'readwrite');
            const store = transaction.objectStore('session');
            return store.clear();
        } catch (error) {
            console.error('Error clearing session:', error);
            throw error;
        }
    }

    // Reporting operations
    async getSalesReport(startDate, endDate) {
        try {
            const orders = await this.getOrdersWithItems('completed');
            
            const filteredOrders = orders.filter(order => {
                const orderDate = new Date(order.completed_at);
                return orderDate >= startDate && orderDate <= endDate;
            });
            
            let totalSales = 0;
            let totalOrders = filteredOrders.length;
            const itemsSold = {};
            
            filteredOrders.forEach(order => {
                totalSales += order.total;
                
                order.items.forEach(item => {
                    const itemName = item.menu_item.name;
                    if (!itemsSold[itemName]) {
                        itemsSold[itemName] = { quantity: 0, revenue: 0 };
                    }
                    itemsSold[itemName].quantity += item.quantity;
                    itemsSold[itemName].revenue += item.price * item.quantity;
                });
            });
            
            return {
                totalSales,
                totalOrders,
                averageOrderValue: totalOrders > 0 ? totalSales / totalOrders : 0,
                itemsSold,
                orders: filteredOrders
            };
        } catch (error) {
            console.error('Error generating sales report:', error);
            throw error;
        }
    }

    // Initialize default data
    async initializeDefaultData() {
        try {
            // Check if data already exists
            const users = await this.getAll('users');
            if (users.length > 0) return;

            // Create default admin user
            await this.createUser({
                username: 'admin',
                password: 'admin123',
                full_name: 'Administrator',
                role: 'admin',
                active: true
            });

            // Create default categories
            const beverageCategory = await this.create('categories', {
                name: 'Beverages',
                description: 'Hot and cold drinks'
            });

            const foodCategory = await this.create('categories', {
                name: 'Food',
                description: 'Main dishes and snacks'
            });

            // Create default menu items
            await this.create('menu_items', {
                name: 'Coffee',
                description: 'Freshly brewed coffee',
                price: 2.50,
                category_id: beverageCategory,
                available: true,
                image_path: ''
            });

            await this.create('menu_items', {
                name: 'Tea',
                description: 'Premium tea selection',
                price: 2.00,
                category_id: beverageCategory,
                available: true,
                image_path: ''
            });

            await this.create('menu_items', {
                name: 'Sandwich',
                description: 'Fresh sandwich with your choice of filling',
                price: 5.99,
                category_id: foodCategory,
                available: true,
                image_path: ''
            });

            // Initialize default settings
            await this.setSetting('restaurant_name', 'POS-V2 Restaurant');
            await this.setSetting('tax_rate', 0.08);
            await this.setSetting('currency_symbol', '$');
            await this.setSetting('receipt_footer', 'Thank you for your visit!');
            await this.setSetting('auto_logout_minutes', 30);

            console.log('Default data initialized successfully');
            showToast('System initialized with default data', 'success');
        } catch (error) {
            console.error('Error initializing default data:', error);
            showToast('Failed to initialize default data', 'error');
        }
    }
}

// Export database manager instance
const dbManager = new DatabaseManager();

// Initialize default data after database is ready
setTimeout(() => {
    if (dbManager.db) {
        dbManager.initializeDefaultData();
    }
}, 1000);
