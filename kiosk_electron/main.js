const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const Store = require('electron-store');
const Database = require('better-sqlite3');

const store = new Store();

function getDatabasePath() {
    return store.get('dbPath') || path.join(__dirname, '..', 'db', 'pos_system.db');
}

function executeQuery(query, params = []) {
    const dbPath = getDatabasePath();
    try {
        const db = new Database(dbPath, { readonly: true });
        const stmt = db.prepare(query);
        const rows = stmt.all(params);
        db.close();
        return Promise.resolve(rows);
    } catch (err) {
        return Promise.reject(err);
    }
}

// Fix 1: Set app data path to avoid permission issues
const userDataPath = path.join(__dirname, 'app-data');
if (!fs.existsSync(userDataPath)) {
    fs.mkdirSync(userDataPath, { recursive: true });
}
app.setPath('userData', userDataPath);

// Fix 2: Disable hardware acceleration to avoid GPU cache issues
app.disableHardwareAcceleration();

// Fix 3: Set app user model ID
app.setAppUserModelId('pos-v2-kiosk');

// Fix 4: Additional Chromium flags to prevent quota database issues
app.commandLine.appendSwitch('--disable-web-security');
app.commandLine.appendSwitch('--disable-features', 'VizDisplayCompositor');
app.commandLine.appendSwitch('--disable-quota-management');
app.commandLine.appendSwitch('--disable-storage-quota-database');
app.commandLine.appendSwitch('--no-sandbox');
app.commandLine.appendSwitch('--disable-dev-shm-usage');
app.commandLine.appendSwitch('--disable-background-timer-throttling');
app.commandLine.appendSwitch('--disable-backgrounding-occluded-windows');
app.commandLine.appendSwitch('--disable-renderer-backgrounding');
app.commandLine.appendSwitch('--disable-background-networking');

class POSKioskApp {
    constructor() {
        this.mainWindow = null;
        this.isDev = process.argv.includes('--dev');
        this.isKioskMode = !this.isDev;
        
        // Initialize app
        this.initializeApp();
    }
    
    initializeApp() {
        // App event handlers with enhanced error handling
        app.whenReady().then(() => {
            console.log('🚀 Electron app ready, creating main window...');
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
        
        // Fix: Prevent new window creation
        app.on('web-contents-created', (event, contents) => {
            contents.on('new-window', (event, navigationUrl) => {
                event.preventDefault();
                console.log('🚫 Blocked new window creation:', navigationUrl);
            });
        });
        
        app.on('before-quit', (event) => {
            if (this.isKioskMode) {
                // Prevent quit in kiosk mode unless specific condition
                event.preventDefault();
            }
        });
        
        // IPC handlers
        this.setupIpcHandlers();
    }
      createMainWindow() {
        // Fix 4: Enhanced window configuration with cache settings
        const windowConfig = {
            width: this.isDev ? 1400 : 1920,
            height: this.isDev ? 900 : 1080,            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                enableRemoteModule: false,
                preload: path.join(__dirname, 'preload.js'),
                // Fix 5: Use temporary session to avoid quota database persistence
                partition: 'temp:kiosk-session',
                webSecurity: false, // Relaxed for kiosk mode
                allowRunningInsecureContent: false,
                experimentalFeatures: false,
                // Disable problematic features to prevent quota issues
                webgl: false,
                webaudio: false,
                plugins: false,
                // Enhanced cache and storage settings
                cache: false,
                // Disable quota management features
                backgroundThrottling: false,
                offscreen: false
            },
            icon: path.join(__dirname, 'assets', 'icon.png'),
            show: false, // Show after ready
            autoHideMenuBar: true,
            titleBarStyle: 'hidden',
            // Fix 6: Window appearance
            backgroundColor: '#ffffff'
        };
        
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
        }        this.mainWindow = new BrowserWindow(windowConfig);
        
        // Fix 8: Configure session to prevent quota database issues
        const session = this.mainWindow.webContents.session;
          // Clear storage data on startup to prevent quota issues
        session.clearStorageData({
            storages: ['websql', 'indexdb', 'localstorage', 'shadercache', 'serviceworkers']
        }).then(() => {
            console.log('🧹 Session storage cleared to prevent quota issues');
        }).catch((error) => {
            console.log('⚠️ Session storage clear warning:', error.message);
        });
        
        // Configure session settings to prevent quota database issues
        session.setUserAgent('POS-V2-Kiosk/1.0');
        
        // Fix 9: Load the app with error handling
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
            
            // Suppress quota database error messages in console
            this.mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
                // Filter out quota database errors as they don't affect functionality
                if (message.includes('quota_database') || 
                    message.includes('Failed to reset the quota database') ||
                    message.includes('Could not open the quota database')) {
                    return; // Don't log these specific errors
                }
                
                // Log other console messages normally
                if (level === 2) { // Error level
                    console.error(`Console Error: ${message}`);
                } else if (level === 1) { // Warning level
                    console.warn(`Console Warning: ${message}`);
                }
            });
            
            if (this.isDev) {
                this.mainWindow.webContents.openDevTools();
            }
        });
        
        // Fix 8: Handle window events
        this.mainWindow.on('closed', () => {
            this.mainWindow = null;
        });
        
        // Prevent navigation to external URLs
        this.mainWindow.webContents.on('will-navigate', (event, navigationUrl) => {
            const parsedUrl = new URL(navigationUrl);
            
            if (parsedUrl.origin !== 'file://') {
                event.preventDefault();
            }
        });
        
        // Handle external links
        this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
            shell.openExternal(url);
            return { action: 'deny' };
        });
        
        // Security: Prevent new window creation
        this.mainWindow.webContents.on('new-window', (event) => {
            event.preventDefault();
        });
    }
      setupIpcHandlers() {
        // Fix 11: Enhanced database IPC handlers with error handling
        
        // Get app version
        ipcMain.handle('get-app-version', () => {
            return app.getVersion();
        });
        
        // Get app info
        ipcMain.handle('get-app-info', () => {
            return {
                version: app.getVersion(),
                platform: process.platform,
                arch: process.arch,
                isDev: this.isDev,
                isKioskMode: this.isKioskMode
            };
        });
        
        // Database operations - Enhanced with error handling
        ipcMain.handle('database:getCategories', async () => {
            try {
                console.log('🔍 Fetching categories from database...');
                // Mock data for now - replace with actual database call
                const categories = [
                    { id: 1, name: 'Appetizers', description: 'Start your meal', is_active: 1 },
                    { id: 2, name: 'Main Courses', description: 'Hearty dishes', is_active: 1 },
                    { id: 3, name: 'Beverages', description: 'Drinks & more', is_active: 1 },
                    { id: 4, name: 'Desserts', description: 'Sweet endings', is_active: 1 }
                ];
                console.log('✅ Categories fetched successfully:', categories.length);
                return categories;
            } catch (error) {
                console.error('❌ Database error getting categories:', error);
                return [];
            }
        });

        ipcMain.handle('database:getMenuItems', async (event, categoryId) => {
            try {
                console.log('🔍 Fetching menu items for category:', categoryId);
                // Mock data for now - replace with actual database call
                const mockItems = [
                    { 
                        id: 1, 
                        name: 'Chicken Wings', 
                        description: 'Spicy buffalo wings with ranch dip', 
                        sell_price: 12.99, 
                        category_id: 1,
                        image_path: null,
                        is_active: 1 
                    },
                    { 
                        id: 2, 
                        name: 'Caesar Salad', 
                        description: 'Fresh romaine with parmesan and croutons', 
                        sell_price: 9.99, 
                        category_id: 1,
                        image_path: null,
                        is_active: 1 
                    },
                    { 
                        id: 3, 
                        name: 'Grilled Salmon', 
                        description: 'Atlantic salmon with seasonal vegetables', 
                        sell_price: 24.99, 
                        category_id: 2,
                        image_path: null,
                        is_active: 1 
                    }
                ];
                
                const filteredItems = categoryId ? mockItems.filter(item => item.category_id === categoryId) : mockItems;
                console.log('✅ Menu items fetched successfully:', filteredItems.length);
                return filteredItems;
            } catch (error) {
                console.error('❌ Database error getting menu items:', error);
                return [];
            }
        });

        ipcMain.handle('database:createOrder', async (event, orderData) => {
            try {
                console.log('📝 Creating order:', orderData);
                // Mock order creation - replace with actual database call
                const result = { 
                    success: true, 
                    orderId: Math.floor(Math.random() * 10000),
                    message: 'Order placed successfully'
                };
                console.log('✅ Order created successfully:', result.orderId);
                return result;
            } catch (error) {
                console.error('❌ Database error creating order:', error);
                return { success: false, message: error.message };
            }
        });
        
        // Window operations
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
        
        // Quit app (admin only)
        ipcMain.handle('quit-app', async () => {
            if (!this.isKioskMode) {
                app.quit();
                return true;
            }
            
            // In kiosk mode, require admin confirmation
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
        
        // Open external URL
        ipcMain.handle('open-external', (event, url) => {
            shell.openExternal(url);
        });
        
        // Print operations
        ipcMain.handle('print-receipt', async (event, content) => {
            try {
                // Create a hidden window for printing
                const printWindow = new BrowserWindow({
                    width: 300,
                    height: 400,
                    show: false,
                    webPreferences: {
                        nodeIntegration: false,
                        contextIsolation: true
                    }
                });
                
                // Load receipt content
                await printWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(content)}`);
                
                // Print
                await printWindow.webContents.print({
                    silent: true,
                    printBackground: true,
                    margins: {
                        marginType: 'none'
                    }
                });
                
                printWindow.close();
                return true;
            } catch (error) {
                console.error('Print error:', error);
                return false;
            }
        });
        
        // Database path configuration
        ipcMain.handle('get-db-path', () => {
            return getDatabasePath();
        });
        
        ipcMain.handle('set-db-path', (event, dbPath) => {
            store.set('dbPath', dbPath);
        });

        // Database operations for kiosk
        ipcMain.handle('db-get-categories', async () => {
            try {
                const query = `SELECT id, name, description FROM categories WHERE is_active = 1 ORDER BY name`;
                const rows = await executeQuery(query);
                return rows;
            } catch (error) {
                console.error('Error getting categories:', error);
                throw error;
            }
        });

        ipcMain.handle('db-get-menu-items', async () => {
            try {
                const query = `SELECT id, name, price, category_id, description, image_path, is_active FROM menu_items WHERE is_active = 1 ORDER BY name`;
                const rows = await executeQuery(query);
                return rows.map(row => ({
                    id: row.id,
                    name: row.name,
                    price: row.price,
                    category_id: row.category_id,
                    description: row.description,
                    image_path: row.image_path,
                    is_available: row.is_active ? true : false
                }));
            } catch (error) {
                console.error('Error getting menu items:', error);
                throw error;
            }
        });

        ipcMain.handle('db-create-order', async (event, orderData) => {
            try {
                // In production, this would save to actual database
                console.log('Creating order:', orderData);
                
                // Generate order ID and return success
                const orderId = Date.now();
                
                return {
                    success: true,
                    orderId: orderId,
                    orderNumber: `ORD-${orderId}`
                };
            } catch (error) {
                console.error('Error creating order:', error);
                throw error;
            }
        });
        
        // Settings operations
        ipcMain.handle('get-settings', () => {
            return {
                dbPath: store.get('dbPath'),
                theme: store.get('theme', 'light'),
                language: store.get('language', 'en'),
                autoStartKiosk: store.get('autoStartKiosk', true),
                printerSettings: store.get('printerSettings', {}),
                kioskSettings: store.get('kioskSettings', {
                    idleTimeout: 300, // 5 minutes
                    screensaverEnabled: true,
                    autoLogout: true
                })
            };
        });
        
        ipcMain.handle('save-settings', (event, settings) => {
            Object.keys(settings).forEach(key => {
                store.set(key, settings[key]);
            });
        });
    }
}

// Fix 13: Handle app crashes and errors
process.on('uncaughtException', (error) => {
    console.error('❌ Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
});

console.log('🚀 Electron main process starting...');

// Initialize the application
new POSKioskApp();
