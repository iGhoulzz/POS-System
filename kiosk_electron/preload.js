const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // App information
    getAppVersion: () => ipcRenderer.invoke('get-app-version'),
    getAppInfo: () => ipcRenderer.invoke('get-app-info'),
    
    // Store operations
    store: {
        get: (key) => ipcRenderer.invoke('store-get', key),
        set: (key, value) => ipcRenderer.invoke('store-set', key, value),
        delete: (key) => ipcRenderer.invoke('store-delete', key),
        clear: () => ipcRenderer.invoke('store-clear')
    },
    
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
    
    // External operations
    openExternal: (url) => ipcRenderer.invoke('open-external', url),
    
    // Print operations
    print: {
        receipt: (content) => ipcRenderer.invoke('print-receipt', content)
    },
      // Database operations
    database: {
        getPath: () => ipcRenderer.invoke('get-db-path'),
        setPath: (path) => ipcRenderer.invoke('set-db-path', path),
        getCategories: () => ipcRenderer.invoke('db-get-categories'),
        getMenuItems: () => ipcRenderer.invoke('db-get-menu-items'),
        createOrder: (orderData) => ipcRenderer.invoke('db-create-order', orderData)
    },
    
    // Settings operations
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
