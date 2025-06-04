// Utility functions for the POS application
class Utils {
    static formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    }
    
    static formatDate(date) {
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    }
    
    static formatTime(date) {
        return new Intl.DateTimeFormat('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        }).format(new Date(date));
    }
    
    static generateOrderNumber() {
        const now = new Date();
        const timestamp = now.getTime().toString().slice(-6);
        const random = Math.floor(Math.random() * 100).toString().padStart(2, '0');
        return `ORD${timestamp}${random}`;
    }
    
    static generateReceiptId() {
        const now = new Date();
        const timestamp = now.getTime().toString().slice(-8);
        return `RCP${timestamp}`;
    }
    
    static calculateTax(amount, taxRate = 0.08) {
        return amount * taxRate;
    }
    
    static calculateTotal(subtotal, tax) {
        return subtotal + tax;
    }
    
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    static throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    static showToast(title, message, type = 'info', duration = 4000) {
        const container = document.getElementById('toast-container');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icon = this.getToastIcon(type);
        
        toast.innerHTML = `
            <div class="toast-icon">
                <i class="${icon}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add close functionality
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.removeToast(toast);
        });
        
        // Add to container
        container.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        // Auto remove
        setTimeout(() => {
            this.removeToast(toast);
        }, duration);
    }
    
    static getToastIcon(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }
    
    static removeToast(toast) {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }
    
    static showModal(options) {
        const {
            title = 'Confirmation',
            message = 'Are you sure?',
            type = 'confirm',
            onConfirm = () => {},
            onCancel = () => {},
            confirmText = 'Confirm',
            cancelText = 'Cancel'
        } = options;
        
        const container = document.getElementById('modal-container');
        if (!container) return;
        
        const modal = document.createElement('div');
        modal.className = 'modal';
        
        modal.innerHTML = `
            <div class="modal-header">
                <h3>${title}</h3>
                <button class="modal-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <p>${message}</p>
            </div>
            <div class="modal-footer">
                ${type === 'confirm' ? `<button class="btn btn-secondary modal-cancel">${cancelText}</button>` : ''}
                <button class="btn btn-primary modal-confirm">${confirmText}</button>
            </div>
        `;
        
        // Add event listeners
        const closeModal = () => {
            container.classList.remove('active');
            setTimeout(() => {
                container.innerHTML = '';
            }, 300);
        };
        
        modal.querySelector('.modal-close').addEventListener('click', () => {
            closeModal();
            onCancel();
        });
        
        if (type === 'confirm') {
            modal.querySelector('.modal-cancel').addEventListener('click', () => {
                closeModal();
                onCancel();
            });
        }
        
        modal.querySelector('.modal-confirm').addEventListener('click', () => {
            closeModal();
            onConfirm();
        });
        
        // Add to container and show
        container.innerHTML = '';
        container.appendChild(modal);
        container.classList.add('active');
        
        // Focus on confirm button
        setTimeout(() => {
            modal.querySelector('.modal-confirm').focus();
        }, 100);
    }
    
    static showLoadingModal(title = 'Loading...', message = 'Please wait...') {
        const container = document.getElementById('modal-container');
        if (!container) return;
        
        const modal = document.createElement('div');
        modal.className = 'modal';
        
        modal.innerHTML = `
            <div class="modal-header">
                <h3>${title}</h3>
            </div>
            <div class="modal-body text-center">
                <div class="loading-spinner"></div>
                <p>${message}</p>
            </div>
        `;
        
        container.innerHTML = '';
        container.appendChild(modal);
        container.classList.add('active');
        
        return {
            close: () => {
                container.classList.remove('active');
                setTimeout(() => {
                    container.innerHTML = '';
                }, 300);
            }
        };
    }
    
    static validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    static validatePhoneNumber(phone) {
        const re = /^\+?[\d\s\-\(\)]+$/;
        return re.test(phone) && phone.replace(/\D/g, '').length >= 10;
    }
    
    static sanitizeInput(input) {
        const div = document.createElement('div');
        div.textContent = input;
        return div.innerHTML;
    }
    
    static truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.slice(0, maxLength) + '...';
    }
    
    static groupBy(array, key) {
        return array.reduce((result, item) => {
            const group = item[key];
            if (!result[group]) {
                result[group] = [];
            }
            result[group].push(item);
            return result;
        }, {});
    }
    
    static sortBy(array, key, direction = 'asc') {
        return array.sort((a, b) => {
            const aVal = a[key];
            const bVal = b[key];
            
            if (direction === 'asc') {
                return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
            } else {
                return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
            }
        });
    }
    
    static exportToCSV(data, filename) {
        if (!data || !data.length) {
            this.showToast('Export Error', 'No data to export', 'error');
            return;
        }
        
        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => 
                headers.map(header => {
                    let value = row[header];
                    if (typeof value === 'string' && value.includes(',')) {
                        value = `"${value}"`;
                    }
                    return value;
                }).join(',')
            )
        ].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
    }
    
    static async printReceipt(content) {
        try {
            const result = await window.electronAPI.print.receipt(content);
            if (result) {
                this.showToast('Print Success', 'Receipt printed successfully', 'success');
            } else {
                this.showToast('Print Error', 'Failed to print receipt', 'error');
            }
            return result;
        } catch (error) {
            console.error('Print error:', error);
            this.showToast('Print Error', 'An error occurred while printing', 'error');
            return false;
        }
    }
    
    static generateReceiptHTML(order) {
        const { items, subtotal, tax, total, orderNumber, timestamp } = order;
        
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Receipt</title>
                <style>
                    body {
                        font-family: 'Courier New', monospace;
                        font-size: 12px;
                        line-height: 1.4;
                        margin: 0;
                        padding: 10px;
                        width: 280px;
                    }
                    .header {
                        text-align: center;
                        border-bottom: 1px dashed #000;
                        padding-bottom: 10px;
                        margin-bottom: 10px;
                    }
                    .title {
                        font-size: 16px;
                        font-weight: bold;
                        margin-bottom: 5px;
                    }
                    .order-info {
                        margin-bottom: 10px;
                    }
                    .items {
                        border-bottom: 1px dashed #000;
                        padding-bottom: 10px;
                        margin-bottom: 10px;
                    }
                    .item {
                        display: flex;
                        justify-content: space-between;
                        margin-bottom: 3px;
                    }
                    .item-name {
                        flex: 1;
                    }
                    .item-qty {
                        margin: 0 10px;
                    }
                    .item-price {
                        text-align: right;
                        min-width: 60px;
                    }
                    .totals {
                        text-align: right;
                    }
                    .total-line {
                        margin-bottom: 3px;
                    }
                    .grand-total {
                        font-weight: bold;
                        font-size: 14px;
                        border-top: 1px solid #000;
                        padding-top: 5px;
                        margin-top: 5px;
                    }
                    .footer {
                        text-align: center;
                        margin-top: 15px;
                        font-size: 10px;
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="title">POS-V2 Restaurant</div>
                    <div>Thank you for your order!</div>
                </div>
                
                <div class="order-info">
                    <div>Order #: ${orderNumber}</div>
                    <div>Date: ${this.formatDate(timestamp)}</div>
                </div>
                
                <div class="items">
                    ${items.map(item => `
                        <div class="item">
                            <span class="item-name">${item.name}</span>
                            <span class="item-qty">x${item.quantity}</span>
                            <span class="item-price">${this.formatCurrency(item.price * item.quantity)}</span>
                        </div>
                    `).join('')}
                </div>
                
                <div class="totals">
                    <div class="total-line">Subtotal: ${this.formatCurrency(subtotal)}</div>
                    <div class="total-line">Tax: ${this.formatCurrency(tax)}</div>
                    <div class="grand-total">Total: ${this.formatCurrency(total)}</div>
                </div>
                
                <div class="footer">
                    <div>Thank you for dining with us!</div>
                    <div>Visit us again soon</div>
                </div>
            </body>
            </html>
        `;
    }
    
    static async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('Copied', 'Text copied to clipboard', 'success');
            return true;
        } catch (error) {
            console.error('Failed to copy to clipboard:', error);
            this.showToast('Copy Error', 'Failed to copy to clipboard', 'error');
            return false;
        }
    }
    
    static createElementFromHTML(htmlString) {
        const div = document.createElement('div');
        div.innerHTML = htmlString.trim();
        return div.firstChild;
    }
    
    static isEmpty(value) {
        return value === null || value === undefined || value === '' || 
               (Array.isArray(value) && value.length === 0) ||
               (typeof value === 'object' && Object.keys(value).length === 0);
    }
    
    static isValidNumber(value) {
        return !isNaN(value) && isFinite(value) && value >= 0;
    }
    
    static roundToTwo(num) {
        return Math.round((num + Number.EPSILON) * 100) / 100;
    }
    
    static getTimeAgo(date) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - new Date(date)) / 1000);
        
        const intervals = {
            year: 31536000,
            month: 2592000,
            week: 604800,
            day: 86400,
            hour: 3600,
            minute: 60,
            second: 1
        };
        
        for (const [unit, seconds] of Object.entries(intervals)) {
            const count = Math.floor(diffInSeconds / seconds);
            if (count >= 1) {
                return `${count} ${unit}${count !== 1 ? 's' : ''} ago`;
            }
        }
        
        return 'just now';
    }
    
    static generateRandomId(length = 8) {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let result = '';
        for (let i = 0; i < length; i++) {
            result += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return result;
    }
}

// Make Utils available globally
window.Utils = Utils;
