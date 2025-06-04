# POS-V2 Point of Sale System

<div align="center">

![POS-V2 Logo](kiosk_electron/assets/images/logo.svg)

**A Modern, Comprehensive Point of Sale System**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Electron](https://img.shields.io/badge/Electron-27.0+-green.svg)](https://electronjs.org)
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightblue.svg)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

## 🚀 Overview

POS-V2 is a comprehensive point of sale system designed for restaurants, cafes, and retail businesses. It features dual interfaces: a robust Python desktop application for administrative tasks and a modern Electron kiosk interface for streamlined point-of-sale operations.

### ✨ Key Features

- 🛒 **Complete POS Operations** - Full point of sale workflow
- 👥 **Role-based Access Control** - Admin, Cashier, Kitchen roles
- 🍽️ **Kitchen Display System** - Real-time order tracking
- 📊 **Comprehensive Reporting** - Sales analytics and business insights
- 🧾 **Receipt Generation** - PDF and thermal printer support
- 💰 **Expense Management** - Business expense tracking
- 🎨 **Modern UI** - Multiple themes and responsive design
- 🔐 **Secure Authentication** - Encrypted passwords and session management

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐
│   Python App    │    │  Electron App   │
│   (Admin UI)    │    │   (Kiosk UI)    │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          └──────────┬───────────┘
                     │
            ┌────────▼────────┐
            │  SQLite Database │
            │   (Shared Data)  │
            └─────────────────┘
```

### Technology Stack

- **Backend:** Python 3.8+, SQLite
- **Desktop UI:** Tkinter with custom styling
- **Kiosk UI:** Electron with HTML5/CSS3/JavaScript
- **Database:** SQLite with IndexedDB for client storage
- **Printing:** ESC/POS thermal printers, PDF generation
- **Security:** SHA256 password hashing, role-based access

## 📦 Installation

### Prerequisites

- **Python 3.8 or higher** - [Download Python](https://python.org/downloads/)
- **Node.js 16 or higher** - [Download Node.js](https://nodejs.org/downloads/)
- **Windows 10/11** (primary support, cross-platform capable)

### Quick Installation

#### Option 1: Using Startup Scripts (Recommended)

1. **Clone or download** the project to your desired location
2. **For Python App:**
   ```powershell
   cd "path\to\POS-V2"
   .\start_pos.bat
   ```
3. **For Electron Kiosk:**
   ```powershell
   cd "path\to\POS-V2\kiosk_electron"
   .\start_kiosk.bat
   ```

#### Option 2: Manual Setup

**Python Application:**
```powershell
# Navigate to project directory
cd "c:\Users\User\Desktop\POS-V2"

# Install Python dependencies
python -m pip install -r requirements.txt

# Initialize database
python db\init_db.py

# Start the application
python main.py
```

**Electron Kiosk:**
```powershell
# Navigate to kiosk directory
cd "c:\Users\User\Desktop\POS-V2\kiosk_electron"

# Install dependencies
npm install

# Start the application
npm start
```

## 🎯 Getting Started

### Default Login

After installation, use these credentials to access the system:

- **Username:** `admin`
- **Password:** `admin123`
- **Role:** Administrator (full access)

### First Steps

1. **Launch the Application** using the startup scripts
2. **Login** with the default admin credentials
3. **Configure Business Settings** (name, address, tax rates)
4. **Add Menu Categories** and items
5. **Create User Accounts** for your staff
6. **Start Processing Orders**

## 🖥️ User Interfaces

### Python Desktop Application
- **Admin Panel** - Complete system administration
- **Menu Management** - Add/edit menu items and categories
- **User Management** - Staff account administration
- **Reports** - Sales analytics and business reports
- **Expense Tracking** - Business expense management
- **Settings** - System configuration

### Electron Kiosk Interface
- **POS Terminal** - Streamlined order processing
- **Kitchen Display** - Real-time order tracking
- **Admin Dashboard** - Quick administrative access
- **Multi-theme Support** - Light, dark, and blue themes
- **Touch-friendly** - Optimized for touch screens

## 📊 Features Overview

### Order Management
- ✅ Add items to cart with quantities
- ✅ Apply discounts and tax calculations
- ✅ Multiple payment methods (cash, card, etc.)
- ✅ Customer information tracking
- ✅ Order status workflow (Pending → Preparing → Ready → Completed)
- ✅ Receipt generation and printing

### Kitchen Operations
- ✅ Real-time order display
- ✅ Order status updates
- ✅ Wait time tracking
- ✅ Priority alerts for urgent orders
- ✅ Auto-refresh functionality

### Reporting & Analytics
- ✅ Daily, weekly, monthly sales reports
- ✅ Expense tracking and categorization
- ✅ Profit/loss analysis
- ✅ CSV export for external analysis
- ✅ Real-time dashboard statistics

### User Management
- ✅ Role-based access control
- ✅ Secure password management
- ✅ Session tracking and timeout
- ✅ User activity logging

## 🔧 Configuration

### Database Configuration
Edit `config.py` to modify database settings:
```python
DATABASE_NAME = 'pos_system.db'
DATABASE_PATH = 'db'
```

### System Settings
Access system settings through the admin panel to configure:
- Business information (name, address, phone)
- Tax rates and calculations
- Receipt templates and formatting
- User permissions and roles

### Themes
The Electron interface supports multiple themes:
- **Light Theme** - Clean, bright interface
- **Dark Theme** - Easy on the eyes for long use
- **Blue Theme** - Professional business look

## 📁 Project Structure

```
POS-V2/
├── config.py                 # System configuration
├── main.py                   # Python app entry point
├── requirements.txt          # Python dependencies
├── start_pos.bat            # Windows startup script
├── test_system.py           # System validation tests
├── IMPLEMENTATION_STATUS.md  # Detailed status report
├── README.md                # This file
│
├── db/                      # Database layer
│   ├── init_db.py          # Database initialization
│   ├── db_utils.py         # Database utilities
│   └── pos_system.db       # SQLite database
│
├── logic/                   # Business logic
│   ├── user_manager.py     # User authentication
│   ├── order_manager.py    # Order processing
│   ├── invoice_printer.py  # Receipt generation
│   ├── report_generator.py # Analytics
│   ├── settings_manager.py # Configuration
│   └── utils.py            # Utility functions
│
├── ui/admin/               # Python UI components
│   ├── login_screen.py     # Authentication interface
│   ├── admin_panel.py      # Main dashboard
│   ├── pos_screen.py       # POS interface
│   ├── kitchen_display.py  # Kitchen orders
│   ├── menu_manager.py     # Menu management
│   ├── reports_screen.py   # Reporting interface
│   ├── expenses_screen.py  # Expense management
│   └── user_management.py  # User administration
│
└── kiosk_electron/         # Electron kiosk app
    ├── main.js             # Electron main process
    ├── preload.js          # Security preload script
    ├── package.json        # Node dependencies
    ├── start_kiosk.bat     # Windows startup script
    │
    ├── assets/images/      # Application assets
    │
    └── renderer/           # Frontend interface
        ├── index.html      # Main HTML
        ├── css/            # Stylesheets
        └── js/             # JavaScript modules
```

## 🛡️ Security

### Authentication
- **SHA256 Password Hashing** - Secure password storage
- **Role-based Access Control** - Three permission levels
- **Session Management** - Automatic timeout and logout
- **Input Validation** - SQL injection prevention

### Data Protection
- **SQLite Database** - ACID compliance and reliability
- **Backup Support** - Easy database backup and restore
- **Error Handling** - Comprehensive error catching
- **Audit Trail** - User activity logging

## 🔧 Troubleshooting

### Common Issues

**Database Connection Errors**
```powershell
# Reinitialize the database
python db\init_db.py
```

**Missing Dependencies**
```powershell
# Reinstall Python packages
python -m pip install -r requirements.txt --force-reinstall

# Reinstall Node packages
cd kiosk_electron
npm install --force
```

**Permission Issues**
- Run as Administrator if file access is denied
- Check that the `db` directory is writable

### Support

For technical support or feature requests:
1. Check the troubleshooting section above
2. Review the implementation status document
3. Examine the log files for error details

## 📈 Performance

### System Requirements
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 500MB for application, additional for data
- **CPU:** Any modern processor (x64 recommended)
- **Network:** Not required for local operation

### Optimization Tips
- Regular database maintenance (built-in)
- Periodic log file cleanup
- Monitor storage usage for large order volumes
- Use SSD storage for better performance

## 🚀 Deployment

### Production Deployment

1. **System Requirements Check**
   - Verify Python and Node.js installations
   - Ensure sufficient disk space
   - Check user permissions

2. **Database Setup**
   - Initialize fresh database for production
   - Configure backup procedures
   - Set up proper file permissions

3. **Configuration**
   - Update business information
   - Configure tax rates and regions
   - Set up user accounts and roles
   - Customize receipt templates

4. **Testing**
   - Run system validation tests
   - Process test orders
   - Verify receipt printing
   - Test all user roles and permissions

5. **Go Live**
   - Train staff on system usage
   - Monitor initial operations
   - Establish backup procedures

## 📋 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

This is a complete implementation designed for production use. The system is feature-complete and ready for deployment.

## 📞 Support

**System Status:** ✅ Production Ready  
**Last Updated:** June 2, 2025  
**Version:** 2.0.0  

---

<div align="center">

**POS-V2 - Modern Point of Sale System**  
*Built with Python, Electron, and SQLite*

⭐ **Ready for Production Use** ⭐

</div>
