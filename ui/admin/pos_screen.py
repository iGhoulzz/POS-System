"""
Point of Sale Screen - Cashier interface
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List
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
        self.setup_ui()
        self.load_categories()
        self.load_menu_items()
    
    def setup_ui(self):
        """Setup the POS interface"""
        # Main paned window
        paned_window = ttk.PanedWindow(self.parent, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Menu items
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=2)
        
        # Categories frame
        cat_frame = ttk.LabelFrame(left_frame, text="Categories")
        cat_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.cat_buttons_frame = ttk.Frame(cat_frame)
        self.cat_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Menu items frame
        items_frame = ttk.LabelFrame(left_frame, text="Menu Items")
        items_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable frame for menu items
        canvas = tk.Canvas(items_frame)
        scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=canvas.yview)
        self.items_scrollable_frame = ttk.Frame(canvas)
        
        self.items_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.items_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # Right panel - Cart and checkout
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)
        
        # Order info frame
        order_info_frame = ttk.LabelFrame(right_frame, text="Order Information")
        order_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_grid = ttk.Frame(order_info_frame)
        info_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Customer name
        ttk.Label(info_grid, text="Customer:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.customer_var = tk.StringVar()
        self.customer_entry = ttk.Entry(info_grid, textvariable=self.customer_var, width=20)
        self.customer_entry.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Order type
        ttk.Label(info_grid, text="Type:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.order_type_var = tk.StringVar(value="dine_in")
        order_type_combo = ttk.Combobox(info_grid, textvariable=self.order_type_var, 
                                       values=["dine_in", "takeout", "delivery"], 
                                       state="readonly", width=17)
        order_type_combo.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Cart frame
        cart_frame = ttk.LabelFrame(right_frame, text="Cart")
        cart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Cart treeview
        cart_columns = ('Item', 'Qty', 'Price', 'Total')
        self.cart_tree = ttk.Treeview(cart_frame, columns=cart_columns, show='headings', height=10)
        
        for col in cart_columns:
            self.cart_tree.heading(col, text=col)
            if col == 'Item':
                self.cart_tree.column(col, width=150)
            else:
                self.cart_tree.column(col, width=60)
        
        cart_scrollbar = ttk.Scrollbar(cart_frame, orient=tk.VERTICAL, command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
        
        self.cart_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        cart_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Cart buttons
        cart_buttons_frame = ttk.Frame(cart_frame)
        cart_buttons_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Button(cart_buttons_frame, text="Remove Item", 
                  command=self.remove_cart_item).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cart_buttons_frame, text="Clear Cart", 
                  command=self.clear_cart).pack(side=tk.LEFT)
        
        # Totals frame
        totals_frame = ttk.LabelFrame(right_frame, text="Order Total")
        totals_frame.pack(fill=tk.X, pady=(0, 10))
        
        totals_grid = ttk.Frame(totals_frame)
        totals_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Subtotal
        ttk.Label(totals_grid, text="Subtotal:").grid(row=0, column=0, sticky=tk.W)
        self.subtotal_label = ttk.Label(totals_grid, text="$0.00", font=("Arial", 12))
        self.subtotal_label.grid(row=0, column=1, sticky=tk.E)
        
        # Tax
        ttk.Label(totals_grid, text="Tax:").grid(row=1, column=0, sticky=tk.W)
        self.tax_label = ttk.Label(totals_grid, text="$0.00", font=("Arial", 12))
        self.tax_label.grid(row=1, column=1, sticky=tk.E)
        
        # Total
        ttk.Label(totals_grid, text="Total:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky=tk.W)
        self.total_label = ttk.Label(totals_grid, text="$0.00", font=("Arial", 14, "bold"))
        self.total_label.grid(row=2, column=1, sticky=tk.E)
        
        totals_grid.columnconfigure(1, weight=1)
        
        # Payment frame
        payment_frame = ttk.LabelFrame(right_frame, text="Payment")
        payment_frame.pack(fill=tk.X)
        
        payment_grid = ttk.Frame(payment_frame)
        payment_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Payment method
        ttk.Label(payment_grid, text="Method:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.payment_method_var = tk.StringVar(value="cash")
        payment_combo = ttk.Combobox(payment_grid, textvariable=self.payment_method_var,
                                   values=["cash", "card", "check"], state="readonly", width=15)
        payment_combo.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Checkout buttons
        checkout_frame = ttk.Frame(payment_grid)
        checkout_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(checkout_frame, text="Process Order", 
                  command=self.process_order, style="Accent.TButton").pack(fill=tk.X, pady=(0, 5))
        ttk.Button(checkout_frame, text="Hold Order", 
                  command=self.hold_order).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(checkout_frame, text="Cancel Order", 
                  command=self.cancel_order).pack(fill=tk.X)
    
    def load_categories(self):
        """Load categories as buttons"""
        # Clear existing category buttons
        for widget in self.cat_buttons_frame.winfo_children():
            widget.destroy()
        
        try:
            query = "SELECT id, name FROM categories WHERE is_active = 1 ORDER BY name"
            categories = execute_query_dict(query, fetch='all') or []
            
            # Add "All" button
            all_btn = ttk.Button(self.cat_buttons_frame, text="All", 
                               command=lambda: self.load_menu_items())
            all_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            # Add category buttons
            for cat in categories:
                btn = ttk.Button(self.cat_buttons_frame, text=cat['name'],
                               command=lambda c=cat['id']: self.load_menu_items(c))
                btn.pack(side=tk.LEFT, padx=(0, 5))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load categories: {str(e)}")
    
    def load_menu_items(self, category_id=None):
        """Load menu items as buttons"""
        # Clear existing item buttons
        for widget in self.items_scrollable_frame.winfo_children():
            widget.destroy()
        
        try:
            if category_id:
                query = '''
                    SELECT id, name, price, description
                    FROM menu_items
                    WHERE category_id = ? AND is_active = 1
                    ORDER BY name
                '''
                items = execute_query_dict(query, (category_id,), 'all') or []
            else:
                query = '''
                    SELECT id, name, price, description
                    FROM menu_items
                    WHERE is_active = 1
                    ORDER BY name
                '''
                items = execute_query_dict(query, fetch='all') or []
            
            # Create item buttons in grid
            row = 0
            col = 0
            max_cols = 3
            
            for item in items:
                item_frame = ttk.Frame(self.items_scrollable_frame, relief=tk.RAISED, borderwidth=1)
                item_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                
                # Item button
                btn_text = f"{item['name']}\n{POSUtils.format_currency(item['price'])}"
                item_btn = ttk.Button(item_frame, text=btn_text, width=15,
                                    command=lambda i=item: self.add_to_cart(i))
                item_btn.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            # Configure column weights
            for i in range(max_cols):
                self.items_scrollable_frame.columnconfigure(i, weight=1)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load menu items: {str(e)}")
    
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
        # Implementation for holding orders
        messagebox.showinfo("Info", "Hold order functionality not yet implemented")
    
    def cancel_order(self):
        """Cancel the current order"""
        if self.cart_items and messagebox.askyesno("Confirm", "Cancel current order?"):
            self.clear_cart()
            self.customer_var.set("")
    
    def print_receipt(self, order, order_items):
        """Print receipt for order"""
        try:
            # Save receipt as PDF
            receipt_path = f"receipts/receipt_{order['order_number']}.pdf"
            os.makedirs("receipts", exist_ok=True)
            
            printer = InvoicePrinter()
            if printer.generate_receipt_pdf(order, order_items, receipt_path):
                # Option to view receipt
                if messagebox.askyesno("Receipt", "Receipt saved. Would you like to view it?"):
                    if sys.platform == 'win32':
                        os.startfile(receipt_path)
                    elif sys.platform == 'darwin':
                        subprocess.Popen(['open', receipt_path])
                    else:
                        subprocess.Popen(['xdg-open', receipt_path])
            
        except Exception as e:
            print(f"Error printing receipt: {e}")


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
        self.parent.title("Point of Sale")
        self.parent.geometry("1200x800")
        self.parent.resizable(True, True)
