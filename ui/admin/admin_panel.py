import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime, date
import os
import sys
import subprocess

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from logic.utils import POSUtils
from logic.order_manager import OrderManager
from logic.invoice_printer import InvoicePrinter
from .menu_manager import MenuManagerTab
from .user_management import UserManagement
from .reports_screen import ReportsTab

class AdminPanel:
    def __init__(self, master, db_path, user=None):
        self.master = master
        self.db_path = db_path
        self.user = user
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
        
        user_display = self.user.get('full_name', 'Admin User') if self.user else 'Admin User'
        user_label = tk.Label(user_frame, text=f"👤 {user_display}", 
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
        # Reset all button colors
        for btn in self.nav_buttons.values():
            btn.config(bg='#34495e')
        
        # Highlight current section
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
        
        self.current_section = section
    
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
            ("📊 View Reports", lambda: self.switch_section("financial"))
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
        
        for i in range(3):
            actions_frame.grid_columnconfigure(i, weight=1)
    
    def show_menu_management(self):
        """Show menu management interface"""
        # Clear content area first
        for widget in self.content_area.winfo_children():
            widget.destroy()
        MenuManagerTab(self.content_area)
    
    def show_user_management(self):
        """Show user management interface"""
        # Clear content area first
        for widget in self.content_area.winfo_children():
            widget.destroy()
        UserManagement(self.content_area, self.db_path)
    
    def show_financial_reports(self):
        """Show financial reports interface"""
        # Clear content area first
        for widget in self.content_area.winfo_children():
            widget.destroy()
        ReportsTab(self.content_area)
    
    def show_orders_history(self):
        """Show orders history interface with real data"""
        self._orders_auto_refresh = True

        # Header row
        header_frame = tk.Frame(self.content_area, bg='white')
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        tk.Label(header_frame, text="📋 Orders History",
                 font=('Segoe UI', 16, 'bold'),
                 bg='white', fg='#2c3e50').pack(side=tk.LEFT)

        # Refresh button
        refresh_btn = tk.Button(header_frame, text="🔄 Refresh",
                                command=self._refresh_orders,
                                font=('Segoe UI', 10),
                                bg='#3498db', fg='white',
                                relief=tk.FLAT, padx=10, pady=3, cursor='hand2')
        refresh_btn.pack(side=tk.RIGHT, padx=5)

        # Date filter
        filter_frame = tk.Frame(self.content_area, bg='white')
        filter_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        tk.Label(filter_frame, text="Filter:", font=('Segoe UI', 10),
                 bg='white', fg='#2c3e50').pack(side=tk.LEFT, padx=(0, 5))

        self._order_filter_var = tk.StringVar(value='today')
        filter_combo = ttk.Combobox(filter_frame, textvariable=self._order_filter_var,
                                    values=['today', 'this_week', 'this_month', 'all'],
                                    state='readonly', width=15)
        filter_combo.pack(side=tk.LEFT)
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self._refresh_orders())

        # Orders treeview
        tree_frame = tk.Frame(self.content_area, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        columns = ('order_number', 'date', 'customer', 'type', 'total', 'tax', 'status')
        self._orders_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        col_config = [
            ('order_number', 'Order #', 130),
            ('date', 'Date / Time', 150),
            ('customer', 'Customer', 130),
            ('type', 'Type', 80),
            ('total', 'Total', 100),
            ('tax', 'Tax', 80),
            ('status', 'Status', 90)
        ]
        for col_id, heading, width in col_config:
            self._orders_tree.heading(col_id, text=heading)
            self._orders_tree.column(col_id, width=width, anchor='center')

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self._orders_tree.yview)
        self._orders_tree.configure(yscrollcommand=scrollbar.set)
        self._orders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Action buttons
        actions_frame = tk.Frame(self.content_area, bg='white')
        actions_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        view_btn = tk.Button(actions_frame, text="📄 View Details",
                             command=self._view_order_details,
                             font=('Segoe UI', 10), bg='#2ecc71', fg='white',
                             relief=tk.FLAT, padx=15, pady=5, cursor='hand2')
        view_btn.pack(side=tk.LEFT, padx=5)

        print_btn = tk.Button(actions_frame, text="🖨️ Print Invoice",
                              command=self._print_order_invoice,
                              font=('Segoe UI', 10), bg='#e67e22', fg='white',
                              relief=tk.FLAT, padx=15, pady=5, cursor='hand2')
        print_btn.pack(side=tk.LEFT, padx=5)

        status_btn = tk.Button(actions_frame, text="✅ Mark Completed",
                               command=self._mark_order_completed,
                               font=('Segoe UI', 10), bg='#9b59b6', fg='white',
                               relief=tk.FLAT, padx=15, pady=5, cursor='hand2')
        status_btn.pack(side=tk.LEFT, padx=5)

        # Load orders
        self._refresh_orders()

        # Start auto-refresh
        self._schedule_orders_refresh()

    def _get_date_range(self):
        """Get date range based on filter selection"""
        from datetime import timedelta
        today = date.today()
        filter_val = self._order_filter_var.get() if hasattr(self, '_order_filter_var') else 'today'

        if filter_val == 'today':
            return today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
        elif filter_val == 'this_week':
            start = today - timedelta(days=today.weekday())
            return start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
        elif filter_val == 'this_month':
            start = today.replace(day=1)
            return start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
        else:  # all
            return '2000-01-01', today.strftime('%Y-%m-%d')

    def _refresh_orders(self):
        """Fetch and display orders from the database"""
        if not hasattr(self, '_orders_tree'):
            return
        try:
            # Clear tree
            for item in self._orders_tree.get_children():
                self._orders_tree.delete(item)

            start_date, end_date = self._get_date_range()

            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.id, o.order_number, o.created_at, o.customer_name,
                       o.order_type, o.total_amount, o.tax_amount, o.status
                FROM orders o
                WHERE DATE(o.created_at) BETWEEN ? AND ?
                ORDER BY o.created_at DESC
            """, (start_date, end_date))
            orders = cursor.fetchall()
            conn.close()

            for order in orders:
                oid = order['id']
                order_num = order['order_number'] or f'#{oid}'
                created = order['created_at'] or ''
                customer = order['customer_name'] or 'Walk-in'
                o_type = (order['order_type'] or '').replace('_', ' ').title()
                total = POSUtils.format_currency(order['total_amount'] or 0)
                tax = POSUtils.format_currency(order['tax_amount'] or 0)
                status = (order['status'] or 'pending').title()

                tag = 'completed' if status == 'Completed' else 'pending' if status == 'Pending' else ''
                self._orders_tree.insert('', tk.END, iid=str(oid),
                                        values=(order_num, created, customer, o_type, total, tax, status),
                                        tags=(tag,))

            self._orders_tree.tag_configure('completed', foreground='#27ae60')
            self._orders_tree.tag_configure('pending', foreground='#e67e22')

        except Exception as e:
            print(f"Error loading orders: {e}")

    def _schedule_orders_refresh(self):
        """Auto-refresh orders every 30 seconds"""
        if hasattr(self, '_orders_auto_refresh') and self._orders_auto_refresh and self.current_section == 'orders':
            self._refresh_orders()
            self.content_area.after(30000, self._schedule_orders_refresh)

    def _get_selected_order_id(self):
        """Get the selected order ID from the treeview"""
        selection = self._orders_tree.selection()
        if not selection:
            from tkinter import messagebox
            messagebox.showwarning("Warning", "Please select an order first.")
            return None
        return int(selection[0])

    def _view_order_details(self):
        """Show order details in a popup"""
        from tkinter import messagebox
        order_id = self._get_selected_order_id()
        if not order_id:
            return

        order = OrderManager.get_order_by_id(order_id)
        items = OrderManager.get_order_items(order_id)

        if not order:
            messagebox.showerror("Error", "Order not found.")
            return

        # Build detail window
        detail_win = tk.Toplevel(self.master)
        detail_win.title(f"Order Details — {order['order_number']}")
        detail_win.geometry("500x450")
        detail_win.configure(bg='white')
        detail_win.resizable(False, False)
        detail_win.grab_set()

        # Order info
        info_frame = tk.Frame(detail_win, bg='white', padx=20, pady=15)
        info_frame.pack(fill=tk.X)

        info_lines = [
            ("Order #:", order['order_number']),
            ("Date:", order.get('created_at', '')),
            ("Customer:", order.get('customer_name', 'Walk-in') or 'Walk-in'),
            ("Type:", (order.get('order_type', '') or '').replace('_', ' ').title()),
            ("Payment:", order.get('payment_method', 'N/A') or 'N/A'),
            ("Status:", (order.get('status', 'pending') or 'pending').title()),
        ]
        for label, value in info_lines:
            row = tk.Frame(info_frame, bg='white')
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=label, font=('Segoe UI', 10, 'bold'),
                     bg='white', fg='#2c3e50', width=12, anchor='w').pack(side=tk.LEFT)
            tk.Label(row, text=str(value), font=('Segoe UI', 10),
                     bg='white', fg='#555').pack(side=tk.LEFT)

        # Items table
        tk.Label(detail_win, text="Order Items", font=('Segoe UI', 12, 'bold'),
                 bg='white', fg='#2c3e50').pack(pady=(10, 5))

        items_frame = tk.Frame(detail_win, bg='white')
        items_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        item_cols = ('item', 'qty', 'price', 'total')
        items_tree = ttk.Treeview(items_frame, columns=item_cols, show='headings', height=8)
        for cid, heading, w in [('item', 'Item', 200), ('qty', 'Qty', 50),
                                 ('price', 'Price', 80), ('total', 'Total', 80)]:
            items_tree.heading(cid, text=heading)
            items_tree.column(cid, width=w, anchor='center' if cid != 'item' else 'w')

        for it in items:
            items_tree.insert('', tk.END, values=(
                it.get('item_name', 'Unknown'),
                it.get('quantity', 0),
                POSUtils.format_currency(it.get('unit_price', 0)),
                POSUtils.format_currency(it.get('total_price', 0))
            ))
        items_tree.pack(fill=tk.BOTH, expand=True)

        # Totals
        totals_frame = tk.Frame(detail_win, bg='#f0f0f0', padx=20, pady=10)
        totals_frame.pack(fill=tk.X)
        tax_amt = order.get('tax_amount', 0) or 0
        total_amt = order.get('total_amount', 0) or 0
        subtotal = total_amt - tax_amt
        tk.Label(totals_frame, text=f"Subtotal: {POSUtils.format_currency(subtotal)}   |   "
                 f"Tax: {POSUtils.format_currency(tax_amt)}   |   "
                 f"Total: {POSUtils.format_currency(total_amt)}",
                 font=('Segoe UI', 11, 'bold'), bg='#f0f0f0', fg='#2c3e50').pack()

        tk.Button(detail_win, text="Close", command=detail_win.destroy,
                  font=('Segoe UI', 10), bg='#e74c3c', fg='white',
                  relief=tk.FLAT, padx=20, pady=5, cursor='hand2').pack(pady=10)

    def _print_order_invoice(self):
        """Generate and open PDF invoice for selected order"""
        from tkinter import messagebox
        order_id = self._get_selected_order_id()
        if not order_id:
            return

        order = OrderManager.get_order_by_id(order_id)
        items = OrderManager.get_order_items(order_id)

        if not order:
            messagebox.showerror("Error", "Order not found.")
            return

        try:
            os.makedirs("receipts", exist_ok=True)
            receipt_path = f"receipts/receipt_{order['order_number']}.pdf"
            printer = InvoicePrinter()
            if printer.generate_receipt_pdf(order, items, receipt_path):
                messagebox.showinfo("Success", f"Invoice saved to:\n{receipt_path}")
                if sys.platform == 'win32':
                    os.startfile(receipt_path)
                elif sys.platform == 'darwin':
                    subprocess.Popen(['open', receipt_path])
                else:
                    subprocess.Popen(['xdg-open', receipt_path])
            else:
                messagebox.showerror("Error", "Failed to generate invoice PDF.")
        except Exception as e:
            messagebox.showerror("Error", f"Invoice error: {e}")

    def _mark_order_completed(self):
        """Mark a selected order as completed"""
        from tkinter import messagebox
        order_id = self._get_selected_order_id()
        if not order_id:
            return

        if messagebox.askyesno("Confirm", "Mark this order as completed?"):
            if OrderManager.update_order_status(order_id, 'completed'):
                messagebox.showinfo("Success", "Order marked as completed.")
                self._refresh_orders()
            else:
                messagebox.showerror("Error", "Failed to update order status.")
    
    def show_settings(self):
        """Show settings interface"""
        header = tk.Label(self.content_area, text="⚙️ System Settings", 
                         font=('Segoe UI', 16, 'bold'),
                         bg='white', fg='#2c3e50')
        header.pack(pady=20)
        
        # Settings content (placeholder)
        settings_frame = tk.LabelFrame(self.content_area, text="General Settings", 
                                      font=('Segoe UI', 12, 'bold'),
                                      bg='white', fg='#2c3e50',
                                      padx=20, pady=15)
        settings_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(settings_frame, text="Settings panel coming soon...", 
                font=('Segoe UI', 12),
                bg='white', fg='#7f8c8d').pack(pady=20)
    
    def get_today_stats(self):
        """Get today's statistics from database"""
        try:
            conn = sqlite3.connect(self.db_path)
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
    
    def logout(self):
        """Return to startup screen"""
        from ui.startup_screen import StartupScreen
        StartupScreen(self.master)
