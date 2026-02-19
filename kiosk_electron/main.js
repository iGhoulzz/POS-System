const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const fs = require('fs');

// Use Electron's writable per-user data directory
const userDataPath = app.getPath('userData');
if (!fs.existsSync(userDataPath)) {
    fs.mkdirSync(userDataPath, { recursive: true });
}

// Fix 2: Disable hardware acceleration to avoid GPU cache issues
app.disableHardwareAcceleration();

// Fix 3: Set app user model ID
app.setAppUserModelId('pos-v2-kiosk');

// Chromium flags
app.commandLine.appendSwitch('--disable-features', 'VizDisplayCompositor');
app.commandLine.appendSwitch('--disable-dev-shm-usage');
app.commandLine.appendSwitch('--disable-background-timer-throttling');
app.commandLine.appendSwitch('--disable-backgrounding-occluded-windows');
app.commandLine.appendSwitch('--disable-renderer-backgrounding');

// ---- Database Setup (sql.js — pure JS/WASM, no native build needed) ----
const DB_PATH = path.join(__dirname, '..', 'db', 'pos_system.db');

let db = null;
let SQL = null;

async function initDatabase() {
    if (db) return db;
    try {
        const initSqlJs = require('sql.js');
        SQL = await initSqlJs();

        if (!fs.existsSync(DB_PATH)) {
            console.error('❌ Database file not found:', DB_PATH);
            return null;
        }

        const fileBuffer = fs.readFileSync(DB_PATH);
        db = new SQL.Database(fileBuffer);
        console.log('✅ Connected to SQLite database at:', DB_PATH);
        return db;
    } catch (error) {
        console.error('❌ Failed to connect to database:', error);
        return null;
    }
}

function saveDatabase() {
    if (!db) return;
    try {
        const data = db.export();
        const buffer = Buffer.from(data);
        fs.writeFileSync(DB_PATH, buffer);
        console.log('💾 Database saved to disk');
    } catch (error) {
        console.error('❌ Failed to save database:', error);
    }
}

// Helper: run a SELECT query and return results as array of objects
function queryAll(sql, params = []) {
    if (!db) return [];
    try {
        const stmt = db.prepare(sql);
        if (params.length > 0) stmt.bind(params);

        const results = [];
        while (stmt.step()) {
            results.push(stmt.getAsObject());
        }
        stmt.free();
        return results;
    } catch (error) {
        console.error('❌ Query error:', error.message, 'SQL:', sql);
        return [];
    }
}

// Helper: run a single-row SELECT
function queryOne(sql, params = []) {
    const results = queryAll(sql, params);
    return results.length > 0 ? results[0] : null;
}

// Helper: run INSERT/UPDATE/DELETE
function runSQL(sql, params = []) {
    if (!db) return null;
    try {
        db.run(sql, params);
        return true;
    } catch (error) {
        console.error('❌ Run error:', error.message, 'SQL:', sql);
        return false;
    }
}

// ---- Electron Store Setup ----
let store = null;

function getStore() {
    if (store) return store;
    try {
        const Store = require('electron-store');
        store = new Store({
            name: 'pos-kiosk-settings',
            cwd: userDataPath
        });
        console.log('✅ Electron store initialized');
        return store;
    } catch (error) {
        console.error('❌ Failed to initialize electron-store:', error);
        return null;
    }
}

class POSKioskApp {
    constructor() {
        this.mainWindow = null;
        this.isDev = process.argv.includes('--dev');
        this.isKioskMode = !this.isDev;

        this.initializeApp();
    }

    initializeApp() {
        app.whenReady().then(async () => {
            console.log('🚀 Electron app ready, creating main window...');

            // Initialize database connection
            const database = await initDatabase();
            if (!database) {
                console.error('❌ Database not available. Check that pos_system.db exists at:', DB_PATH);
            }

            // Initialize store
            getStore();

            this.createMainWindow();

            app.on('activate', () => {
                if (BrowserWindow.getAllWindows().length === 0) {
                    this.createMainWindow();
                }
            });
        }).catch((error) => {
            console.error('❌ Failed to initialize app:', error);
        });

        app.on('window-all-closed', () => {
            if (process.platform !== 'darwin') {
                app.quit();
            }
        });

        // Prevent new window creation
        app.on('web-contents-created', (event, contents) => {
            contents.on('new-window', (event, navigationUrl) => {
                event.preventDefault();
            });
        });

        app.on('before-quit', (event) => {
            // Save and close database on quit
            if (db) {
                try {
                    saveDatabase();
                    db.close();
                } catch (e) { /* ignore */ }
                db = null;
            }
        });

        // IPC handlers
        this.setupIpcHandlers();
    }

    createMainWindow() {
        const iconPath = path.join(__dirname, 'assets', 'icon.png');
        const windowConfig = {
            width: this.isDev ? 1400 : 1920,
            height: this.isDev ? 900 : 1080,
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                enableRemoteModule: false,
                preload: path.join(__dirname, 'preload.js'),
                partition: 'temp:kiosk-session',
                webSecurity: true,
                allowRunningInsecureContent: false,
                experimentalFeatures: false,
                backgroundThrottling: false
            },
            show: false,
            autoHideMenuBar: true,
            titleBarStyle: 'hidden',
            backgroundColor: '#0B0E14'
        };

        if (fs.existsSync(iconPath)) {
            windowConfig.icon = iconPath;
        }

        // Kiosk mode settings
        if (this.isKioskMode) {
            windowConfig.kiosk = true;
            windowConfig.fullscreen = true;
            windowConfig.alwaysOnTop = true;
            windowConfig.resizable = false;
            windowConfig.minimizable = false;
            windowConfig.maximizable = false;
            windowConfig.closable = false;
        } else {
            windowConfig.frame = true;
            windowConfig.resizable = true;
            windowConfig.minWidth = 1024;
            windowConfig.minHeight = 768;
        }

        this.mainWindow = new BrowserWindow(windowConfig);

        // Clear storage data on startup
        const session = this.mainWindow.webContents.session;
        session.clearStorageData({
            storages: ['websql', 'indexdb', 'localstorage', 'shadercache', 'serviceworkers']
        }).catch((error) => {
            console.log('⚠️ Session storage clear warning:', error.message);
        });

        // Load the app
        const indexPath = path.join(__dirname, 'renderer', 'index.html');

        if (fs.existsSync(indexPath)) {
            this.mainWindow.loadFile(indexPath)
                .then(() => {
                    console.log('✅ Kiosk application loaded successfully');
                })
                .catch((error) => {
                    console.error('❌ Failed to load application:', error);
                });
        } else {
            console.error('❌ Index file not found:', indexPath);
        }

        // Show window when ready
        this.mainWindow.once('ready-to-show', () => {
            this.mainWindow.show();
            console.log('🖥️ Kiosk window displayed');

            if (this.isDev) {
                this.mainWindow.webContents.openDevTools();
            }
        });

        this.mainWindow.on('closed', () => {
            this.mainWindow = null;
        });

        // Prevent navigation to external URLs
        this.mainWindow.webContents.on('will-navigate', (event, navigationUrl) => {
            try {
                const parsedUrl = new URL(navigationUrl);
                if (parsedUrl.origin !== 'file://') {
                    event.preventDefault();
                }
            } catch (e) {
                // ignore invalid URLs
            }
        });

        // Handle external links
        this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
            shell.openExternal(url);
            return { action: 'deny' };
        });
    }

    setupIpcHandlers() {
        // ---- App Info ----
        ipcMain.handle('get-app-version', () => app.getVersion());

        ipcMain.handle('get-app-info', () => ({
            version: app.getVersion(),
            platform: process.platform,
            arch: process.arch,
            isDev: this.isDev,
            isKioskMode: this.isKioskMode
        }));

        // ---- Real Database Operations ----

        ipcMain.handle('db-get-categories', async () => {
            try {
                const categories = queryAll(
                    'SELECT id, name, description FROM categories WHERE is_active = 1 ORDER BY name'
                );
                console.log(`✅ Fetched ${categories.length} categories from DB`);
                return categories;
            } catch (error) {
                console.error('❌ Error getting categories:', error);
                return [];
            }
        });

        ipcMain.handle('db-get-menu-items', async () => {
            try {
                const items = queryAll(`
                    SELECT mi.id, mi.name, mi.description, mi.price, mi.cost_price,
                           mi.category_id, mi.image_path, mi.is_active
                    FROM menu_items mi
                    WHERE mi.is_active = 1
                    ORDER BY mi.name
                `);

                // Map fields for kiosk compatibility
                const mappedItems = items.map(item => ({
                    ...item,
                    is_available: item.is_active === 1,
                    // Resolve image path relative to project root
                    image_path: item.image_path
                        ? path.join(__dirname, '..', item.image_path).replace(/\\/g, '/')
                        : null
                }));

                console.log(`✅ Fetched ${mappedItems.length} menu items from DB`);
                return mappedItems;
            } catch (error) {
                console.error('❌ Error getting menu items:', error);
                return [];
            }
        });

        ipcMain.handle('db-create-order', async (event, orderData) => {
            let transactionStarted = false;
            try {
                if (!db) {
                    return { success: false, message: 'Database not available' };
                }
                if (!Array.isArray(orderData?.items) || orderData.items.length === 0) {
                    return { success: false, message: 'Order must include at least one item' };
                }

                // Generate order number
                const now = new Date();
                const dateStr = now.toISOString().split('T')[0].replace(/-/g, '');
                const countResult = queryOne(
                    "SELECT COUNT(*) as count FROM orders WHERE date(created_at) = date('now', 'localtime')"
                );
                const orderCount = (countResult?.count || 0) + 1;
                const orderNumber = `ORD-${dateStr}-${orderCount.toString().padStart(3, '0')}`;

                // Calculate totals
                const subtotal = orderData.subtotal || 0;
                const taxRate = orderData.tax_rate || 0.08;
                const taxAmount = subtotal * taxRate;
                const totalAmount = subtotal + taxAmount;

                // Keep order + items atomic
                if (!runSQL('BEGIN TRANSACTION')) {
                    throw new Error('Failed to start database transaction');
                }
                transactionStarted = true;

                // Insert order
                const orderInserted = runSQL(`
                    INSERT INTO orders (order_number, customer_name, order_type, 
                                       total_amount, tax_amount, 
                                       payment_method, status, created_by, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, datetime('now', 'localtime'))
                `, [
                    orderNumber,
                    orderData.customer_name || 'Kiosk Customer',
                    orderData.order_type || 'dine_in',
                    totalAmount,
                    taxAmount,
                    orderData.payment_method || 'cash',
                    null  // created_by = null for kiosk orders
                ]);
                if (!orderInserted) {
                    throw new Error('Failed to insert order');
                }

                // Get the last inserted order ID
                const lastIdResult = queryOne('SELECT last_insert_rowid() as id');
                const orderId = lastIdResult?.id;
                if (!orderId) {
                    throw new Error('Failed to determine created order ID');
                }

                // Insert order items
                for (const item of (orderData.items || [])) {
                    const quantity = Number(item.quantity);
                    const unitPrice = Number(item.price);
                    if (!Number.isFinite(quantity) || quantity <= 0 || !Number.isFinite(unitPrice) || unitPrice < 0) {
                        throw new Error('Invalid order item quantity or price');
                    }

                    const itemInserted = runSQL(`
                        INSERT INTO order_items (order_id, menu_item_id, quantity, unit_price, total_price)
                        VALUES (?, ?, ?, ?, ?)
                    `, [
                        orderId,
                        item.item_id || item.id,
                        quantity,
                        unitPrice,
                        unitPrice * quantity
                    ]);
                    if (!itemInserted) {
                        throw new Error('Failed to insert order item');
                    }
                }

                if (!runSQL('COMMIT')) {
                    throw new Error('Failed to commit order transaction');
                }
                transactionStarted = false;

                // Save to disk after order creation
                saveDatabase();

                console.log(`✅ Order created: ${orderNumber} (ID: ${orderId})`);
                return {
                    success: true,
                    orderId: orderId,
                    orderNumber: orderNumber
                };
            } catch (error) {
                if (transactionStarted) {
                    runSQL('ROLLBACK');
                }
                console.error('❌ Error creating order:', error);
                return { success: false, message: error.message };
            }
        });

        ipcMain.handle('db-get-settings', async () => {
            try {
                const settings = queryAll('SELECT key, value FROM settings');
                const result = {};
                settings.forEach(s => { result[s.key] = s.value; });
                return result;
            } catch (error) {
                console.error('❌ Error getting settings:', error);
                return {};
            }
        });

        // ---- Window Operations ----
        ipcMain.handle('minimize-window', () => {
            if (this.mainWindow && !this.isKioskMode) {
                this.mainWindow.minimize();
            }
        });

        ipcMain.handle('maximize-window', () => {
            if (this.mainWindow && !this.isKioskMode) {
                if (this.mainWindow.isMaximized()) {
                    this.mainWindow.unmaximize();
                } else {
                    this.mainWindow.maximize();
                }
            }
        });

        ipcMain.handle('close-window', () => {
            if (this.mainWindow && !this.isKioskMode) {
                this.mainWindow.close();
            }
        });

        // Restart app
        ipcMain.handle('restart-app', () => {
            app.relaunch();
            app.exit();
        });

        // Quit app
        ipcMain.handle('quit-app', async () => {
            if (!this.isKioskMode) {
                app.quit();
                return true;
            }

            const result = await dialog.showMessageBox(this.mainWindow, {
                type: 'question',
                buttons: ['Cancel', 'Quit'],
                defaultId: 0,
                title: 'Quit Application',
                message: 'Are you sure you want to quit the kiosk application?',
                detail: 'This will close the POS system.'
            });

            if (result.response === 1) {
                app.quit();
                return true;
            }
            return false;
        });

        // Toggle fullscreen
        ipcMain.handle('toggle-fullscreen', () => {
            if (this.mainWindow && !this.isKioskMode) {
                this.mainWindow.setFullScreen(!this.mainWindow.isFullScreen());
            }
        });

        // Show error dialog
        ipcMain.handle('show-error', (event, title, content) => {
            return dialog.showErrorBox(title, content);
        });

        // Show message dialog
        ipcMain.handle('show-message', async (event, options) => {
            return await dialog.showMessageBox(this.mainWindow, options);
        });

        // Print receipt
        ipcMain.handle('print-receipt', async (event, content) => {
            try {
                const printWindow = new BrowserWindow({
                    width: 300,
                    height: 400,
                    show: false,
                    webPreferences: {
                        nodeIntegration: false,
                        contextIsolation: true
                    }
                });

                await printWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(content)}`);

                await printWindow.webContents.print({
                    silent: true,
                    printBackground: true,
                    margins: { marginType: 'none' }
                });

                printWindow.close();
                return true;
            } catch (error) {
                console.error('Print error:', error);
                return false;
            }
        });

        // Settings via electron-store
        ipcMain.handle('get-settings', () => {
            const s = getStore();
            if (!s) return {};
            return {
                theme: s.get('theme', 'light'),
                language: s.get('language', 'en'),
                autoStartKiosk: s.get('autoStartKiosk', true),
                printerSettings: s.get('printerSettings', {}),
                kioskSettings: s.get('kioskSettings', {
                    idleTimeout: 300,
                    screensaverEnabled: true,
                    autoLogout: true
                })
            };
        });

        ipcMain.handle('save-settings', (event, settings) => {
            const s = getStore();
            if (!s) return;
            Object.keys(settings).forEach(key => {
                s.set(key, settings[key]);
            });
        });
    }
}

// Handle crashes
process.on('uncaughtException', (error) => {
    console.error('❌ Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
});

console.log('🚀 Electron main process starting...');

// Initialize the application
new POSKioskApp();
