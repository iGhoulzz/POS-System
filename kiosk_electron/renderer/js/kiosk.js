// Modern Kiosk Interface - Fixed Version
class KioskApp {
    constructor() {
        this.currentScreen = 'loading';
        this.orderType = null;
        this.categories = [];
        this.menuItems = [];
        this.currentCategory = null;
        this.cart = [];
        this.cartTotal = 0;
        this.isLoading = false;
        this.taxRate = 0.08; // Default, will be loaded from settings

        this.init();
    }

    async init() {
        try {
            console.log('🚀 Initializing Kiosk App...');

            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            }

            // Initialize current time display
            this.updateCurrentTime();
            setInterval(() => this.updateCurrentTime(), 1000);

            // Show loading screen
            this.showLoadingScreen();

            // Load settings (tax rate etc.)
            await this.loadSettings();

            // Load initial data
            await this.loadCategories();
            await this.loadMenuItems();

            console.log('✅ Data loaded successfully');

            // Initialize event listeners AFTER data is loaded
            this.initializeEventListeners();

            // Transition to order type screen
            setTimeout(() => {
                this.showOrderTypeScreen();
            }, 1500);

        } catch (error) {
            console.error('❌ Failed to initialize kiosk:', error);
            this.showError('Failed to initialize. Please contact staff.');
        }
    }

    initializeEventListeners() {
        console.log('🎧 Setting up event listeners...');

        // Order type selection
        document.querySelectorAll('.order-type-card').forEach(card => {
            card.addEventListener('click', (e) => {
                e.stopPropagation();
                this.selectOrderType(card.dataset.type);
            });
        });

        // Back button on dashboard
        const backBtn = document.getElementById('back-btn');
        if (backBtn) {
            backBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.showOrderTypeScreen();
            });
        }

        // Cart button
        const cartBtn = document.getElementById('cart-btn');
        if (cartBtn) {
            cartBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.showPaymentScreen();
            });
        }

        // Back button on payment screen
        const paymentBackBtn = document.getElementById('payment-back-btn');
        if (paymentBackBtn) {
            paymentBackBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.showDashboard();
            });
        }

        // Add to cart from modal
        const addToCartBtn = document.getElementById('add-to-cart-btn');
        if (addToCartBtn) {
            addToCartBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.addToCartFromModal();
            });
        }

        // Modal close button
        const modalCloseBtn = document.getElementById('modal-close-btn');
        if (modalCloseBtn) {
            modalCloseBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.closeModal();
            });
        }

        // Modal backdrop click to close
        const modal = document.getElementById('item-modal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                // Only close if clicking the backdrop itself, not content inside
                if (e.target === modal) {
                    this.closeModal();
                }
            });
        }

        // Quantity controls in modal
        const quantityMinus = document.getElementById('quantity-decrease');
        const quantityPlus = document.getElementById('quantity-increase');

        if (quantityMinus) {
            quantityMinus.addEventListener('click', (e) => {
                e.stopPropagation();
                this.adjustModalQuantity(-1);
            });
        }

        if (quantityPlus) {
            quantityPlus.addEventListener('click', (e) => {
                e.stopPropagation();
                this.adjustModalQuantity(1);
            });
        }

        // Place order button
        const placeOrderBtn = document.getElementById('place-order-btn');
        if (placeOrderBtn) {
            placeOrderBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.placeOrder();
            });
        }

        // New order button (on success screen)
        const newOrderBtn = document.getElementById('new-order-btn');
        if (newOrderBtn) {
            newOrderBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (this.countdownInterval) clearInterval(this.countdownInterval);
                this.resetKiosk();
            });
        }

        // Single delegated click handler for dynamically-created elements
        // Uses a priority-based approach to avoid conflicts
        document.addEventListener('click', (e) => {
            // Priority 1: Cart item controls (on payment screen)
            const quantityBtn = e.target.closest('.cart-item-controls .quantity-btn, .cart-item-controls .remove-btn');
            if (quantityBtn) {
                e.stopPropagation();
                const itemIndex = parseInt(quantityBtn.dataset.index);
                const action = quantityBtn.dataset.action;
                this.updateCartItemQuantity(itemIndex, action);
                return;
            }

            // Priority 2: Payment method buttons
            const paymentBtn = e.target.closest('.payment-method-btn');
            if (paymentBtn) {
                e.stopPropagation();
                this.selectPaymentMethod(paymentBtn.dataset.method);
                return;
            }

            // Priority 3: Category items (sidebar)
            const categoryItem = e.target.closest('.category-item');
            if (categoryItem && !e.target.closest('.menu-items-section')) {
                e.stopPropagation();
                this.selectCategory(categoryItem.dataset.categoryId);
                return;
            }

            // Priority 4: Menu items (grid)
            const menuItem = e.target.closest('.menu-item');
            if (menuItem) {
                e.stopPropagation();
                this.showItemDetail(menuItem.dataset.itemId);
                return;
            }
        });

        console.log('✅ All event listeners set up successfully');
    }

    // Screen Management
    showScreen(screenId) {
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.add('hidden');
        });

        const targetScreen = document.getElementById(screenId);
        if (targetScreen) {
            targetScreen.classList.remove('hidden');
            this.currentScreen = screenId;
        }
    }

    showLoadingScreen() {
        this.showScreen('loading-screen');
    }

    showOrderTypeScreen() {
        this.showScreen('order-type-screen');

        // Add entrance animation
        const cards = document.querySelectorAll('.order-type-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(50px)';
            setTimeout(() => {
                card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 200);
        });
    }

    showDashboard() {
        this.showScreen('dashboard-screen');
        this.renderCategories();
        if (this.currentCategory) {
            this.renderMenuItems(this.currentCategory);
        } else if (this.categories.length > 0) {
            this.selectCategory(this.categories[0].id);
        }
    }

    showPaymentScreen() {
        if (this.cart.length === 0) {
            this.showToast('Your cart is empty', 'error');
            return;
        }
        this.showScreen('payment-screen');
        this.renderCartItems();
        this.updatePaymentSummary();
    }

    // Order Type Selection
    selectOrderType(type) {
        this.orderType = type;

        // Update header indicator
        const icon = document.getElementById('order-type-icon');
        const text = document.getElementById('order-type-text');
        if (icon) icon.className = type === 'dine-in' ? 'fas fa-chair' : 'fas fa-shopping-bag';
        if (text) text.textContent = type === 'dine-in' ? 'Dine In' : 'Take Away';

        this.showToast(`Selected: ${type === 'dine-in' ? 'Dine In' : 'Take Away'}`);

        setTimeout(() => {
            this.showDashboard();
        }, 600);
    }

    // Data Loading
    async loadSettings() {
        try {
            if (window.electronAPI && window.electronAPI.database) {
                const settings = await window.electronAPI.database.getSettings();
                if (settings && settings.tax_rate) {
                    this.taxRate = parseFloat(settings.tax_rate);
                    console.log('📊 Tax rate loaded from DB:', this.taxRate);
                }
            }
        } catch (error) {
            console.warn('⚠️ Could not load settings, using defaults:', error);
        }
    }

    async loadCategories() {
        try {
            this.isLoading = true;

            if (window.electronAPI && window.electronAPI.database) {
                const response = await window.electronAPI.database.getCategories();
                this.categories = response || [];
            } else {
                this.categories = this.getMockCategories();
            }

            console.log('✅ Loaded categories:', this.categories.length);
        } catch (error) {
            console.error('❌ Failed to load categories:', error);
            this.categories = this.getMockCategories();
        } finally {
            this.isLoading = false;
        }
    }

    async loadMenuItems() {
        try {
            this.isLoading = true;

            if (window.electronAPI && window.electronAPI.database) {
                const response = await window.electronAPI.database.getMenuItems();
                this.menuItems = response || [];
            } else {
                this.menuItems = this.getMockMenuItems();
            }

            console.log('✅ Loaded menu items:', this.menuItems.length);
        } catch (error) {
            console.error('❌ Failed to load menu items:', error);
            this.menuItems = this.getMockMenuItems();
        } finally {
            this.isLoading = false;
        }
    }

    // Category Management
    selectCategory(categoryId) {
        this.currentCategory = categoryId;

        // Update category UI
        document.querySelectorAll('.category-item').forEach(item => {
            item.classList.remove('active');
        });

        const activeCategory = document.querySelector(`[data-category-id="${categoryId}"]`);
        if (activeCategory) {
            activeCategory.classList.add('active');
        }

        // Update category title
        const selectedCategory = this.categories.find(cat => cat.id == categoryId);
        if (selectedCategory) {
            const titleElement = document.getElementById('current-category-title');
            if (titleElement) {
                titleElement.textContent = selectedCategory.name;
            }
        }

        this.renderMenuItems(categoryId);
    }

    renderCategories() {
        const sidebar = document.getElementById('categories-list');
        if (!sidebar) return;

        const esc = (str) => Utils.sanitizeInput(String(str ?? ''));
        const categoriesHTML = this.categories.map(category => `
            <div class="category-item" data-category-id="${category.id}">
                <div class="category-icon">
                    <i class="${this.getCategoryIcon(category.name)}"></i>
                </div>
                <span class="category-name">${esc(category.name)}</span>
            </div>
        `).join('');

        sidebar.innerHTML = categoriesHTML;
    }

    renderMenuItems(categoryId) {
        const grid = document.getElementById('menu-items-grid');
        if (!grid) return;

        const categoryItems = this.menuItems.filter(item =>
            item.category_id == categoryId && (item.is_available || item.is_active)
        );

        const esc = (str) => Utils.sanitizeInput(String(str ?? ''));
        const itemsHTML = categoryItems.map(item => {
            const imageSrc = item.image_path || 'assets/images/placeholder.svg';
            return `
                <div class="menu-item" data-item-id="${item.id}">
                    <div class="menu-item-image">
                        <img src="${imageSrc}" 
                             alt="${esc(item.name)}" 
                             onerror="this.src='assets/images/placeholder.svg'">
                        <div class="item-price-badge">$${parseFloat(item.price).toFixed(2)}</div>
                    </div>
                    <div class="menu-item-content">
                        <h3 class="menu-item-title">${esc(item.name)}</h3>
                        <p class="menu-item-description">${esc(item.description || '')}</p>
                    </div>
                </div>
            `;
        }).join('');

        grid.innerHTML = itemsHTML;

        // Update items count
        const itemsCount = document.getElementById('items-count');
        if (itemsCount) {
            itemsCount.textContent = `${categoryItems.length} items`;
        }
    }

    // Item Detail Modal
    showItemDetail(itemId) {
        const item = this.menuItems.find(i => i.id == itemId);
        if (!item) return;

        const modal = document.getElementById('item-modal');
        if (!modal) return;

        // Populate modal
        const modalItemName = document.getElementById('modal-item-name');
        const modalItemImage = document.getElementById('modal-item-image');
        const modalItemDescription = document.getElementById('modal-item-description');
        const modalItemPrice = document.getElementById('modal-item-price');
        const quantityDisplay = document.getElementById('quantity-display');

        if (modalItemName) modalItemName.textContent = item.name;
        if (modalItemImage) {
            modalItemImage.src = item.image_path || 'assets/images/placeholder.svg';
            modalItemImage.alt = item.name;
            modalItemImage.onerror = function () { this.src = 'assets/images/placeholder.svg'; };
        }
        if (modalItemDescription) modalItemDescription.textContent = item.description || '';
        if (modalItemPrice) modalItemPrice.textContent = `$${parseFloat(item.price).toFixed(2)}`;
        if (quantityDisplay) quantityDisplay.textContent = '1';

        modal.dataset.itemId = itemId;
        modal.classList.remove('hidden');
    }

    adjustModalQuantity(delta) {
        const quantitySpan = document.getElementById('quantity-display');
        if (!quantitySpan) return;
        const currentQuantity = parseInt(quantitySpan.textContent);
        const newQuantity = Math.max(1, currentQuantity + delta);
        quantitySpan.textContent = newQuantity;
    }

    addToCartFromModal() {
        const modal = document.getElementById('item-modal');
        if (!modal) return;

        const itemId = modal.dataset.itemId;
        const quantityElement = document.getElementById('quantity-display');
        if (!quantityElement) return;

        const quantity = parseInt(quantityElement.textContent);
        this.addToCart(itemId, quantity);
        this.closeModal();
    }

    closeModal() {
        const modal = document.getElementById('item-modal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    // Cart Management
    addToCart(itemId, quantity = 1) {
        const item = this.menuItems.find(i => i.id == itemId);
        if (!item) return;

        const existingIndex = this.cart.findIndex(cartItem => cartItem.id == itemId);

        if (existingIndex !== -1) {
            this.cart[existingIndex].quantity += quantity;
        } else {
            this.cart.push({
                ...item,
                quantity: quantity
            });
        }

        this.updateCartUI();
        this.showToast(`${item.name} added to cart`);
    }

    updateCartItemQuantity(itemIndex, action) {
        if (itemIndex < 0 || itemIndex >= this.cart.length) return;

        if (action === 'increase') {
            this.cart[itemIndex].quantity++;
        } else if (action === 'decrease') {
            if (this.cart[itemIndex].quantity > 1) {
                this.cart[itemIndex].quantity--;
            } else {
                this.cart.splice(itemIndex, 1);
            }
        } else if (action === 'remove') {
            this.cart.splice(itemIndex, 1);
        }

        this.updateCartUI();
        if (this.currentScreen === 'payment-screen') {
            this.renderCartItems();
            this.updatePaymentSummary();
        }
    }

    updateCartUI() {
        const cartCount = this.cart.reduce((sum, item) => sum + item.quantity, 0);
        const cartTotal = this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

        const cartCountElement = document.getElementById('cart-count');
        const cartTotalElement = document.getElementById('cart-total');

        if (cartCountElement) cartCountElement.textContent = cartCount;
        if (cartTotalElement) cartTotalElement.textContent = `$${cartTotal.toFixed(2)}`;

        // Show/hide cart button
        const cartBtn = document.getElementById('cart-btn');
        if (cartBtn) {
            if (cartCount > 0) {
                cartBtn.style.transform = 'translateY(0)';
                cartBtn.style.opacity = '1';
                cartBtn.style.pointerEvents = 'auto';
            } else {
                cartBtn.style.transform = 'translateY(100px)';
                cartBtn.style.opacity = '0';
                cartBtn.style.pointerEvents = 'none';
            }
        }

        this.cartTotal = cartTotal;
    }

    renderCartItems() {
        const cartList = document.getElementById('cart-items-list');
        if (!cartList) return;

        if (this.cart.length === 0) {
            cartList.innerHTML = '<div class="empty-cart">Your cart is empty</div>';
            return;
        }

        const esc = (str) => Utils.sanitizeInput(String(str ?? ''));
        const cartHTML = this.cart.map((item, index) => `
            <div class="cart-item">
                <div class="cart-item-info">
                    <h4>${esc(item.name)}</h4>
                    <p class="cart-item-price">$${parseFloat(item.price).toFixed(2)} each</p>
                </div>
                <div class="cart-item-controls">
                    <button class="quantity-btn" data-index="${index}" data-action="decrease">
                        <i class="fas fa-minus"></i>
                    </button>
                    <span class="cart-item-quantity">${item.quantity}</span>
                    <button class="quantity-btn" data-index="${index}" data-action="increase">
                        <i class="fas fa-plus"></i>
                    </button>
                    <button class="remove-btn quantity-btn" data-index="${index}" data-action="remove">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                <div class="cart-item-total">
                    $${(item.price * item.quantity).toFixed(2)}
                </div>
            </div>
        `).join('');

        cartList.innerHTML = cartHTML;
    }

    updatePaymentSummary() {
        const subtotal = this.cartTotal;
        const tax = subtotal * this.taxRate;
        const total = subtotal + tax;

        const subtotalElement = document.getElementById('subtotal');
        const taxElement = document.getElementById('tax-amount');
        const totalElement = document.getElementById('final-total');

        if (subtotalElement) subtotalElement.textContent = `$${subtotal.toFixed(2)}`;
        if (taxElement) taxElement.textContent = `$${tax.toFixed(2)}`;
        if (totalElement) totalElement.textContent = `$${total.toFixed(2)}`;
    }

    // Payment Processing
    selectPaymentMethod(method) {
        document.querySelectorAll('.payment-method-btn').forEach(pm => {
            pm.classList.remove('selected');
        });

        const selectedMethod = document.querySelector(`[data-method="${method}"]`);
        if (selectedMethod) {
            selectedMethod.classList.add('selected');
        }

        this.selectedPaymentMethod = method;

        const placeOrderBtn = document.getElementById('place-order-btn');
        if (placeOrderBtn) {
            placeOrderBtn.disabled = false;
        }
    }

    async placeOrder() {
        if (this.cart.length === 0) {
            this.showToast('Your cart is empty', 'error');
            return;
        }

        if (!this.selectedPaymentMethod) {
            this.showToast('Please select a payment method', 'error');
            return;
        }

        try {
            const orderData = {
                order_type: this.orderType === 'dine-in' ? 'dine_in' : 'takeout',
                customer_name: 'Kiosk Customer',
                payment_method: this.selectedPaymentMethod,
                items: this.cart.map(item => ({
                    item_id: item.id,
                    name: item.name,
                    quantity: item.quantity,
                    price: item.price
                })),
                subtotal: this.cartTotal,
                tax_rate: this.taxRate,
                timestamp: new Date().toISOString()
            };

            // Show processing state
            const placeOrderBtn = document.getElementById('place-order-btn');
            if (placeOrderBtn) {
                placeOrderBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                placeOrderBtn.disabled = true;
            }

            // Actually create the order via IPC
            let result;
            if (window.electronAPI && window.electronAPI.database) {
                result = await window.electronAPI.database.createOrder(orderData);
            } else {
                // Browser fallback — simulate
                await new Promise(resolve => setTimeout(resolve, 1000));
                result = { success: true, orderNumber: 'DEMO-001' };
            }

            if (result && result.success) {
                this.showSuccessScreen(result.orderNumber);
            } else {
                throw new Error(result?.message || 'Order creation failed');
            }

        } catch (error) {
            console.error('Failed to place order:', error);
            this.showToast('Failed to place order. Please try again.', 'error');

            const placeOrderBtn = document.getElementById('place-order-btn');
            if (placeOrderBtn) {
                placeOrderBtn.innerHTML = '<i class="fas fa-check"></i> Place Order';
                placeOrderBtn.disabled = false;
            }
        }
    }

    showSuccessScreen(orderNumber) {
        // Update success screen content
        const orderIdEl = document.getElementById('success-order-id');
        if (orderIdEl) orderIdEl.textContent = orderNumber || '---';

        this.showScreen('success-screen');
        this.startCountdown(10);
    }

    startCountdown(seconds) {
        const timerEl = document.getElementById('countdown-timer');
        let remaining = seconds;
        if (timerEl) timerEl.textContent = remaining;

        if (this.countdownInterval) clearInterval(this.countdownInterval);

        this.countdownInterval = setInterval(() => {
            remaining--;
            if (timerEl) timerEl.textContent = remaining;
            if (remaining <= 0) {
                clearInterval(this.countdownInterval);
                this.countdownInterval = null;
                this.resetKiosk();
            }
        }, 1000);
    }

    resetKiosk() {
        this.cart = [];
        this.cartTotal = 0;
        this.orderType = null;
        this.currentCategory = null;
        this.selectedPaymentMethod = null;
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
            this.countdownInterval = null;
        }
        this.updateCartUI();

        // Reset place order button
        const placeOrderBtn = document.getElementById('place-order-btn');
        if (placeOrderBtn) {
            placeOrderBtn.innerHTML = '<i class="fas fa-check"></i><span>Place Order</span>';
            placeOrderBtn.disabled = false;
        }

        this.showOrderTypeScreen();
    }

    // Utility Functions
    updateCurrentTime() {
        const timeElement = document.getElementById('current-time');
        if (timeElement) {
            const now = new Date();
            timeElement.textContent = now.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
            });
        }
    }

    showToast(message, type = 'info') {
        // Remove existing notification
        const existing = document.querySelector('.kiosk-notification');
        if (existing) existing.remove();
        if (this._toastTimeout) clearTimeout(this._toastTimeout);

        // Config per type
        const config = {
            success: { icon: 'fa-check-circle', title: 'Success' },
            error: { icon: 'fa-exclamation-triangle', title: 'Error' },
            info: { icon: 'fa-info-circle', title: 'Notice' },
            warning: { icon: 'fa-exclamation-circle', title: 'Warning' }
        };
        const { icon, title } = config[type] || config.info;

        // Build notification element
        const notif = document.createElement('div');
        notif.className = `kiosk-notification ${type}`;
        const esc = (str) => Utils.sanitizeInput(String(str ?? ''));
        notif.innerHTML = `
            <div class="notif-icon"><i class="fas ${icon}"></i></div>
            <div class="notif-body">
                <div class="notif-title">${esc(title)}</div>
                <div class="notif-message">${esc(message)}</div>
            </div>
            <button class="notif-close"><i class="fas fa-times"></i></button>
            <div class="notif-progress"></div>
        `;
        document.body.appendChild(notif);

        // Close button
        notif.querySelector('.notif-close').addEventListener('click', () => {
            notif.classList.remove('show');
            setTimeout(() => notif.remove(), 500);
        });

        // Animate in
        requestAnimationFrame(() => {
            requestAnimationFrame(() => notif.classList.add('show'));
        });

        // Auto dismiss
        this._toastTimeout = setTimeout(() => {
            notif.classList.remove('show');
            setTimeout(() => notif.remove(), 500);
        }, 4000);
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    getCategoryIcon(categoryName) {
        const icons = {
            'appetizers': 'fas fa-seedling',
            'mains': 'fas fa-utensils',
            'main courses': 'fas fa-utensils',
            'desserts': 'fas fa-ice-cream',
            'beverages': 'fas fa-coffee',
            'drinks': 'fas fa-coffee',
            'salads': 'fas fa-leaf',
            'soups': 'fas fa-bowl-hot',
            'pizza': 'fas fa-pizza-slice',
            'burgers': 'fas fa-hamburger',
            'pasta': 'fas fa-wheat-awn',
            'seafood': 'fas fa-fish',
            'sandwiches': 'fas fa-bread-slice',
            'breakfast': 'fas fa-egg',
            'sides': 'fas fa-french-fries'
        };

        const key = categoryName.toLowerCase();
        return icons[key] || 'fas fa-utensils';
    }

    // Mock data for browser fallback only
    getMockCategories() {
        return [
            { id: 1, name: 'Appetizers' },
            { id: 2, name: 'Mains' },
            { id: 3, name: 'Desserts' },
            { id: 4, name: 'Beverages' }
        ];
    }

    getMockMenuItems() {
        return [
            { id: 1, name: 'Caesar Salad', price: 12.99, category_id: 1, is_available: true, description: 'Fresh romaine lettuce with caesar dressing' },
            { id: 2, name: 'Grilled Chicken', price: 18.99, category_id: 2, is_available: true, description: 'Tender grilled chicken breast' },
            { id: 3, name: 'Chocolate Cake', price: 8.99, category_id: 3, is_available: true, description: 'Rich chocolate cake with cream' },
            { id: 4, name: 'Coffee', price: 3.99, category_id: 4, is_available: true, description: 'Fresh brewed coffee' },
            { id: 5, name: 'Garlic Bread', price: 6.99, category_id: 1, is_available: true, description: 'Crispy bread with garlic butter' },
            { id: 6, name: 'Beef Steak', price: 24.99, category_id: 2, is_available: true, description: 'Juicy beef steak cooked to perfection' }
        ];
    }
}

// Initialize the kiosk app ONCE when DOM is loaded
let kioskInitialized = false;

function initKiosk() {
    if (kioskInitialized) return;
    kioskInitialized = true;
    console.log('🎯 Initializing Kiosk Interface...');
    window.kioskApp = new KioskApp();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initKiosk);
} else {
    initKiosk();
}