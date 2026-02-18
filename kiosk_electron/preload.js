const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // App information
    getAppVersion: () => ipcRenderer.invoke('get-app-version'),
    getAppInfo: () => ipcRenderer.invoke('get-app-info'),

    // Window operations
    window: {
        minimize: () => ipcRenderer.invoke('minimize-window'),
        maximize: () => ipcRenderer.invoke('maximize-window'),
        close: () => ipcRenderer.invoke('close-window'),
        toggleFullscreen: () => ipcRenderer.invoke('toggle-fullscreen')
    },

    // App operations
    app: {
        restart: () => ipcRenderer.invoke('restart-app'),
        quit: () => ipcRenderer.invoke('quit-app')
    },

    // Dialog operations
    dialog: {
        showError: (title, content) => ipcRenderer.invoke('show-error', title, content),
        showMessage: (options) => ipcRenderer.invoke('show-message', options)
    },

    // Print operations
    print: {
        receipt: (content) => ipcRenderer.invoke('print-receipt', content)
    },

    // Database operations (real SQLite via main process)
    database: {
        getCategories: () => ipcRenderer.invoke('db-get-categories'),
        getMenuItems: () => ipcRenderer.invoke('db-get-menu-items'),
        createOrder: (orderData) => ipcRenderer.invoke('db-create-order', orderData),
        getSettings: () => ipcRenderer.invoke('db-get-settings')
    },

    // App-level settings (electron-store)
    settings: {
        get: () => ipcRenderer.invoke('get-settings'),
        save: (settings) => ipcRenderer.invoke('save-settings', settings)
    }
});

// Expose Node.js APIs for development mode only
contextBridge.exposeInMainWorld('nodeAPI', {
    platform: process.platform,
    versions: process.versions
});
