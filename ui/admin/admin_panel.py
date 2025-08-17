import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from db.db_utils import get_db_connection
from datetime import datetime, date
import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from logic.utils import POSUtils
from logic.settings_manager import SettingsManager
from .menu_manager import MenuManagerTab
from .user_management import UserManagement
from .reports_screen import ReportsTab

class AdminPanel:
    def __init__(self, master, db_path):
        self.master = master
        self.db_path = db_path
        self.current_section = "dashboard"
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the modern admin panel UI"""
        # Clear all existing widgets from master window
        for widget in self.master.winfo_children():
            widget.destroy()
            
        # Configure main window
        self.master.configure(bg='#f8f9fa')
        self.master.title("POS Admin Panel")
        
        # Main container
        self.main_frame = tk.Frame(self.master, bg='#f8f9fa')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        self.create_header()
        
        # Create content area with sidebar and main content
        content_frame = tk.Frame(self.main_frame, bg='#f8f9fa')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create sidebar
        self.create_sidebar(content_frame)
        
        # Create main content area
        self.content_area = tk.Frame(content_frame, bg='white', relief=tk.RAISED, bd=1)
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        # Show dashboard by default
        self.show_dashboard()
    
    def create_header(self):
        """Create the header with title and user info"""
        header_frame = tk.Frame(self.main_frame, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame, text="🏪 POS Admin Panel", 
                              font=('Segoe UI', 18, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(side=tk.LEFT, padx=20, pady=25)
        
        # User info and logout
        user_frame = tk.Frame(header_frame, bg='#2c3e50')
        user_frame.pack(side=tk.RIGHT, padx=20, pady=25)
        
        user_label = tk.Label(user_frame, text="👤 Admin User", 
                             font=('Segoe UI', 12), 
                             fg='white', bg='#2c3e50')
        user_label.pack(side=tk.LEFT, padx=(0, 15))
        
        logout_btn = tk.Button(user_frame, text="🚪 Logout", 
                              command=self.logout,
                              font=('Segoe UI', 10),
                              bg='#e74c3c', fg='white',
                              relief=tk.FLAT, padx=15, pady=5,
                              cursor='hand2')
        logout_btn.pack(side=tk.RIGHT)
        
        # Add hover effect
        def on_enter(e):
            logout_btn.config(bg='#c0392b')
        def on_leave(e):
            logout_btn.config(bg='#e74c3c')
        
        logout_btn.bind("<Enter>", on_enter)
        logout_btn.bind("<Leave>", on_leave)
    
    def create_sidebar(self, parent):
        """Create the navigation sidebar"""
        sidebar = tk.Frame(parent, bg='#34495e', width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Sidebar title
        sidebar_title = tk.Label(sidebar, text="Navigation", 
                                font=('Segoe UI', 14, 'bold'),
                                fg='white', bg='#34495e')
        sidebar_title.pack(pady=20)
        
        # Navigation buttons
        nav_items = [
            ("📊 Dashboard", "dashboard"),
            ("🍽️ Menu Management", "menu"),
            ("👥 User Accounts", "users"),
            ("💰 Financial Reports", "financial"),
            ("📋 Orders History", "orders"),
            ("⚙️ Settings", "settings")
        ]
        
        self.nav_buttons = {}
        for text, section in nav_items:
            btn = tk.Button(sidebar, text=text, 
                          command=lambda s=section: self.switch_section(s),
                          font=('Segoe UI', 11),
                          bg='#34495e', fg='white',
                          relief=tk.FLAT, anchor='w',
                          padx=20, pady=12,
                          cursor='hand2',
                          width=25)
            btn.pack(fill=tk.X, padx=10, pady=2)
            
            # Add hover effects
            def on_enter(e, button=btn):
                if button['bg'] != '#3498db':
                    button.config(bg='#4a6078')
            def on_leave(e, button=btn):
                if button['bg'] != '#3498db':
                    button.config(bg='#34495e')
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
            self.nav_buttons[section] = btn
        
        # Set dashboard as active
        self.nav_buttons['dashboard'].config(bg='#3498db')
    
    def switch_section(self, section):
        """Switch to different section"""
        try:
            # Reset all button colors
            for btn in self.nav_buttons.values():
                btn.config(bg='#34495e')
            
            # Highlight current section
            if section in self.nav_buttons:
                self.nav_buttons[section].config(bg='#3498db')
            
            # Clear content area
            for widget in self.content_area.winfo_children():
                widget.destroy()
            
            # Show selected section
            if section == "dashboard":
                self.show_dashboard()
            elif section == "menu":
                self.show_menu_management()
            elif section == "users":
                self.show_user_management()
            elif section == "financial":
                self.show_financial_reports()
            elif section == "orders":
                self.show_orders_history()
            elif section == "settings":
                self.show_settings()
            else:
                # Fallback for unknown sections
                self.show_error_section(f"Unknown section: {section}")
                return
            
            self.current_section = section
            
        except Exception as e:
            self.show_error_section(f"Navigation error: {str(e)}")
    
    def show_error_section(self, error_message):
        """Show error section when navigation fails"""
        error_frame = tk.Frame(self.content_area, bg='white')
        error_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Error icon and message
        error_label = tk.Label(error_frame, text="⚠️", font=('Segoe UI', 48), 
                              bg='white', fg='#e74c3c')
        error_label.pack(pady=(50, 20))
        
        error_text = tk.Label(error_frame, text=error_message,
                             font=('Segoe UI', 14), bg='white', fg='#e74c3c')
        error_text.pack(pady=10)
        
        # Retry button
        retry_btn = tk.Button(error_frame, text="🔄 Return to Dashboard",
                             command=lambda: self.switch_section("dashboard"),
                             font=('Segoe UI', 12),
                             bg='#3498db', fg='white',
                             relief=tk.FLAT, padx=20, pady=10,
                             cursor='hand2')
        retry_btn.pack(pady=20)
    
    def show_dashboard(self):
        """Show the dashboard with statistics"""
        # Header
        header = tk.Label(self.content_area, text="📊 Dashboard Overview", 
                         font=('Segoe UI', 16, 'bold'),
                         bg='white', fg='#2c3e50')
        header.pack(pady=20)
        
        # Statistics cards
        cards_frame = tk.Frame(self.content_area, bg='white')
        cards_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Get today's stats
        today_stats = self.get_today_stats()
        
        # Create stat cards
        stats = [
            ("📋 Orders Today", str(today_stats['orders']), "#3498db"),
            ("💰 Total Sales", POSUtils.format_currency(today_stats['revenue']), "#27ae60"),
            ("🏷️ Tax Collected", POSUtils.format_currency(today_stats['tax']), "#e67e22"),
            ("📊 Average Order", POSUtils.format_currency(today_stats['avg_order']), "#9b59b6")
        ]
        
        for i, (title, value, color) in enumerate(stats):
            card = tk.Frame(cards_frame, bg=color, relief=tk.RAISED, bd=2)
            card.grid(row=0, column=i, padx=10, pady=10, sticky='ew')
            
            title_label = tk.Label(card, text=title, 
                                  font=('Segoe UI', 10, 'bold'),
                                  fg='white', bg=color)
            title_label.pack(pady=(15, 5))
            
            value_label = tk.Label(card, text=value, 
                                  font=('Segoe UI', 14, 'bold'),
                                  fg='white', bg=color)
            value_label.pack(pady=(0, 15))
        
        # Configure grid weights
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1)
        
        # Quick actions
        actions_frame = tk.LabelFrame(self.content_area, text="Quick Actions", 
                                     font=('Segoe UI', 12, 'bold'),
                                     bg='white', fg='#2c3e50',
                                     padx=20, pady=15)
        actions_frame.pack(fill=tk.X, padx=20, pady=20)
        
        action_buttons = [
            ("🍽️ Manage Menu", lambda: self.switch_section("menu")),
            ("👥 Manage Users", lambda: self.switch_section("users")),
            ("📊 View Reports", lambda: self.switch_section("financial")),
            ("🏥 System Health", self.show_health_check)
        ]
        
        for i, (text, command) in enumerate(action_buttons):
            btn = tk.Button(actions_frame, text=text, command=command,
                           font=('Segoe UI', 11),
                           bg='#ecf0f1', fg='#2c3e50',
                           relief=tk.FLAT, padx=20, pady=10,
                           cursor='hand2')
            btn.grid(row=0, column=i, padx=10, pady=10, sticky='ew')
            
            # Hover effects
            def on_enter(e, button=btn):
                button.config(bg='#bdc3c7')
            def on_leave(e, button=btn):
                button.config(bg='#ecf0f1')
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        
        for i in range(4):
            actions_frame.grid_columnconfigure(i, weight=1)
    
    def show_menu_management(self):
        """Show menu management interface"""
        try:
            # Clear content area first
            for widget in self.content_area.winfo_children():
                widget.destroy()
            
            # Show loading indicator
            loading_frame = tk.Frame(self.content_area, bg='white')
            loading_frame.pack(fill=tk.BOTH, expand=True)
            
            loading_label = tk.Label(loading_frame, text="🔄 Loading Menu Management...",
                                   font=('Segoe UI', 14),
                                   bg='white', fg='#3498db')
            loading_label.pack(expand=True)
            
            # Update the display
            self.master.update()
            
            # Clear loading and show actual interface
            for widget in self.content_area.winfo_children():
                widget.destroy()
                
            MenuManagerTab(self.content_area)
            
        except Exception as e:
            # Clear loading and show error
            for widget in self.content_area.winfo_children():
                widget.destroy()
            
            self.show_error_section(f"Failed to load menu management: {str(e)}")
    
    def show_user_management(self):
        """Show user management interface"""
        try:
            # Clear content area first
            for widget in self.content_area.winfo_children():
                widget.destroy()
            
            # Show loading indicator
            loading_frame = tk.Frame(self.content_area, bg='white')
            loading_frame.pack(fill=tk.BOTH, expand=True)
            
            loading_label = tk.Label(loading_frame, text="🔄 Loading User Management...",
                                   font=('Segoe UI', 14),
                                   bg='white', fg='#3498db')
            loading_label.pack(expand=True)
            
            # Update the display
            self.master.update()
            
            # Clear loading and show actual interface
            for widget in self.content_area.winfo_children():
                widget.destroy()
                
            UserManagement(self.content_area, self.db_path)
            
        except Exception as e:
            # Clear loading and show error
            for widget in self.content_area.winfo_children():
                widget.destroy()
            
            self.show_error_section(f"Failed to load user management: {str(e)}")
    
    def show_financial_reports(self):
        """Show financial reports interface"""
        try:
            # Clear content area first
            for widget in self.content_area.winfo_children():
                widget.destroy()
            
            # Show loading indicator
            loading_frame = tk.Frame(self.content_area, bg='white')
            loading_frame.pack(fill=tk.BOTH, expand=True)
            
            loading_label = tk.Label(loading_frame, text="🔄 Loading Financial Reports...",
                                   font=('Segoe UI', 14),
                                   bg='white', fg='#3498db')
            loading_label.pack(expand=True)
            
            # Update the display
            self.master.update()
            
            # Clear loading and show actual interface
            for widget in self.content_area.winfo_children():
                widget.destroy()
                
            ReportsTab(self.content_area)
            
        except Exception as e:
            # Clear loading and show error
            for widget in self.content_area.winfo_children():
                widget.destroy()
            
            self.show_error_section(f"Failed to load financial reports: {str(e)}")
    
    def show_orders_history(self):
        """Show orders history interface"""
        header = tk.Label(self.content_area, text="📋 Orders History", 
                         font=('Segoe UI', 16, 'bold'),
                         bg='white', fg='#2c3e50')
        header.pack(pady=20)
        
        orders_frame = tk.Frame(self.content_area, bg='white')
        orders_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ('Order Number', 'Date', 'Customer', 'Items', 'Total', 'Status')
        self.orders_tree = ttk.Treeview(orders_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=120, anchor='center')

        self.orders_tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(orders_frame, orient=tk.VERTICAL, command=self.orders_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)

        self.load_orders()
    
    def show_settings(self):
        """Show settings interface"""
        header = tk.Label(self.content_area, text="⚙️ System Settings", 
                         font=('Segoe UI', 16, 'bold'),
                         bg='white', fg='#2c3e50')
        header.pack(pady=20)
        
        settings_frame = tk.Frame(self.content_area, bg='white')
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ('Key', 'Value', 'Description')
        self.settings_tree = ttk.Treeview(settings_frame, columns=columns, show='headings', height=12)

        for col in columns:
            self.settings_tree.heading(col, text=col)
            width = 150 if col != 'Description' else 250
            self.settings_tree.column(col, width=width, anchor='center')

        self.settings_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(settings_frame, orient=tk.VERTICAL, command=self.settings_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.settings_tree.configure(yscrollcommand=scrollbar.set)
        self.settings_tree.bind('<<TreeviewSelect>>', self.on_setting_select)

        edit_frame = tk.LabelFrame(self.content_area, text='Edit Setting', font=('Segoe UI', 12, 'bold'), bg='white', fg='#2c3e50', padx=20, pady=15)
        edit_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        tk.Label(edit_frame, text='Key:', bg='white').grid(row=0, column=0, sticky='w')
        self.setting_key_var = tk.StringVar()
        tk.Entry(edit_frame, textvariable=self.setting_key_var, state='readonly', width=40).grid(row=0, column=1, padx=10, pady=5, sticky='w')

        tk.Label(edit_frame, text='Value:', bg='white').grid(row=1, column=0, sticky='w')
        self.setting_value_var = tk.StringVar()
        tk.Entry(edit_frame, textvariable=self.setting_value_var, width=40).grid(row=1, column=1, padx=10, pady=5, sticky='w')

        save_btn = tk.Button(edit_frame, text='Save', command=self.save_setting, bg='#3498db', fg='white', relief=tk.FLAT, cursor='hand2')
        save_btn.grid(row=2, column=0, columnspan=2, pady=10)

        self.load_settings()

    def load_orders(self):
        """Load orders from the database into the treeview"""
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = '''
                SELECT o.order_number,
                       DATE(o.created_at) as order_date,
                       COALESCE(o.customer_name, ''),
                       (SELECT COUNT(*) FROM order_items oi WHERE oi.order_id = o.id) as items_count,
                       o.total_amount,
                       o.status
                FROM orders o
                ORDER BY o.created_at DESC
            '''
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()

            for order_number, order_date, customer, items_count, total, status in rows:
                self.orders_tree.insert('', tk.END, values=(
                    order_number,
                    order_date,
                    customer,
                    items_count,
                    POSUtils.format_currency(total),
                    status.capitalize()
                ))
        except sqlite3.Error as e:
            print(f"Database error in load_orders: {e}")

    def load_settings(self):
        """Load settings from database"""
        for item in self.settings_tree.get_children():
            self.settings_tree.delete(item)

        settings = SettingsManager.get_all_settings()
        for setting in settings:
            self.settings_tree.insert('', tk.END, values=(
                setting['key'],
                setting['value'],
                setting.get('description', '')
            ))

    def on_setting_select(self, event):
        """Populate fields with selected setting"""
        selected = self.settings_tree.selection()
        if selected:
            values = self.settings_tree.item(selected[0])['values']
            self.setting_key_var.set(values[0])
            self.setting_value_var.set(values[1])

    def save_setting(self):
        """Save changes to selected setting"""
        key = self.setting_key_var.get().strip()
        value = self.setting_value_var.get()
        if not key:
            messagebox.showerror("Error", "No setting selected")
            return

        if SettingsManager.set_setting(key, value):
            messagebox.showinfo("Success", "Setting updated successfully")
            self.load_settings()
        else:
            messagebox.showerror("Error", "Failed to update setting")
    
    def get_today_stats(self):
        """Get today's statistics from database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            today = date.today().strftime('%Y-%m-%d')
            
            # Get orders count and revenue for today
            cursor.execute("""
                SELECT COUNT(*), COALESCE(SUM(total_amount), 0), COALESCE(SUM(tax_amount), 0)
                FROM orders 
                WHERE DATE(created_at) = ?
            """, (today,))
            
            orders, revenue, tax = cursor.fetchone()
            orders = orders or 0
            revenue = revenue or 0.0
            tax = tax or 0.0
            
            # Calculate average order value
            avg_order = revenue / orders if orders > 0 else 0.0
            
            conn.close()
            
            return {
                'orders': orders,
                'revenue': revenue,
                'tax': tax,
                'avg_order': avg_order
            }
            
        except sqlite3.Error as e:
            print(f"Database error in get_today_stats: {e}")
            return {
                'orders': 0,
                'revenue': 0.0,
                'tax': 0.0,
                'avg_order': 0.0
            }
    
    def show_health_check(self):
        """Show system health check interface"""
        # Clear content area first
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Label(self.content_area, text="🏥 System Health Check", 
                         font=('Segoe UI', 16, 'bold'),
                         bg='white', fg='#2c3e50')
        header.pack(pady=20)
        
        # Health check content frame
        health_frame = tk.Frame(self.content_area, bg='white')
        health_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Run health check button
        check_btn = tk.Button(health_frame, text="🔍 Run Health Check",
                             command=self.run_health_check,
                             font=('Segoe UI', 12, 'bold'),
                             bg='#3498db', fg='white',
                             relief=tk.FLAT, padx=20, pady=10,
                             cursor='hand2')
        check_btn.pack(pady=20)
        
        # Results area
        self.health_results_frame = tk.Frame(health_frame, bg='white')
        self.health_results_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Auto-run health check
        self.run_health_check()
    
    def run_health_check(self):
        """Run health check and display results"""
        # Clear previous results
        for widget in self.health_results_frame.winfo_children():
            widget.destroy()
        
        # Show loading
        loading_label = tk.Label(self.health_results_frame, text="🔄 Running health check...",
                               font=('Segoe UI', 12),
                               bg='white', fg='#3498db')
        loading_label.pack(pady=10)
        
        # Update display
        self.master.update()
        
        try:
            from logic.health_check import HealthChecker
            all_passed, results = HealthChecker.run_full_health_check()
            
            # Clear loading
            loading_label.destroy()
            
            # Overall status
            status_color = '#27ae60' if all_passed else '#e74c3c'
            status_text = "✅ System is healthy" if all_passed else "⚠️ Issues detected"
            
            status_label = tk.Label(self.health_results_frame, text=status_text,
                                  font=('Segoe UI', 14, 'bold'),
                                  bg='white', fg=status_color)
            status_label.pack(pady=10)
            
            # Individual check results
            for name, passed, message in results:
                result_frame = tk.Frame(self.health_results_frame, bg='white')
                result_frame.pack(fill=tk.X, pady=5, padx=20)
                
                status_icon = "✅" if passed else "❌"
                color = '#27ae60' if passed else '#e74c3c'
                
                result_text = f"{status_icon} {name}: {message}"
                result_label = tk.Label(result_frame, text=result_text,
                                      font=('Segoe UI', 11),
                                      bg='white', fg=color,
                                      anchor='w')
                result_label.pack(fill=tk.X)
            
            # Recommendations
            if not all_passed:
                rec_frame = tk.Frame(self.health_results_frame, bg='#fff3cd', relief=tk.RAISED, bd=1)
                rec_frame.pack(fill=tk.X, pady=20, padx=20)
                
                rec_title = tk.Label(rec_frame, text="🔧 Recommended Actions:",
                                   font=('Segoe UI', 12, 'bold'),
                                   bg='#fff3cd', fg='#856404')
                rec_title.pack(anchor='w', padx=10, pady=(10, 5))
                
                recommendations = [
                    "• Check database file permissions",
                    "• Restart the application",
                    "• Run validation script: python3 validate_fixes.py",
                    "• Check troubleshooting guide: TROUBLESHOOTING.md"
                ]
                
                for rec in recommendations:
                    rec_label = tk.Label(rec_frame, text=rec,
                                       font=('Segoe UI', 10),
                                       bg='#fff3cd', fg='#856404',
                                       anchor='w')
                    rec_label.pack(anchor='w', padx=20, pady=2)
                
                # Add spacing
                tk.Label(rec_frame, text="", bg='#fff3cd').pack(pady=5)
        
        except Exception as e:
            # Clear loading
            loading_label.destroy()
            
            error_label = tk.Label(self.health_results_frame, 
                                 text=f"❌ Health check failed: {str(e)}",
                                 font=('Segoe UI', 12),
                                 bg='white', fg='#e74c3c')
            error_label.pack(pady=10)
    
    def logout(self):
        """Return to startup screen"""
        try:
            from ui.startup_screen import StartupScreen
            StartupScreen(self.master)
        except Exception as e:
            # Fallback if startup screen fails
            messagebox.showerror("Navigation Error", 
                               f"Cannot return to main menu: {str(e)}\n\n"
                               f"Please restart the application.")
            # Clear current content and show basic menu
            for widget in self.master.winfo_children():
                widget.destroy()
            
            # Create basic restart interface
            restart_frame = tk.Frame(self.master, bg='#f8f9fa')
            restart_frame.pack(fill=tk.BOTH, expand=True)
            
            message_label = tk.Label(restart_frame, 
                                   text="⚠️ Navigation Error\n\nPlease restart the application",
                                   font=('Segoe UI', 16),
                                   bg='#f8f9fa', fg='#e74c3c')
            message_label.pack(expand=True)
            
            restart_btn = tk.Button(restart_frame, text="🔄 Restart Application",
                                  command=self.master.quit,
                                  font=('Segoe UI', 12),
                                  bg='#3498db', fg='white',
                                  relief=tk.FLAT, padx=20, pady=10)
            restart_btn.pack(pady=20)
