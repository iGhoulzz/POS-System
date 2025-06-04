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
        
        this.init();
    }    async init() {
        try {
            console.log('🚀 Initializing Kiosk App...');
            
            // Add custom styles first to ensure proper interaction
            this.addStyleSheet();
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            }
            
            // Initialize current time display
            this.updateCurrentTime();
            setInterval(() => this.updateCurrentTime(), 1000);
            
            // Start the app flow immediately
            console.log('📺 Showing loading screen...');
            this.showLoadingScreen();
            
            // Load initial data
            console.log('📊 Loading categories and menu items...');
            await this.loadCategories();
            await this.loadMenuItems();
            
            console.log('✅ Data loaded successfully');
            
            // Initialize event listeners AFTER data is loaded
            console.log('🎧 Setting up event listeners...');
            this.initializeEventListeners();
            
            // Shorter loading time for better UX
            setTimeout(() => {
                console.log('🎯 Transitioning to order type screen...');
                this.showOrderTypeScreen();
            }, 1500);
            
        } catch (error) {
            console.error('❌ Failed to initialize kiosk:', error);
            this.showError('Failed to initialize. Please contact staff.');
        }
    }

    initializeEventListeners() {
        console.log('🎧 Setting up all event listeners...');
        
        // Order type selection
        document.querySelectorAll('.order-type-card').forEach(card => {
            card.addEventListener('click', (e) => {
                console.log('🎯 Order type selected:', card.dataset.type);
                this.selectOrderType(card.dataset.type);
            });
        });

        // Back button on dashboard
        const backBtn = document.getElementById('back-btn');
        if (backBtn) {
            backBtn.addEventListener('click', (e) => {
                console.log('⬅️ Back button clicked');
                this.showOrderTypeScreen();
            });
        }        // Removed document-level click handler - using specific handlers instead
        console.log('✅ Event listeners initialized with specific handlers');

        // Add to cart from modal
        const addToCartBtn = document.getElementById('add-to-cart-btn');
        if (addToCartBtn) {
            addToCartBtn.addEventListener('click', () => {
                console.log('🛒 Add to cart clicked');
                this.addToCartFromModal();
            });
        }

        // Cart button
        const cartBtn = document.getElementById('cart-btn');
        if (cartBtn) {
            cartBtn.addEventListener('click', () => {
                console.log('🛒 Cart button clicked');
                this.showPaymentScreen();
            });
        }

        // Back button on payment screen
        const paymentBackBtn = document.getElementById('payment-back-btn');
        if (paymentBackBtn) {
            paymentBackBtn.addEventListener('click', () => {
                console.log('⬅️ Payment back button clicked');
                this.showDashboard();
            });
        }

        // Modal close functionality
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal') || e.target.closest('.modal-close')) {
                console.log('❌ Modal close clicked');
                this.closeModal();
            }
        });

        // Quantity controls in modal
        const quantityMinus = document.getElementById('quantity-decrease');
        const quantityPlus = document.getElementById('quantity-increase');
        
        if (quantityMinus) {
            quantityMinus.addEventListener('click', () => {
                console.log('➖ Quantity decrease clicked');
                this.adjustModalQuantity(-1);
            });
        }
        
        if (quantityPlus) {
            quantityPlus.addEventListener('click', () => {
                console.log('➕ Quantity increase clicked');
                this.adjustModalQuantity(1);
            });
        }

        // Payment methods using event delegation
        document.addEventListener('click', (e) => {
            if (e.target.closest('.payment-method-btn')) {
                const method = e.target.closest('.payment-method-btn').dataset.method;
                console.log('💳 Payment method selected:', method);
                this.selectPaymentMethod(method);
            }
        });

        // Place order button
        const placeOrderBtn = document.getElementById('place-order-btn');
        if (placeOrderBtn) {
            placeOrderBtn.addEventListener('click', () => {
                console.log('✅ Place order clicked');
                this.placeOrder();
            });
        }

        // Cart item quantity controls using event delegation
        document.addEventListener('click', (e) => {
            if (e.target.closest('.quantity-btn')) {
                const btn = e.target.closest('.quantity-btn');
                const itemIndex = parseInt(btn.dataset.index);
                const action = btn.dataset.action;
                console.log('🔢 Cart quantity changed:', action, itemIndex);
                this.updateCartItemQuantity(itemIndex, action);
            }
        });
        
        console.log('✅ All event listeners set up successfully');
    }

    // Screen Management
    showScreen(screenId) {
        console.log(`🖥️ Switching to screen: ${screenId}`);
        
        // Hide all screens
        const allScreens = document.querySelectorAll('.screen');
        console.log(`📱 Found ${allScreens.length} screens to manage`);
        
        allScreens.forEach(screen => {
            screen.classList.add('hidden');
        });
        
        // Show target screen
        const targetScreen = document.getElementById(screenId);
        if (targetScreen) {
            targetScreen.classList.remove('hidden');
            this.currentScreen = screenId;
            console.log(`✅ Successfully switched to ${screenId}`);
        } else {
            console.error(`❌ Screen not found: ${screenId}`);
        }
    }

    showLoadingScreen() {
        console.log('📺 Showing loading screen...');
        this.showScreen('loading-screen');
    }

    showOrderTypeScreen() {
        console.log('🎯 Showing order type screen...');
        this.showScreen('order-type-screen');
        
        // Add entrance animation
        const cards = document.querySelectorAll('.order-type-card');
        console.log(`🎴 Found ${cards.length} order type cards for animation`);
        
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
        this.showScreen('payment-screen');
        this.renderCartItems();
        this.updatePaymentSummary();
    }

    // Order Type Selection
    selectOrderType(type) {
        this.orderType = type;
        
        // Add selection animation
        const selectedCard = document.querySelector(`[data-type="${type}"]`);
        if (selectedCard) {
            selectedCard.style.transform = 'scale(1.05)';
        }
        
        // Show toast notification
        this.showToast(`Selected: ${type === 'dine-in' ? 'Dine In' : 'Take Away'}`);
        
        setTimeout(() => {
            this.showDashboard();
        }, 800);
    }

    // Data Loading
    async loadCategories() {
        try {
            this.isLoading = true;
            console.log('📊 Loading categories...');
            
            // Check if running in Electron or browser
            if (window.electronAPI && window.electronAPI.database) {
                console.log('🔌 Using Electron API for categories');
                const response = await window.electronAPI.database.getCategories();
                this.categories = response || [];
            } else {
                console.log('🌐 Using mock data for categories (browser mode)');
                this.categories = this.getMockCategories();
            }
            
            console.log('✅ Loaded categories:', this.categories.length);
        } catch (error) {
            console.error('❌ Failed to load categories:', error);
            console.log('🔄 Falling back to mock data');
            this.categories = this.getMockCategories();
        } finally {
            this.isLoading = false;
        }
    }

    async loadMenuItems() {
        try {
            this.isLoading = true;
            console.log('📊 Loading menu items...');
            
            // Check if running in Electron or browser
            if (window.electronAPI && window.electronAPI.database) {
                console.log('🔌 Using Electron API for menu items');
                const response = await window.electronAPI.database.getMenuItems();
                this.menuItems = response || [];
            } else {
                console.log('🌐 Using mock data for menu items (browser mode)');
                this.menuItems = this.getMockMenuItems();
            }
            
            console.log('✅ Loaded menu items:', this.menuItems.length);
        } catch (error) {
            console.error('❌ Failed to load menu items:', error);
            console.log('🔄 Falling back to mock data');
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
        
        // Render menu items for this category
        this.renderMenuItems(categoryId);
    }    renderCategories() {
        console.log('🎨 Rendering categories with DOM creation...');
        const sidebar = document.getElementById('categories-list');
        if (!sidebar) {
            console.error('❌ Categories sidebar not found!');
            return;
        }

        // Clear previous categories
        sidebar.innerHTML = '';
        console.log('📊 Categories to render:', this.categories.length);

        // Create each category using DOM creation for better control
        this.categories.forEach(category => {
            console.log('🏷️ Rendering category:', category.name, 'ID:', category.id);
            
            // Create the category element
            const categoryItem = document.createElement('div');
            categoryItem.className = 'category-item';
            categoryItem.setAttribute('data-category-id', category.id);
            categoryItem.style.cursor = 'pointer';
            
            // Create icon element
            const iconDiv = document.createElement('div');
            iconDiv.className = 'category-icon';
            const icon = document.createElement('i');
            icon.className = this.getCategoryIcon(category.name);
            iconDiv.appendChild(icon);
            
            // Create name element
            const nameSpan = document.createElement('span');
            nameSpan.className = 'category-name';
            nameSpan.textContent = category.name;
            
            // Assemble the category item
            categoryItem.appendChild(iconDiv);
            categoryItem.appendChild(nameSpan);
            
            // Add direct click handler to this specific category
            categoryItem.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                console.log('📂 Category clicked directly:', category.id, '-', category.name);
                
                // Update active category visual state
                document.querySelectorAll('.category-item').forEach(cat => {
                    cat.classList.remove('active');
                });
                categoryItem.classList.add('active');
                
                this.selectCategory(category.id);
            });
            
            // Add to sidebar
            sidebar.appendChild(categoryItem);
        });
        
        // Verify categories were added
        const renderedCategories = document.querySelectorAll('.category-item');
        console.log('✅ Categories rendered:', renderedCategories.length);
        renderedCategories.forEach((cat, index) => {
            console.log(`📝 Category ${index}:`, cat.dataset.categoryId, cat.textContent.trim());
        });
    }

    attachCategoryClickHandlers() {
        console.log('🎯 Attaching category click handlers...');
        const categoryItems = document.querySelectorAll('.category-item');
        
        categoryItems.forEach(categoryItem => {
            categoryItem.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const categoryId = categoryItem.dataset.categoryId;
                console.log('📂 Category clicked directly:', categoryId);
                
                // Update active category visual state
                document.querySelectorAll('.category-item').forEach(cat => {
                    cat.classList.remove('active');
                });
                categoryItem.classList.add('active');
                
                this.selectCategory(categoryId);
            });
        });
        
        console.log('✅ Category click handlers attached:', categoryItems.length);
    }    renderMenuItems(categoryId) {
        const grid = document.getElementById('menu-items-grid');
        if (!grid) return;

        const categoryItems = this.menuItems.filter(item => 
            item.category_id == categoryId && item.is_available
        );

        const itemsHTML = categoryItems.map(item => `
            <div class="menu-item" data-item-id="${item.id}">
                <div class="item-image">
                    <img src="${item.image_path || 'assets/images/placeholder.svg'}" 
                         alt="${item.name}" 
                         onerror="this.src='assets/images/placeholder.svg'">
                </div>
                <div class="item-info">
                    <h3 class="item-name">${item.name}</h3>
                    <p class="item-description">${item.description || ''}</p>
                    <div class="item-price">$${parseFloat(item.price).toFixed(2)}</div>
                </div>
                <div class="item-overlay">
                    <i class="fas fa-plus"></i>
                </div>
            </div>
        `).join('');

        grid.innerHTML = itemsHTML;

        // Update items count
        const itemsCount = document.getElementById('items-count');
        if (itemsCount) {
            itemsCount.textContent = `${categoryItems.length} items`;
        }

        // Add specific click handlers to each menu item after rendering
        this.attachMenuItemClickHandlers();
    }

    attachMenuItemClickHandlers() {
        console.log('🍽️ Attaching menu item click handlers...');
        const menuItems = document.querySelectorAll('.menu-item');
        
        menuItems.forEach(menuItem => {
            menuItem.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const itemId = menuItem.dataset.itemId;
                console.log('🍔 Menu item clicked directly:', itemId);
                
                this.showItemDetail(itemId);
            });
        });
        
        console.log('✅ Menu item click handlers attached:', menuItems.length);
    }

    // Item Detail Modal
    showItemDetail(itemId) {
        const item = this.menuItems.find(i => i.id == itemId);
        if (!item) {
            console.error('❌ Item not found:', itemId);
            return;
        }

        console.log('📝 Showing item detail for:', item.name);

        // Use the existing modal from HTML
        const modal = document.getElementById('item-modal');
        if (!modal) {
            console.error('❌ Modal element not found in HTML');
            return;
        }

        // Populate modal with item data
        const modalItemName = document.getElementById('modal-item-name');
        const modalItemImage = document.getElementById('modal-item-image');
        const modalItemDescription = document.getElementById('modal-item-description');
        const modalItemPrice = document.getElementById('modal-item-price');
        const quantityDisplay = document.getElementById('quantity-display');

        if (modalItemName) modalItemName.textContent = item.name;
        if (modalItemImage) {
            modalItemImage.src = item.image_path || 'assets/images/placeholder.svg';
            modalItemImage.alt = item.name;
        }
        if (modalItemDescription) modalItemDescription.textContent = item.description || '';
        if (modalItemPrice) modalItemPrice.textContent = `$${parseFloat(item.price).toFixed(2)}`;
        if (quantityDisplay) quantityDisplay.textContent = '1';
        
        // Store item ID on modal for later use
        modal.dataset.itemId = itemId;

        // Show modal
        modal.classList.remove('hidden');
        console.log('✅ Modal displayed for item:', item.name);
    }

    adjustModalQuantity(delta) {
        const quantitySpan = document.getElementById('quantity-display');
        if (!quantitySpan) {
            console.error('❌ Quantity display element not found');
            return;
        }
        const currentQuantity = parseInt(quantitySpan.textContent);
        const newQuantity = Math.max(1, currentQuantity + delta);
        quantitySpan.textContent = newQuantity;
        console.log(`🔢 Modal quantity adjusted to: ${newQuantity}`);
    }

    addToCartFromModal() {
        const modal = document.getElementById('item-modal');
        if (!modal) {
            console.error('❌ Modal not found');
            return;
        }
        
        const itemId = modal.dataset.itemId;
        const quantityElement = document.getElementById('quantity-display');
        if (!quantityElement) {
            console.error('❌ Quantity display not found');
            return;
        }
        
        const quantity = parseInt(quantityElement.textContent);
        console.log(`🛒 Adding item ${itemId} with quantity ${quantity} to cart`);
        
        this.addToCart(itemId, quantity);
        this.closeModal();
    }

    closeModal() {
        const modal = document.getElementById('item-modal');
        if (modal) {
            modal.classList.add('hidden');
            console.log('✅ Modal closed');
        }
    }

    // Cart Management
    addToCart(itemId, quantity = 1) {
        const item = this.menuItems.find(i => i.id == itemId);
        if (!item) return;

        // Check if item already in cart
        const existingIndex = this.cart.findIndex(cartItem => cartItem.id == itemId);
        
        if (existingIndex !== -1) {
            this.cart[existingIndex].quantity += quantity;
        } else {
            this.cart.push({
                ...item,
                quantity: quantity,
                cartId: Date.now() + Math.random() // Unique cart ID
            });
        }

        this.updateCartUI();
        this.showToast(`${item.name} added to cart`);
    }

    updateCartItemQuantity(itemIndex, action) {
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

        // Update cart button
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
            } else {
                cartBtn.style.transform = 'translateY(100px)';
                cartBtn.style.opacity = '0';
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

        const cartHTML = this.cart.map((item, index) => `
            <div class="cart-item">
                <div class="cart-item-info">
                    <h4>${item.name}</h4>
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
        const tax = subtotal * 0.1; // 10% tax
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
        // Update UI
        document.querySelectorAll('.payment-method-btn').forEach(pm => {
            pm.classList.remove('selected');
        });
        
        const selectedMethod = document.querySelector(`[data-method="${method}"]`);
        if (selectedMethod) {
            selectedMethod.classList.add('selected');
        }
        
        // Enable place order button
        const placeOrderBtn = document.getElementById('place-order-btn');
        if (placeOrderBtn) {
            placeOrderBtn.disabled = false;
        }
    }

    async placeOrder() {
        try {
            const orderData = {
                order_type: this.orderType,
                items: this.cart.map(item => ({
                    item_id: item.id,
                    name: item.name,
                    quantity: item.quantity,
                    price: item.price
                })),
                subtotal: this.cartTotal,
                tax: this.cartTotal * 0.1,
                total: this.cartTotal * 1.1,
                timestamp: new Date().toISOString()
            };

            // Show processing state
            const placeOrderBtn = document.getElementById('place-order-btn');
            const originalText = placeOrderBtn.innerHTML;
            placeOrderBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            placeOrderBtn.disabled = true;

            // Simulate order processing
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            this.showToast('Order placed successfully!', 'success');
            console.log('Order placed successfully:', orderData);
            
            // Reset for next customer
            setTimeout(() => {
                this.resetKiosk();
            }, 3000);

        } catch (error) {
            console.error('Failed to place order:', error);
            this.showToast('Failed to place order. Please try again.', 'error');
            
            // Reset button state
            const placeOrderBtn = document.getElementById('place-order-btn');
            if (placeOrderBtn) {
                placeOrderBtn.innerHTML = '<i class="fas fa-credit-card"></i> Place Order';
                placeOrderBtn.disabled = false;
            }
        }
    }

    resetKiosk() {
        this.cart = [];
        this.cartTotal = 0;
        this.orderType = null;
        this.currentCategory = null;
        this.updateCartUI();
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
        // Create toast if it doesn't exist
        let toast = document.getElementById('toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'toast';
            toast.className = 'toast';
            document.body.appendChild(toast);
        }

        toast.textContent = message;
        toast.className = `toast ${type} show`;

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    getCategoryIcon(categoryName) {
        const icons = {
            'appetizers': 'fas fa-seedling',
            'mains': 'fas fa-utensils',
            'desserts': 'fas fa-ice-cream',
            'beverages': 'fas fa-coffee',
            'salads': 'fas fa-leaf',
            'soups': 'fas fa-bowl-hot',
            'pizza': 'fas fa-pizza-slice',
            'burgers': 'fas fa-hamburger',
            'pasta': 'fas fa-wheat-awn',
            'seafood': 'fas fa-fish'
        };
        
        const key = categoryName.toLowerCase();
        return icons[key] || 'fas fa-utensils';
    }

    addStyleSheet() {
        console.log('🎨 Adding dynamic styles for better interaction...');
        const style = document.createElement('style');
        style.textContent = `
            /* Enhanced category interaction styles */
            .category-item {
                padding: 12px 16px;
                margin-bottom: 8px;
                background-color: var(--bg-card);
                border-radius: var(--radius-md);
                cursor: pointer !important;
                transition: all 0.2s ease;
                position: relative;
                z-index: 100 !important; /* Very high z-index to ensure clickability */
                border: 2px solid transparent;
                pointer-events: auto !important;
                display: flex;
                align-items: center;
                gap: 12px;
                user-select: none;
            }
            
            .category-item:hover {
                background-color: var(--primary-light);
                transform: translateY(-2px);
                box-shadow: var(--shadow-md);
                border-color: var(--primary-color);
            }
            
            .category-item.active {
                border-color: var(--primary-color);
                background-color: var(--primary-light);
                font-weight: bold;
                color: var(--primary-color);
            }
            
            .category-icon,
            .category-name {
                pointer-events: none !important; /* Make sure clicks go to parent */
            }
            
            .category-icon {
                font-size: 1.2rem;
                width: 24px;
                text-align: center;
            }
            
            .category-name {
                font-weight: 500;
            }
            
            /* Ensure menu items don't overlap categories */
            .menu-items-grid {
                position: relative;
                z-index: 50; /* Lower than categories */
            }
            
            .menu-item {
                position: relative;
                z-index: 50;
                pointer-events: auto !important;
                cursor: pointer !important;
            }
            
            /* Ensure sidebar has proper layering */
            .categories-sidebar {
                position: relative;
                z-index: 100;
            }
            
            .categories-list {
                position: relative;
                z-index: 100;
            }
        `;
        document.head.appendChild(style);
        console.log('✅ Dynamic styles added successfully');
    }

    // Mock data for fallback
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
            { id: 6, name: 'Beef Steak', price: 24.99, category_id: 2, is_available: true, description: 'Juicy beef steak cooked to perfection' },
            { id: 7, name: 'Ice Cream', price: 5.99, category_id: 3, is_available: true, description: 'Vanilla ice cream with toppings' },
            { id: 8, name: 'Orange Juice', price: 4.99, category_id: 4, is_available: true, description: 'Fresh squeezed orange juice' },
            { id: 9, name: 'Fish Tacos', price: 16.99, category_id: 2, is_available: true, description: 'Grilled fish with fresh toppings' },
            { id: 10, name: 'Cheese Sticks', price: 8.99, category_id: 1, is_available: true, description: 'Mozzarella sticks with marinara sauce' }
        ];
    }
}

// Initialize the kiosk app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎯 DOM Content Loaded - Initializing Kiosk Interface...');
    window.kioskApp = new KioskApp();
});

// Also initialize immediately if DOM is already ready
if (document.readyState !== 'loading') {
    console.log('🎯 DOM Already Ready - Initializing Kiosk Interface...');
    window.kioskApp = new KioskApp();
}

// Export for global access
window.KioskApp = KioskApp;