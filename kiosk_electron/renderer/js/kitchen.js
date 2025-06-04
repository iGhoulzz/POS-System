/**
 * Kitchen Display Module for POS-V2 Electron Kiosk
 * Handles order display, status updates, and kitchen workflow
 */

class KitchenManager {
    constructor() {
        this.orders = [];
        this.refreshInterval = null;
        this.refreshRate = 5000; // 5 seconds
        this.statusColors = {
            pending: '#ff9800',
            preparing: '#2196f3',
            ready: '#4caf50',
            completed: '#757575'
        };
        this.init();
    }

    async init() {
        try {
            await this.loadOrders();
            this.setupEventListeners();
            this.renderOrders();
            this.startAutoRefresh();
        } catch (error) {
            console.error('Error initializing kitchen:', error);
            showToast('Failed to initialize kitchen display', 'error');
        }
    }

    async loadOrders() {
        try {
            // Load orders that are not completed
            const allOrders = await dbManager.getOrdersWithItems();
            this.orders = allOrders.filter(order => 
                ['pending', 'preparing', 'ready'].includes(order.status)
            ).sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
            
        } catch (error) {
            console.error('Error loading orders:', error);
            throw error;
        }
    }

    setupEventListeners() {
        // Order status update buttons
        document.addEventListener('click', async (e) => {
            if (e.target.classList.contains('status-btn')) {
                const orderId = parseInt(e.target.dataset.orderId);
                const newStatus = e.target.dataset.status;
                await this.updateOrderStatus(orderId, newStatus);
            }
        });

        // Refresh button
        const refreshBtn = document.getElementById('refresh-orders-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshOrders());
        }

        // Auto-refresh toggle
        const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.startAutoRefresh();
                } else {
                    this.stopAutoRefresh();
                }
            });
        }

        // Filter buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('filter-btn')) {
                const filter = e.target.dataset.filter;
                this.filterOrders(filter);
            }
        });

        // Order details modal
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('order-details-btn')) {
                const orderId = parseInt(e.target.dataset.orderId);
                this.showOrderDetails(orderId);
            }
        });
    }

    async updateOrderStatus(orderId, newStatus) {
        try {
            showLoading('Updating order status...');
            
            await dbManager.updateOrderStatus(orderId, newStatus);
            
            // Update local orders array
            const orderIndex = this.orders.findIndex(order => order.id === orderId);
            if (orderIndex >= 0) {
                this.orders[orderIndex].status = newStatus;
                
                // Remove completed orders from display
                if (newStatus === 'completed') {
                    this.orders.splice(orderIndex, 1);
                }
            }
            
            hideLoading();
            this.renderOrders();
            
            const statusMessages = {
                preparing: 'Order marked as preparing',
                ready: 'Order marked as ready',
                completed: 'Order completed'
            };
            
            showToast(statusMessages[newStatus] || 'Order status updated', 'success');
            
        } catch (error) {
            hideLoading();
            console.error('Error updating order status:', error);
            showToast('Failed to update order status', 'error');
        }
    }

    async refreshOrders() {
        try {
            showLoading('Refreshing orders...');
            await this.loadOrders();
            this.renderOrders();
            hideLoading();
            showToast('Orders refreshed', 'success');
        } catch (error) {
            hideLoading();
            console.error('Error refreshing orders:', error);
            showToast('Failed to refresh orders', 'error');
        }
    }

    startAutoRefresh() {
        this.stopAutoRefresh(); // Clear existing interval
        this.refreshInterval = setInterval(() => {
            this.loadOrders().then(() => {
                this.renderOrders();
            }).catch(error => {
                console.error('Auto-refresh error:', error);
            });
        }, this.refreshRate);
        
        console.log('Auto-refresh started');
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
            console.log('Auto-refresh stopped');
        }
    }

    filterOrders(filter) {
        // Update filter button states
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-filter="${filter}"]`).classList.add('active');

        // Apply filter and render
        this.renderOrders(filter);
    }

    renderOrders(filter = 'all') {
        const container = document.getElementById('kitchen-orders');
        if (!container) return;

        container.innerHTML = '';

        let filteredOrders = this.orders;
        if (filter !== 'all') {
            filteredOrders = this.orders.filter(order => order.status === filter);
        }

        if (filteredOrders.length === 0) {
            container.innerHTML = `
                <div class="no-orders">
                    <i class="fas fa-check-circle"></i>
                    <h3>No ${filter === 'all' ? '' : filter} orders</h3>
                    <p>All caught up! 🎉</p>
                </div>
            `;
            return;
        }

        filteredOrders.forEach(order => {
            const orderCard = this.createOrderCard(order);
            container.appendChild(orderCard);
        });

        // Update order counts
        this.updateOrderCounts();
    }

    createOrderCard(order) {
        const card = document.createElement('div');
        card.className = `order-card status-${order.status}`;
        card.style.borderLeftColor = this.statusColors[order.status];

        const orderTime = new Date(order.created_at);
        const waitTime = this.calculateWaitTime(orderTime);

        card.innerHTML = `
            <div class="order-header">
                <div class="order-info">
                    <h3>Order #${order.order_number || order.id}</h3>
                    <div class="order-meta">
                        <span class="order-time">
                            <i class="fas fa-clock"></i>
                            ${orderTime.toLocaleTimeString()}
                        </span>
                        <span class="wait-time ${waitTime > 20 ? 'urgent' : ''}">
                            <i class="fas fa-stopwatch"></i>
                            ${waitTime}m
                        </span>
                    </div>
                </div>
                <div class="order-status">
                    <span class="status-badge status-${order.status}">
                        ${order.status.toUpperCase()}
                    </span>
                </div>
            </div>

            <div class="order-items">
                ${order.items.map(item => `
                    <div class="order-item">
                        <div class="item-info">
                            <span class="item-name">${item.menu_item ? item.menu_item.name : 'Unknown Item'}</span>
                            <span class="item-quantity">×${item.quantity}</span>
                        </div>
                        ${item.notes ? `<div class="item-notes">Note: ${item.notes}</div>` : ''}
                    </div>
                `).join('')}
            </div>

            <div class="order-actions">
                ${this.renderStatusButtons(order)}
                <button class="btn-secondary order-details-btn" data-order-id="${order.id}">
                    <i class="fas fa-info-circle"></i>
                    Details
                </button>
            </div>

            <div class="order-customer">
                <i class="fas fa-user"></i>
                ${order.customer_name || 'Walk-in Customer'}
            </div>
        `;

        return card;
    }

    renderStatusButtons(order) {
        const buttons = [];
        
        switch (order.status) {
            case 'pending':
                buttons.push(`
                    <button class="btn-primary status-btn" data-order-id="${order.id}" data-status="preparing">
                        <i class="fas fa-play"></i>
                        Start Preparing
                    </button>
                `);
                break;
                
            case 'preparing':
                buttons.push(`
                    <button class="btn-success status-btn" data-order-id="${order.id}" data-status="ready">
                        <i class="fas fa-check"></i>
                        Mark Ready
                    </button>
                `);
                break;
                
            case 'ready':
                buttons.push(`
                    <button class="btn-complete status-btn" data-order-id="${order.id}" data-status="completed">
                        <i class="fas fa-hand-paper"></i>
                        Complete Order
                    </button>
                `);
                break;
        }
        
        return buttons.join('');
    }

    calculateWaitTime(orderTime) {
        const now = new Date();
        const diffInMinutes = Math.floor((now - orderTime) / (1000 * 60));
        return Math.max(0, diffInMinutes);
    }

    updateOrderCounts() {
        const counts = {
            all: this.orders.length,
            pending: this.orders.filter(o => o.status === 'pending').length,
            preparing: this.orders.filter(o => o.status === 'preparing').length,
            ready: this.orders.filter(o => o.status === 'ready').length
        };

        // Update count badges
        Object.entries(counts).forEach(([status, count]) => {
            const badge = document.querySelector(`[data-filter="${status}"] .count-badge`);
            if (badge) {
                badge.textContent = count;
                badge.style.display = count > 0 ? 'inline' : 'none';
            }
        });

        // Update main header count
        const mainCount = document.getElementById('total-orders-count');
        if (mainCount) {
            mainCount.textContent = counts.all;
        }
    }

    showOrderDetails(orderId) {
        const order = this.orders.find(o => o.id === orderId);
        if (!order) {
            showToast('Order not found', 'error');
            return;
        }

        const modal = document.getElementById('order-details-modal');
        if (!modal) return;

        const content = document.getElementById('order-details-content');
        if (!content) return;

        const orderTime = new Date(order.created_at);
        const waitTime = this.calculateWaitTime(orderTime);

        content.innerHTML = `
            <div class="order-details">
                <div class="details-header">
                    <h2>Order #${order.order_number || order.id}</h2>
                    <span class="status-badge status-${order.status}">
                        ${order.status.toUpperCase()}
                    </span>
                </div>

                <div class="details-meta">
                    <div class="meta-item">
                        <strong>Customer:</strong>
                        <span>${order.customer_name || 'Walk-in Customer'}</span>
                    </div>
                    <div class="meta-item">
                        <strong>Order Time:</strong>
                        <span>${orderTime.toLocaleString()}</span>
                    </div>
                    <div class="meta-item">
                        <strong>Wait Time:</strong>
                        <span class="${waitTime > 20 ? 'urgent' : ''}">${waitTime} minutes</span>
                    </div>
                    <div class="meta-item">
                        <strong>Total:</strong>
                        <span>${formatCurrency(order.total)}</span>
                    </div>
                </div>

                <div class="details-items">
                    <h3>Order Items</h3>
                    ${order.items.map(item => `
                        <div class="detail-item">
                            <div class="item-main">
                                <span class="item-name">${item.menu_item ? item.menu_item.name : 'Unknown Item'}</span>
                                <span class="item-quantity">×${item.quantity}</span>
                                <span class="item-price">${formatCurrency(item.price * item.quantity)}</span>
                            </div>
                            ${item.notes ? `
                                <div class="item-notes">
                                    <i class="fas fa-sticky-note"></i>
                                    ${item.notes}
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>

                <div class="details-actions">
                    ${this.renderStatusButtons(order)}
                </div>
            </div>
        `;

        showModal('order-details-modal');
    }

    // Get kitchen statistics
    getKitchenStats() {
        const stats = {
            totalOrders: this.orders.length,
            pendingOrders: this.orders.filter(o => o.status === 'pending').length,
            preparingOrders: this.orders.filter(o => o.status === 'preparing').length,
            readyOrders: this.orders.filter(o => o.status === 'ready').length,
            averageWaitTime: 0,
            urgentOrders: 0
        };

        if (this.orders.length > 0) {
            const waitTimes = this.orders.map(order => 
                this.calculateWaitTime(new Date(order.created_at))
            );
            
            stats.averageWaitTime = Math.round(
                waitTimes.reduce((sum, time) => sum + time, 0) / waitTimes.length
            );
            
            stats.urgentOrders = waitTimes.filter(time => time > 20).length;
        }

        return stats;
    }

    // Sound alerts for new orders (if enabled)
    playNewOrderAlert() {
        try {
            const audio = new Audio('/assets/sounds/new-order.mp3');
            audio.play().catch(e => console.log('Could not play sound:', e));
        } catch (error) {
            console.log('Sound not available');
        }
    }

    // Keyboard shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Only process shortcuts if we're on the kitchen screen
            if (!document.getElementById('kitchen-screen').classList.contains('hidden')) {
                switch (e.key) {
                    case 'F5':
                        e.preventDefault();
                        this.refreshOrders();
                        break;
                    case '1':
                        e.preventDefault();
                        this.filterOrders('pending');
                        break;
                    case '2':
                        e.preventDefault();
                        this.filterOrders('preparing');
                        break;
                    case '3':
                        e.preventDefault();
                        this.filterOrders('ready');
                        break;
                    case '0':
                        e.preventDefault();
                        this.filterOrders('all');
                        break;
                }
            }
        });
    }

    // Cleanup when leaving kitchen screen
    cleanup() {
        this.stopAutoRefresh();
    }
}

// Initialize kitchen manager
const kitchenManager = new KitchenManager();

// Setup keyboard shortcuts
document.addEventListener('DOMContentLoaded', () => {
    kitchenManager.setupKeyboardShortcuts();
    
    // Initialize auto-refresh toggle
    const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
    if (autoRefreshToggle) {
        autoRefreshToggle.checked = true; // Default to enabled
    }
});

// Cleanup when window is closed or user navigates away
window.addEventListener('beforeunload', () => {
    kitchenManager.cleanup();
});

// Export kitchen manager
window.kitchenManager = kitchenManager;
