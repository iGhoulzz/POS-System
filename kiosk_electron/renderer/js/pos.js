/**
 * POS (Point of Sale) Module for POS-V2 Electron Kiosk
 * Handles order processing, cart management, and payment
 */

class POSManager {
    constructor() {
        this.cart = [];
        this.menu = {};
        this.categories = [];
        this.currentCategory = null;
        this.taxRate = 0.08;
        this.init();
    }

    async init() {
        try {
            await this.loadMenu();
            await this.loadSettings();
            await this.loadCart();
            this.setupEventListeners();
            this.renderCategories();
            this.renderCart();
            this.updateTotals();
        } catch (error) {
            console.error('Error initializing POS:', error);
            showToast('Failed to initialize POS system', 'error');
        }
    }

    async loadMenu() {
        try {
            this.menu = await dbManager.getMenuByCategory();
            this.categories = Object.values(this.menu);
            
            if (this.categories.length > 0 && !this.currentCategory) {
                this.currentCategory = this.categories[0].id;
            }
        } catch (error) {
            console.error('Error loading menu:', error);
            throw error;
        }
    }

    async loadSettings() {
        try {
            this.taxRate = await dbManager.getSetting('tax_rate', 0.08);
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }

    async loadCart() {
        try {
            const savedCart = await dbManager.getSession('cart');
            if (savedCart && Array.isArray(savedCart)) {
                this.cart = savedCart;
            }
        } catch (error) {
            console.error('Error loading cart:', error);
        }
    }

    async saveCart() {
        try {
            await dbManager.setSession('cart', this.cart);
        } catch (error) {
            console.error('Error saving cart:', error);
        }
    }

    setupEventListeners() {
        // Category buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('category-btn')) {
                const categoryId = parseInt(e.target.dataset.categoryId);
                this.selectCategory(categoryId);
            }
        });

        // Menu item buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('menu-item-btn')) {
                const itemId = parseInt(e.target.dataset.itemId);
                this.addToCart(itemId);
            }
        });

        // Cart item quantity controls
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('qty-increase')) {
                const index = parseInt(e.target.dataset.index);
                this.updateCartItemQuantity(index, 1);
            }
            
            if (e.target.classList.contains('qty-decrease')) {
                const index = parseInt(e.target.dataset.index);
                this.updateCartItemQuantity(index, -1);
            }
            
            if (e.target.classList.contains('remove-item')) {
                const index = parseInt(e.target.dataset.index);
                this.removeFromCart(index);
            }
        });

        // Checkout button
        const checkoutBtn = document.getElementById('checkout-btn');
        if (checkoutBtn) {
            checkoutBtn.addEventListener('click', () => this.checkout());
        }

        // Clear cart button
        const clearCartBtn = document.getElementById('clear-cart-btn');
        if (clearCartBtn) {
            clearCartBtn.addEventListener('click', () => this.clearCart());
        }

        // Payment method buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('payment-method-btn')) {
                const method = e.target.dataset.method;
                this.processPayment(method);
            }
        });
    }

    selectCategory(categoryId) {
        this.currentCategory = categoryId;
        this.renderMenuItems();
        
        // Update active category button
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeBtn = document.querySelector(`[data-category-id="${categoryId}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
    }

    renderCategories() {
        const container = document.getElementById('categories-container');
        if (!container) return;

        container.innerHTML = '';

        this.categories.forEach(category => {
            const button = document.createElement('button');
            button.className = `category-btn ${category.id === this.currentCategory ? 'active' : ''}`;
            button.dataset.categoryId = category.id;
            button.innerHTML = `
                <i class="fas fa-folder"></i>
                <span>${category.name}</span>
            `;
            container.appendChild(button);
        });

        // Render initial menu items
        if (this.currentCategory) {
            this.renderMenuItems();
        }
    }

    renderMenuItems() {
        const container = document.getElementById('menu-items-container');
        if (!container) return;

        container.innerHTML = '';

        const category = this.menu[this.currentCategory];
        if (!category || !category.items) return;

        category.items.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = 'menu-item-card';
            itemElement.innerHTML = `
                <div class="menu-item-image">
                    ${item.image_path ? 
                        `<img src="${item.image_path}" alt="${item.name}">` : 
                        '<i class="fas fa-utensils"></i>'
                    }
                </div>
                <div class="menu-item-details">
                    <h3>${item.name}</h3>
                    <p class="description">${item.description || ''}</p>
                    <div class="price-section">
                        <span class="price">${formatCurrency(item.price)}</span>
                        <button class="menu-item-btn btn-primary" data-item-id="${item.id}">
                            <i class="fas fa-plus"></i> Add
                        </button>
                    </div>
                </div>
            `;
            container.appendChild(itemElement);
        });
    }

    addToCart(itemId) {
        try {
            // Find the item in the menu
            let item = null;
            for (const category of Object.values(this.menu)) {
                item = category.items.find(i => i.id === itemId);
                if (item) break;
            }

            if (!item) {
                showToast('Item not found', 'error');
                return;
            }

            // Check if item already in cart
            const existingIndex = this.cart.findIndex(cartItem => cartItem.id === itemId);
            
            if (existingIndex >= 0) {
                this.cart[existingIndex].quantity += 1;
            } else {
                this.cart.push({
                    ...item,
                    quantity: 1,
                    notes: ''
                });
            }

            this.saveCart();
            this.renderCart();
            this.updateTotals();
            
            showToast(`${item.name} added to cart`, 'success');
        } catch (error) {
            console.error('Error adding item to cart:', error);
            showToast('Failed to add item to cart', 'error');
        }
    }

    updateCartItemQuantity(index, change) {
        if (index < 0 || index >= this.cart.length) return;

        this.cart[index].quantity += change;

        if (this.cart[index].quantity <= 0) {
            this.removeFromCart(index);
            return;
        }

        this.saveCart();
        this.renderCart();
        this.updateTotals();
    }

    removeFromCart(index) {
        if (index < 0 || index >= this.cart.length) return;

        const item = this.cart[index];
        this.cart.splice(index, 1);

        this.saveCart();
        this.renderCart();
        this.updateTotals();
        
        showToast(`${item.name} removed from cart`, 'info');
    }

    clearCart() {
        if (this.cart.length === 0) {
            showToast('Cart is already empty', 'info');
            return;
        }

        const result = confirm('Are you sure you want to clear the cart?');
        if (result) {
            this.cart = [];
            this.saveCart();
            this.renderCart();
            this.updateTotals();
            showToast('Cart cleared', 'info');
        }
    }

    renderCart() {
        const container = document.getElementById('cart-items');
        if (!container) return;

        container.innerHTML = '';

        if (this.cart.length === 0) {
            container.innerHTML = `
                <div class="empty-cart">
                    <i class="fas fa-shopping-cart"></i>
                    <p>Cart is empty</p>
                </div>
            `;
            return;
        }

        this.cart.forEach((item, index) => {
            const cartItem = document.createElement('div');
            cartItem.className = 'cart-item';
            cartItem.innerHTML = `
                <div class="cart-item-info">
                    <h4>${item.name}</h4>
                    <p class="item-price">${formatCurrency(item.price)} each</p>
                    ${item.notes ? `<p class="item-notes">${item.notes}</p>` : ''}
                </div>
                <div class="cart-item-controls">
                    <div class="quantity-controls">
                        <button class="qty-decrease" data-index="${index}">
                            <i class="fas fa-minus"></i>
                        </button>
                        <span class="quantity">${item.quantity}</span>
                        <button class="qty-increase" data-index="${index}">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                    <div class="item-total">${formatCurrency(item.price * item.quantity)}</div>
                    <button class="remove-item" data-index="${index}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            container.appendChild(cartItem);
        });
    }

    updateTotals() {
        const subtotal = this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const tax = subtotal * this.taxRate;
        const total = subtotal + tax;

        // Update display elements
        const subtotalEl = document.getElementById('subtotal');
        const taxEl = document.getElementById('tax');
        const totalEl = document.getElementById('total');

        if (subtotalEl) subtotalEl.textContent = formatCurrency(subtotal);
        if (taxEl) taxEl.textContent = formatCurrency(tax);
        if (totalEl) totalEl.textContent = formatCurrency(total);

        // Enable/disable checkout button
        const checkoutBtn = document.getElementById('checkout-btn');
        if (checkoutBtn) {
            checkoutBtn.disabled = this.cart.length === 0;
        }
    }

    async checkout() {
        if (this.cart.length === 0) {
            showToast('Cart is empty', 'error');
            return;
        }

        try {
            showModal('payment-modal');
        } catch (error) {
            console.error('Error during checkout:', error);
            showToast('Checkout failed', 'error');
        }
    }

    async processPayment(method) {
        try {
            showLoading('Processing payment...');

            const subtotal = this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
            const tax = subtotal * this.taxRate;
            const total = subtotal + tax;

            // Create order data
            const orderData = {
                customer_name: 'Walk-in Customer',
                subtotal: subtotal,
                tax: tax,
                total: total,
                payment_method: method,
                cashier_id: authManager.getCurrentUser().id,
                items: this.cart.map(item => ({
                    id: item.id,
                    quantity: item.quantity,
                    price: item.price,
                    notes: item.notes
                }))
            };

            // Save order to database
            const orderId = await dbManager.createOrder(orderData);

            hideLoading();
            hideModal('payment-modal');

            // Show receipt modal
            await this.showReceipt(orderId, orderData);

            // Clear cart
            this.cart = [];
            this.saveCart();
            this.renderCart();
            this.updateTotals();

            showToast('Payment processed successfully', 'success');

        } catch (error) {
            hideLoading();
            console.error('Error processing payment:', error);
            showToast('Payment processing failed', 'error');
        }
    }

    async showReceipt(orderId, orderData) {
        const modal = document.getElementById('receipt-modal');
        if (!modal) return;

        const receiptContent = document.getElementById('receipt-content');
        if (!receiptContent) return;

        const receiptHtml = await this.generateReceiptHTML(orderId, orderData);
        receiptContent.innerHTML = receiptHtml;

        showModal('receipt-modal');

        // Setup print button
        const printBtn = document.getElementById('print-receipt-btn');
        if (printBtn) {
            printBtn.onclick = () => this.printReceipt(receiptContent);
        }
    }

    async generateReceiptHTML(orderId, orderData) {
        const restaurantName = await dbManager.getSetting('restaurant_name', 'POS-V2 Restaurant');
        const receiptFooter = await dbManager.getSetting('receipt_footer', 'Thank you for your visit!');
        
        return `
            <div class="receipt">
                <div class="receipt-header">
                    <h2>${restaurantName}</h2>
                    <p>Order #${orderData.order_number || orderId}</p>
                    <p>${new Date().toLocaleString()}</p>
                    <p>Cashier: ${authManager.getCurrentUserName()}</p>
                </div>
                
                <div class="receipt-items">
                    <table>
                        <thead>
                            <tr>
                                <th>Item</th>
                                <th>Qty</th>
                                <th>Price</th>
                                <th>Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${orderData.items.map(item => `
                                <tr>
                                    <td>${this.getItemName(item.id)}</td>
                                    <td>${item.quantity}</td>
                                    <td>${formatCurrency(item.price)}</td>
                                    <td>${formatCurrency(item.price * item.quantity)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                
                <div class="receipt-totals">
                    <div class="total-line">
                        <span>Subtotal:</span>
                        <span>${formatCurrency(orderData.subtotal)}</span>
                    </div>
                    <div class="total-line">
                        <span>Tax:</span>
                        <span>${formatCurrency(orderData.tax)}</span>
                    </div>
                    <div class="total-line total">
                        <span>Total:</span>
                        <span>${formatCurrency(orderData.total)}</span>
                    </div>
                    <div class="total-line">
                        <span>Payment Method:</span>
                        <span>${orderData.payment_method.toUpperCase()}</span>
                    </div>
                </div>
                
                <div class="receipt-footer">
                    <p>${receiptFooter}</p>
                </div>
            </div>
        `;
    }

    getItemName(itemId) {
        for (const category of Object.values(this.menu)) {
            const item = category.items.find(i => i.id === itemId);
            if (item) return item.name;
        }
        return 'Unknown Item';
    }

    printReceipt(content) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Receipt</title>
                    <style>
                        body { font-family: monospace; font-size: 12px; }
                        .receipt { max-width: 300px; margin: 0 auto; }
                        .receipt-header { text-align: center; margin-bottom: 20px; }
                        .receipt-header h2 { margin: 0; }
                        table { width: 100%; border-collapse: collapse; }
                        th, td { text-align: left; padding: 2px; }
                        .receipt-totals { margin-top: 20px; }
                        .total-line { display: flex; justify-content: space-between; }
                        .total { font-weight: bold; border-top: 1px solid #000; }
                        .receipt-footer { text-align: center; margin-top: 20px; }
                    </style>
                </head>
                <body>
                    ${content.innerHTML}
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
        printWindow.close();
    }

    // Quick access methods for specific payment types
    async payWithCash() {
        await this.processPayment('cash');
    }

    async payWithCard() {
        await this.processPayment('card');
    }

    async payWithDigital() {
        await this.processPayment('digital');
    }

    // Get current cart summary
    getCartSummary() {
        const subtotal = this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const tax = subtotal * this.taxRate;
        const total = subtotal + tax;

        return {
            itemCount: this.cart.reduce((sum, item) => sum + item.quantity, 0),
            subtotal,
            tax,
            total
        };
    }

    // Add item with custom notes
    addToCartWithNotes(itemId, notes = '') {
        this.addToCart(itemId);
        if (notes && this.cart.length > 0) {
            const lastItem = this.cart[this.cart.length - 1];
            if (lastItem.id === itemId) {
                lastItem.notes = notes;
                this.saveCart();
                this.renderCart();
            }
        }
    }
}

// Initialize POS manager
const posManager = new POSManager();

// Setup payment method event handlers
document.addEventListener('DOMContentLoaded', () => {
    // Cash payment
    const cashBtn = document.getElementById('pay-cash-btn');
    if (cashBtn) {
        cashBtn.addEventListener('click', () => posManager.payWithCash());
    }

    // Card payment
    const cardBtn = document.getElementById('pay-card-btn');
    if (cardBtn) {
        cardBtn.addEventListener('click', () => posManager.payWithCard());
    }

    // Digital payment
    const digitalBtn = document.getElementById('pay-digital-btn');
    if (digitalBtn) {
        digitalBtn.addEventListener('click', () => posManager.payWithDigital());
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Only process shortcuts if we're on the POS screen
        if (!document.getElementById('pos-screen').classList.contains('hidden')) {
            switch (e.key) {
                case 'F1':
                    e.preventDefault();
                    posManager.payWithCash();
                    break;
                case 'F2':
                    e.preventDefault();
                    posManager.payWithCard();
                    break;
                case 'F3':
                    e.preventDefault();
                    posManager.payWithDigital();
                    break;
                case 'F5':
                    e.preventDefault();
                    posManager.clearCart();
                    break;
                case 'F12':
                    e.preventDefault();
                    posManager.checkout();
                    break;
            }
        }
    });
});

// Export POS manager
window.posManager = posManager;
