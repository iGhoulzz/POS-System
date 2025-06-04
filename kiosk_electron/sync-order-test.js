console.log('Starting synchronous order creation test...');

const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, '..', 'db', 'pos_system.db');
console.log('Database path:', dbPath);

try {
    const db = new Database(dbPath);
    console.log('Database connected');
    
    // Check initial state
    const initialCount = db.prepare('SELECT COUNT(*) as count FROM orders').get();
    console.log('Initial orders count:', initialCount.count);
    
    // Generate order number
    const timestamp = Date.now();
    const orderNumber = `ORD-${timestamp}`;
    console.log('Creating order:', orderNumber);
    
    // Insert order
    const insertOrderQuery = `
        INSERT INTO orders (order_number, customer_name, customer_phone, order_type, subtotal, tax, total, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', datetime('now'))
    `;
    
    const stmt = db.prepare(insertOrderQuery);
    const result = stmt.run(
        orderNumber,
        'Test Customer',
        '555-1234',
        'dine_in',
        20.97,
        2.10,
        23.07
    );
    
    const orderId = result.lastInsertRowid;
    console.log('✅ Order created with ID:', orderId);
    
    // Add order items
    const insertItemQuery = `
        INSERT INTO order_items (order_id, menu_item_id, quantity, price, notes)
        VALUES (?, ?, ?, ?, ?)
    `;
    
    const itemStmt = db.prepare(insertItemQuery);
    
    // Add Caesar Salad
    const item1Result = itemStmt.run(orderId, 2, 2, 8.99, 'Extra croutons');
    console.log('✅ Added Caesar Salad (x2)');
    
    // Add Coca Cola
    const item2Result = itemStmt.run(orderId, 3, 1, 2.99, '');
    console.log('✅ Added Coca Cola (x1)');
    
    // Verify final state
    const finalCount = db.prepare('SELECT COUNT(*) as count FROM orders').get();
    console.log('Final orders count:', finalCount.count);
    
    // Get the created order details
    const createdOrder = db.prepare('SELECT * FROM orders WHERE id = ?').get(orderId);
    console.log('Created order details:', createdOrder);
    
    // Get order items
    const orderItems = db.prepare(`
        SELECT oi.*, mi.name as item_name 
        FROM order_items oi 
        JOIN menu_items mi ON oi.menu_item_id = mi.id 
        WHERE oi.order_id = ?
    `).all(orderId);
    console.log('Order items:', orderItems);
    
    db.close();
    console.log('🎉 Test completed successfully!');
    
} catch (error) {
    console.error('❌ Test failed:', error);
}

console.log('Script finished.');
