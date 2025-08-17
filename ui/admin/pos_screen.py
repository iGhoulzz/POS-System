"""
Point of Sale Screen - Cashier interface
"""

import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List
import datetime
from logic.order_manager import OrderManager
from logic.settings_manager import SettingsManager
from logic.invoice_printer import InvoicePrinter
from logic.utils import POSUtils
from db.db_utils import execute_query_dict

class POSTab:
    def __init__(self, parent: ttk.Frame, user: Dict):
        self.parent = parent
        self.user = user
        self.cart_items = []
        self.current_order = None
        self.held_orders: List[Dict] = []
        self.current_category_id = None
        self.search_var = tk.StringVar()
        self.setup_ui()
        self.load_categories()
        self.load_menu_items()
    
    def setup_ui(self):
        """Setup the POS interface"""
        # Configure modern styles with enhanced colors and fonts
        style = ttk.Style()
        
        # Set theme to modern appearance
        try:
            style.theme_use('clam')  # Modern flat theme
        except:
            pass
        
        # Enhanced style configurations
        style.configure('Header.TLabelFrame', 
                       font=('Segoe UI', 12, 'bold'), 
                       foreground='#2c3e50',
                       background='#ecf0f1')
        
        style.configure('Category.TButton', 
                       font=('Segoe UI', 10, 'bold'), 
                       padding=(12, 8),
                       foreground='#ffffff',
                       background='#3498db')
        
        style.map('Category.TButton',
                 background=[('active', '#2980b9'),
                            ('pressed', '#1f618d')])
        
        style.configure('Item.TButton', 
                       font=('Segoe UI', 9), 
                       padding=(8, 6),
                       foreground='#2c3e50',
                       background='#bdc3c7')
        
        style.map('Item.TButton',
                 background=[('active', '#95a5a6'),
                            ('pressed', '#7f8c8d')])
        
        style.configure('Action.TButton', 
                       font=('Segoe UI', 11, 'bold'), 
                       padding=(15, 10),
                       foreground='#ffffff',
                       background='#27ae60')
        
        style.map('Action.TButton',
                 background=[('active', '#229954'),
                            ('pressed', '#1e8449')])
        
        style.configure('Danger.TButton', 
                       font=('Segoe UI', 10, 'bold'), 
                       padding=(12, 8),
                       foreground='#ffffff',
                       background='#e74c3c')
        
        style.map('Danger.TButton',
                 background=[('active', '#c0392b'),
                            ('pressed', '#a93226')])
        
        style.configure('Payment.TButton', 
                       font=('Segoe UI', 12, 'bold'), 
                       padding=(20, 12),
                       foreground='#ffffff',
                       background='#f39c12')
        
        style.map('Payment.TButton',
                 background=[('active', '#e67e22'),
                            ('pressed', '#d35400')])
        
        # Configure treeview for modern appearance
        style.configure('Modern.Treeview',
                       background='#ffffff',
                       foreground='#2c3e50',
                       fieldbackground='#ffffff',
                       font=('Segoe UI', 10))
        
        style.configure('Modern.Treeview.Heading',
                       background='#34495e',
                       foreground='#ffffff',
                       font=('Segoe UI', 10, 'bold'))
        
        # Main container with modern header bar
        header_frame = ttk.Frame(self.parent)
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        # Enhanced header with user info and styling
        header_content = ttk.Frame(header_frame)
        header_content.pack(fill=tk.X)
        
        # User info with icon
        user_frame = ttk.Frame(header_content)
        user_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Add user icon (using Unicode symbol)
        user_icon = ttk.Label(user_frame, text="👤", font=('Segoe UI', 16))
        user_icon.pack(side=tk.LEFT, padx=(0, 8))
        
        user_info_frame = ttk.Frame(user_frame)
        user_info_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        cashier_label = ttk.Label(user_info_frame, text="Cashier:", 
                                 font=('Segoe UI', 10))
        cashier_label.pack(anchor=tk.W)
        
        user_name_label = ttk.Label(user_info_frame, 
                                   text=f"{self.user.get('full_name', 'Unknown')}", 
                                   font=('Segoe UI', 14, 'bold'),
                                   foreground='#2c3e50')
        user_name_label.pack(anchor=tk.W)
        
        # Add current time display
        self.time_label = ttk.Label(header_content, font=('Segoe UI', 12), 
                                   foreground='#7f8c8d')
        self.time_label.pack(side=tk.RIGHT, padx=(10, 0))
        self.update_time()
        
        # Add logout button with enhanced styling
        logout_btn = ttk.Button(header_content, text="🚪 Logout", style='Danger.TButton',
                               command=self.logout)
        logout_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Main paned window with better proportions
        paned_window = ttk.PanedWindow(self.parent, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Left panel - Menu items
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=2)
        
        # Categories frame with modern styling
        cat_frame = ttk.LabelFrame(left_frame, text="🍽️ Categories", 
                                  style='Header.TLabelFrame')
        cat_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.cat_buttons_frame = ttk.Frame(cat_frame)
        self.cat_buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Menu items frame with modern styling
        items_frame = ttk.LabelFrame(left_frame, text="🛒 Menu Items",
                                   style='Header.TLabelFrame')
        items_frame.pack(fill=tk.BOTH, expand=True)

        # Search bar for fast item lookup
        search_frame = ttk.Frame(items_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        ttk.Label(search_frame, text="🔎 Search:", font=('Segoe UI', 10)).pack(side=tk.LEFT)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        search_entry.bind('<Return>', lambda e: self.search_items())
        ttk.Button(search_frame, text="Go", command=self.search_items,
                  style='Action.TButton').pack(side=tk.LEFT)
        ttk.Button(search_frame, text="Reset", command=self.reset_search,
                  style='Danger.TButton').pack(side=tk.LEFT, padx=(5, 0))

        # Create scrollable frame for menu items
        canvas = tk.Canvas(items_frame, bg='#ffffff', highlightthickness=0)
        scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=canvas.yview)
        self.items_scrollable_frame = ttk.Frame(canvas)
        
        self.items_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.items_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Right panel - Cart and checkout
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)
        
        # Order info frame with enhanced styling
        order_info_frame = ttk.LabelFrame(right_frame, text="📋 Order Information",
                                        style='Header.TLabelFrame')
        order_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_grid = ttk.Frame(order_info_frame)
        info_grid.pack(fill=tk.X, padx=15, pady=15)
        
        # Customer name with icon
        customer_frame = ttk.Frame(info_grid)
        customer_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
        
        ttk.Label(customer_frame, text="👤 Customer:", 
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        self.customer_var = tk.StringVar()
        self.customer_entry = ttk.Entry(customer_frame, textvariable=self.customer_var, 
                                       font=('Segoe UI', 10), width=25)
        self.customer_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Order type with icon
        type_frame = ttk.Frame(info_grid)
        type_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
        
        ttk.Label(type_frame, text="🏪 Order Type:", 
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        self.order_type_var = tk.StringVar(value="dine_in")
        order_type_combo = ttk.Combobox(type_frame, textvariable=self.order_type_var, 
                                       values=["dine_in", "takeout", "delivery"], 
                                       state="readonly", font=('Segoe UI', 10), width=22)
        order_type_combo.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        info_grid.columnconfigure(1, weight=1)
        
        # Cart frame with enhanced styling
        cart_frame = ttk.LabelFrame(right_frame, text="🛒 Shopping Cart",
                                  style='Header.TLabelFrame')
        cart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Cart treeview with modern styling
        cart_columns = ('Item', 'Qty', 'Price', 'Total')
        self.cart_tree = ttk.Treeview(cart_frame, columns=cart_columns, show='headings', 
                                     height=8, style='Modern.Treeview')
        
        # Configure column headings and widths
        column_configs = {
            'Item': {'text': '🍽️ Item', 'width': 180},
            'Qty': {'text': '#', 'width': 50},
            'Price': {'text': '💰 Price', 'width': 80},
            'Total': {'text': '💵 Total', 'width': 80}
        }
        
        for col, config in column_configs.items():
            self.cart_tree.heading(col, text=config['text'])
            self.cart_tree.column(col, width=config['width'], anchor=tk.CENTER if col != 'Item' else tk.W)
        
        cart_scrollbar = ttk.Scrollbar(cart_frame, orient=tk.VERTICAL, command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)

        self.cart_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.cart_tree.bind('<Double-1>', self.edit_cart_item)
        cart_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Cart buttons with enhanced styling
        cart_buttons_frame = ttk.Frame(cart_frame)
        cart_buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(cart_buttons_frame, text="➖ Remove Item", 
                  command=self.remove_cart_item, style='Action.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(cart_buttons_frame, text="🗑️ Clear Cart", 
                  command=self.clear_cart, style='Danger.TButton').pack(side=tk.LEFT)
        
        # Totals frame with enhanced styling
        totals_frame = ttk.LabelFrame(right_frame, text="💰 Order Total",
                                    style='Header.TLabelFrame')
        totals_frame.pack(fill=tk.X, pady=(0, 10))
        
        totals_grid = ttk.Frame(totals_frame)
        totals_grid.pack(fill=tk.X, padx=15, pady=15)
        
        # Subtotal
        ttk.Label(totals_grid, text="Subtotal:", font=("Segoe UI", 11)).grid(row=0, column=0, sticky=tk.W, pady=3)
        self.subtotal_label = ttk.Label(totals_grid, text="$0.00", font=("Segoe UI", 12, 'bold'),
                                       foreground='#27ae60')
        self.subtotal_label.grid(row=0, column=1, sticky=tk.E, pady=3)
        
        # Tax
        ttk.Label(totals_grid, text="Tax:", font=("Segoe UI", 11)).grid(row=1, column=0, sticky=tk.W, pady=3)
        self.tax_label = ttk.Label(totals_grid, text="$0.00", font=("Segoe UI", 12, 'bold'),
                                  foreground='#f39c12')
        self.tax_label.grid(row=1, column=1, sticky=tk.E, pady=3)
        
        # Add separator line
        separator = ttk.Separator(totals_grid, orient=tk.HORIZONTAL)
        separator.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E, pady=8)
        
        # Total
        ttk.Label(totals_grid, text="TOTAL:", font=("Segoe UI", 14, "bold"),
                 foreground='#2c3e50').grid(row=3, column=0, sticky=tk.W, pady=3)
        self.total_label = ttk.Label(totals_grid, text="$0.00", font=("Segoe UI", 16, "bold"),
                                    foreground='#e74c3c')
        self.total_label.grid(row=3, column=1, sticky=tk.E, pady=3)
        
        totals_grid.columnconfigure(1, weight=1)
        
        # Payment frame with enhanced styling
        payment_frame = ttk.LabelFrame(right_frame, text="💳 Payment Options",
                                     style='Header.TLabelFrame')
        payment_frame.pack(fill=tk.X)
        
        payment_grid = ttk.Frame(payment_frame)
        payment_grid.pack(fill=tk.X, padx=15, pady=15)
        
        # Payment method with icon
        method_frame = ttk.Frame(payment_grid)
        method_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.E, pady=10)
        
        ttk.Label(method_frame, text="💳 Payment Method:", 
                 font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        self.payment_method_var = tk.StringVar(value="cash")
        payment_combo = ttk.Combobox(method_frame, textvariable=self.payment_method_var,
                                   values=["cash", "card", "check"], state="readonly", 
                                   font=('Segoe UI', 10), width=15)
        payment_combo.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Checkout buttons with enhanced styling
        checkout_frame = ttk.Frame(payment_grid)
        checkout_frame.grid(row=1, column=0, columnspan=2, pady=15)
        
        ttk.Button(checkout_frame, text="💰 Process Order",
                  command=self.process_order, style="Payment.TButton").pack(fill=tk.X, pady=(0, 8))
        ttk.Button(checkout_frame, text="⏸️ Hold Order",
                  command=self.hold_order, style='Action.TButton').pack(fill=tk.X, pady=(0, 8))
        ttk.Button(checkout_frame, text="▶️ Resume Held Order",
                  command=self.resume_held_order, style='Action.TButton').pack(fill=tk.X, pady=(0, 8))
        ttk.Button(checkout_frame, text="❌ Cancel Order",
                  command=self.cancel_order, style='Danger.TButton').pack(fill=tk.X)
    
    def update_time(self):
        """Update the time display"""
        if hasattr(self, 'time_label'):
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            current_date = datetime.datetime.now().strftime("%m/%d/%Y")
            self.time_label.config(text=f"{current_date}\n{current_time}")
            # Schedule next update
            self.parent.after(1000, self.update_time)
    
    def load_categories(self):
        """Load categories as buttons"""
        # Clear existing category buttons
        for widget in self.cat_buttons_frame.winfo_children():
            widget.destroy()
        
        try:
            # Check database connection first
            from db.db_utils import get_db_connection
            
            # Test connection
            conn = get_db_connection()
            conn.execute("SELECT 1")
            conn.close()
            
            query = "SELECT id, name FROM categories WHERE is_active = 1 ORDER BY name"
            categories = execute_query_dict(query, fetch='all') or []
            
            # Add "All" button with modern styling
            all_btn = ttk.Button(self.cat_buttons_frame, text="📋 All Items",
                               command=lambda: self.load_menu_items(None),
                               style='Category.TButton')
            all_btn.pack(side=tk.LEFT, padx=(0, 8), pady=5)
            
            # Add category buttons with modern styling
            for cat in categories:
                btn = ttk.Button(self.cat_buttons_frame, text=f"🏷️ {cat['name']}",
                               command=lambda c=cat['id']: self.load_menu_items(c),
                               style='Category.TButton')
                btn.pack(side=tk.LEFT, padx=(0, 8), pady=5)
                
        except sqlite3.OperationalError as e:
            error_msg = f"Database error: {str(e)}"
            messagebox.showerror("Database Error", f"Failed to load categories: {error_msg}")
            # Add fallback button
            error_btn = ttk.Button(self.cat_buttons_frame, text="⚠️ Database Error - Click to Retry",
                                 command=self.load_categories,
                                 style='Category.TButton')
            error_btn.pack(side=tk.LEFT, padx=(0, 8), pady=5)
        except Exception as e:
            error_msg = f"Failed to load categories: {str(e)}"
            messagebox.showerror("Error", error_msg)
            # Add fallback button
            retry_btn = ttk.Button(self.cat_buttons_frame, text="🔄 Error - Click to Retry",
                                 command=self.load_categories,
                                 style='Category.TButton')
            retry_btn.pack(side=tk.LEFT, padx=(0, 8), pady=5)
    
    def load_menu_items(self, category_id=None, search_query=None):
        """Load menu items as buttons"""
        self.current_category_id = category_id
        if search_query is None:
            self.search_var.set('')
        
        # Clear existing item buttons
        for widget in self.items_scrollable_frame.winfo_children():
            widget.destroy()

        try:
            # Check database connection first
            from db.db_utils import get_db_connection
            
            # Test connection
            conn = get_db_connection()
            conn.execute("SELECT 1")
            conn.close()
            
            params = []
            search_clause = ''
            if search_query:
                search_clause = ' AND name LIKE ?'
                params.append(f"%{search_query}%")

            if category_id:
                query = f'''
                    SELECT id, name, price, description
                    FROM menu_items
                    WHERE category_id = ? AND is_active = 1{search_clause}
                    ORDER BY name
                '''
                params.insert(0, category_id)
                items = execute_query_dict(query, tuple(params), 'all') or []
            else:
                query = f'''
                    SELECT id, name, price, description
                    FROM menu_items
                    WHERE is_active = 1{search_clause}
                    ORDER BY name
                '''
                items = execute_query_dict(query, tuple(params), 'all') or []
            
            # If no items found, show a message
            if not items:
                no_items_label = tk.Label(self.items_scrollable_frame, 
                                        text="No products available in this category",
                                        font=('Segoe UI', 12),
                                        fg='#7f8c8d',
                                        bg='white')
                no_items_label.grid(row=0, column=0, columnspan=3, pady=20)
                return
            
            # Create item buttons in grid with enhanced styling
            row = 0
            col = 0
            max_cols = 3
            
            for item in items:
                item_frame = ttk.Frame(self.items_scrollable_frame, relief=tk.RAISED, borderwidth=1)
                item_frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
                
                # Item button with enhanced styling
                btn_text = f"🍽️ {item['name']}\n💰 {POSUtils.format_currency(item['price'])}"
                if item.get('description'):
                    btn_text += f"\n📝 {item['description'][:30]}..."
                
                item_btn = ttk.Button(item_frame, text=btn_text, width=18,
                                    command=lambda i=item: self.add_to_cart(i),
                                    style='Item.TButton')
                item_btn.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            # Configure column weights
            for i in range(max_cols):
                self.items_scrollable_frame.columnconfigure(i, weight=1)
                
        except sqlite3.OperationalError as e:
            error_msg = f"Database error: {str(e)}"
            messagebox.showerror("Database Error", f"Failed to load products: {error_msg}")
            # Add fallback error label
            error_label = tk.Label(self.items_scrollable_frame, 
                                 text="Failed to load products - Database connection error",
                                 font=('Segoe UI', 12),
                                 fg='#e74c3c',
                                 bg='white')
            error_label.grid(row=0, column=0, columnspan=3, pady=20)
        except Exception as e:
            error_msg = f"Failed to load products: {str(e)}"
            messagebox.showerror("Error", error_msg)
            # Add fallback error label
            error_label = tk.Label(self.items_scrollable_frame, 
                                 text="Failed to load products - Please try again",
                                 font=('Segoe UI', 12),
                                 fg='#e74c3c',
                                 bg='white')
            error_label.grid(row=0, column=0, columnspan=3, pady=20)

    def search_items(self):
        """Search menu items based on the search entry"""
        query = self.search_var.get().strip()
        self.load_menu_items(self.current_category_id, query)

    def reset_search(self):
        """Reset search field and reload items"""
        self.search_var.set('')
        self.load_menu_items(self.current_category_id)
    
    def add_to_cart(self, item):
        """Add item to cart"""
        # Check if item already in cart
        for cart_item in self.cart_items:
            if cart_item['menu_item_id'] == item['id']:
                cart_item['quantity'] += 1
                cart_item['total_price'] = cart_item['quantity'] * cart_item['unit_price']
                break
        else:
            # Add new item to cart
            cart_item = {
                'menu_item_id': item['id'],
                'name': item['name'],
                'quantity': 1,
                'unit_price': item['price'],
                'total_price': item['price'],
                'special_instructions': ''
            }
            self.cart_items.append(cart_item)
        
        self.update_cart_display()
        self.update_totals()
    
    def remove_cart_item(self):
        """Remove selected item from cart"""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        
        # Get selected item index
        item_index = self.cart_tree.index(selection[0])
        
        # Remove from cart
        del self.cart_items[item_index]

        self.update_cart_display()
        self.update_totals()

    def edit_cart_item(self, event=None):
        """Open a popup to edit quantity or instructions for a cart item"""
        selection = self.cart_tree.selection()
        if not selection:
            return

        index = self.cart_tree.index(selection[0])
        cart_item = self.cart_items[index]

        top = tk.Toplevel(self.parent)
        top.title("Edit Item")
        top.resizable(False, False)
        top.grab_set()

        frame = ttk.Frame(top)
        frame.pack(padx=20, pady=20)

        qty_var = tk.IntVar(value=cart_item['quantity'])
        instr_var = tk.StringVar(value=cart_item.get('special_instructions', ''))

        ttk.Label(frame, text="Quantity:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky=tk.W)
        qty_spin = ttk.Spinbox(frame, from_=1, to=99, textvariable=qty_var, width=5)
        qty_spin.grid(row=0, column=1, pady=(0, 10), sticky=tk.W)

        ttk.Label(frame, text="Instructions:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky=tk.W)
        instr_entry = ttk.Entry(frame, textvariable=instr_var, width=30)
        instr_entry.grid(row=1, column=1, pady=(0, 10), sticky=tk.W)

        def save():
            cart_item['quantity'] = max(1, qty_var.get())
            cart_item['special_instructions'] = instr_var.get().strip()
            cart_item['total_price'] = cart_item['quantity'] * cart_item['unit_price']
            self.update_cart_display()
            self.update_totals()
            top.destroy()

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(btn_frame, text="Save", command=save, style='Action.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Cancel", command=top.destroy, style='Danger.TButton').pack(side=tk.LEFT)
    
    def clear_cart(self):
        """Clear all items from cart"""
        if self.cart_items and messagebox.askyesno("Confirm", "Clear all items from cart?"):
            self.cart_items.clear()
            self.update_cart_display()
            self.update_totals()
    
    def update_cart_display(self):
        """Update cart treeview display"""
        # Clear existing items
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Add cart items
        for cart_item in self.cart_items:
            self.cart_tree.insert('', 'end', values=(
                cart_item['name'],
                cart_item['quantity'],
                POSUtils.format_currency(cart_item['unit_price']),
                POSUtils.format_currency(cart_item['total_price'])
            ))
    
    def update_totals(self):
        """Update order totals"""
        subtotal = sum(item['total_price'] for item in self.cart_items)
        tax_rate = SettingsManager.get_tax_rate()
        tax_amount, total_amount = POSUtils.calculate_total_with_tax(subtotal, tax_rate)
        
        self.subtotal_label.config(text=POSUtils.format_currency(subtotal))
        self.tax_label.config(text=POSUtils.format_currency(tax_amount))
        self.total_label.config(text=POSUtils.format_currency(total_amount))
    
    def process_order(self):
        """Process the current order"""
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty")
            return
        
        try:
            # Create order
            customer_name = self.customer_var.get().strip() or None
            order_type = self.order_type_var.get()
            payment_method = self.payment_method_var.get()
            tax_rate = SettingsManager.get_tax_rate()
            
            order_id = OrderManager.create_order(
                customer_name=customer_name,
                order_type=order_type,
                items=self.cart_items,
                payment_method=payment_method,
                created_by=self.user['id'],
                tax_rate=tax_rate
            )
            
            if order_id:
                # Get order details for receipt
                order = OrderManager.get_order_by_id(order_id)
                order_items = OrderManager.get_order_items(order_id)
                
                # Print receipt
                self.print_receipt(order, order_items)
                
                # Clear cart
                self.cart_items.clear()
                self.customer_var.set("")
                self.update_cart_display()
                self.update_totals()
                
                messagebox.showinfo("Success", f"Order {order['order_number']} processed successfully!")
            else:
                messagebox.showerror("Error", "Failed to create order")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process order: {str(e)}")
    
    def hold_order(self):
        """Hold the current order for later"""
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty")
            return

        held = {
            'customer': self.customer_var.get().strip(),
            'order_type': self.order_type_var.get(),
            'payment_method': self.payment_method_var.get(),
            'items': [item.copy() for item in self.cart_items]
        }
        self.held_orders.append(held)

        self.clear_cart()
        self.customer_var.set("")
        messagebox.showinfo("Info", "Order held successfully")

    def resume_held_order(self):
        """Resume a previously held order"""
        if not self.held_orders:
            messagebox.showinfo("Info", "No held orders")
            return

        top = tk.Toplevel(self.parent)
        top.title("Resume Held Order")
        top.geometry("500x400")
        top.resizable(False, False)

        # Center the window
        top.transient(self.parent)
        top.grab_set()

        frame = ttk.Frame(top)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Select an order to resume:", 
                 font=('Segoe UI', 12, 'bold')).pack(pady=(0, 10))

        listbox = tk.Listbox(frame, font=('Segoe UI', 10))
        for idx, order in enumerate(self.held_orders):
            customer = order['customer'] or 'Guest'
            total = sum(i['total_price'] for i in order['items'])
            listbox.insert(tk.END, f"Order #{idx + 1}: {customer} - {POSUtils.format_currency(total)}")
        listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        def load_selected():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("Warning", "Please select an order to resume")
                return
            index = sel[0]
            data = self.held_orders.pop(index)

            self.cart_items = [item.copy() for item in data['items']]
            self.customer_var.set(data['customer'])
            self.order_type_var.set(data['order_type'])
            self.payment_method_var.set(data['payment_method'])

            self.update_cart_display()
            self.update_totals()
            top.destroy()

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Resume Selected Order", 
                  command=load_selected, style='Action.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", 
                  command=top.destroy, style='Danger.TButton').pack(side=tk.LEFT)
    
    def cancel_order(self):
        """Cancel the current order"""
        if self.cart_items and messagebox.askyesno("Confirm", "Cancel current order?"):
            self.clear_cart()
            self.customer_var.set("")
    
    def print_receipt(self, order, order_items):
        """Print receipt for order"""
        try:
            printer = InvoicePrinter()
            
            # Save receipt as PDF
            receipt_path = f"receipts/receipt_{order['order_number']}.pdf"
            os.makedirs("receipts", exist_ok=True)
            
            if printer.generate_receipt_pdf(order, order_items, receipt_path):
                # Option to view receipt
                if messagebox.askyesno("Receipt", "Receipt saved. Would you like to view it?"):
                    os.startfile(receipt_path)  # Windows
            
        except Exception as e:
            print(f"Error printing receipt: {e}")
    
    def logout(self):
        """Logout and return to login screen"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            # Clear any current order
            if self.cart_items:
                self.cart_items.clear()
                self.update_cart_display()
                self.update_totals()
            
            # Find the toplevel window and close it
            current_window = self.parent
            while current_window and not isinstance(current_window, tk.Toplevel):
                current_window = current_window.master
            
            if current_window:
                current_window.destroy()
                
            # Restore the main login window
            # Find root window
            root = self.parent
            while root.master:
                root = root.master
            
            if hasattr(root, 'deiconify'):
                root.deiconify()  # Show login window again
            else:
                # Create new login window if needed
                from ui.admin.login_screen import LoginScreen
                new_root = tk.Tk()
                LoginScreen(new_root)
                new_root.mainloop()


class POSWindow:
    """Standalone POS window"""
    def __init__(self, parent: tk.Toplevel, user: Dict):
        self.parent = parent
        self.user = user
        self.setup_window()
        
        # Create POS tab
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.pos_tab = POSTab(main_frame, user)
    
    def setup_window(self):
        """Setup the POS window"""
        self.parent.title(f"🛒 Point of Sale - {self.user.get('full_name', 'Cashier')}")
        
        # Set window icon if possible
        try:
            self.parent.iconbitmap(default="assets/pos_icon.ico")
        except:
            pass
        
        # Get screen dimensions for responsive sizing
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        
        # Set window to 85% of screen size to prevent cutting
        window_width = min(1400, int(screen_width * 0.85))
        window_height = min(900, int(screen_height * 0.85))
        
        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.parent.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.parent.resizable(True, True)
        self.parent.minsize(1000, 600)  # Minimum size to prevent UI cutting
        
        # Configure window background
        self.parent.configure(bg='#ecf0f1')
        
        # Optionally maximize for better experience
        try:
            self.parent.state('zoomed')  # Windows maximize
        except:
            pass  # Fallback for other systems
