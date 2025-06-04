console.log('Starting order creation test...');

const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, '..', 'db', 'pos_system.db');
console.log('Database path:', dbPath);

// Test order creation
async function createTestOrder() {
    console.log('Creating test order...');
    
    try {
        const db = new Database(dbPath);
        
        // Generate order number
        const timestamp = Date.now();
        const orderNumber = `ORD-${timestamp}`;
        
        // Insert order
        const insertOrderQuery = `
            INSERT INTO orders (order_number, customer_name, customer_phone, order_type, subtotal, tax, total, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', datetime('now'))
        `;
        
        const stmt = db.prepare(insertOrderQuery);
        const result = stmt.run([
            orderNumber,
            'Test Customer',
            '555-1234',
            'dine_in',
            20.97,
            2.10,
            23.07
        ]);
        
        console.log('Order created with ID:', result.lastInsertRowid);
        
        // Add order items
        const insertItemQuery = `
            INSERT INTO order_items (order_id, menu_item_id, quantity, price, notes)
            VALUES (?, ?, ?, ?, ?)
        `;
        
        const itemStmt = db.prepare(insertItemQuery);
        itemStmt.run([result.lastInsertRowid, 2, 2, 8.99, 'Extra croutons']);
        itemStmt.run([result.lastInsertRowid, 3, 1, 2.99, '']);
        
        console.log('Order items added');
        
        // Verify
        const orderCount = db.prepare('SELECT COUNT(*) as count FROM orders').get();
        console.log('Total orders:', orderCount.count);
        
        db.close();
        console.log('✅ Test completed successfully!');
        
    } catch (error) {
        console.error('❌ Test failed:', error);
    }
}

createTestOrder();
