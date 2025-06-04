"""
Kitchen Display Screen
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict
from logic.order_manager import OrderManager
from logic.utils import POSUtils
import threading
import time

class KitchenDisplayTab:
    def __init__(self, parent: ttk.Frame):
        self.parent = parent
        self.setup_ui()
        self.start_auto_refresh()
    
    def setup_ui(self):
        """Setup the kitchen display UI"""
        # Header frame
        header_frame = ttk.Frame(self.parent)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        title_label = ttk.Label(header_frame, text="Kitchen Display", 
                               font=("Arial", 18, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Refresh button
        refresh_btn = ttk.Button(header_frame, text="Refresh", command=self.load_orders)
        refresh_btn.pack(side=tk.RIGHT)
        
        # Orders frame
        orders_frame = ttk.Frame(self.parent)
        orders_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create scrollable frame for orders
        canvas = tk.Canvas(orders_frame)
        scrollbar = ttk.Scrollbar(orders_frame, orient="vertical", command=canvas.yview)
        self.orders_scrollable_frame = ttk.Frame(canvas)
        
        self.orders_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.orders_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load initial orders
        self.load_orders()
    
    def load_orders(self):
        """Load pending orders"""
        # Clear existing order widgets
        for widget in self.orders_scrollable_frame.winfo_children():
            widget.destroy()
        
        try:
            orders = OrderManager.get_pending_orders()
            
            if not orders:
                no_orders_label = ttk.Label(self.orders_scrollable_frame, 
                                          text="No pending orders", 
                                          font=("Arial", 16))
                no_orders_label.pack(pady=50)
                return
            
            # Display orders in grid
            row = 0
            col = 0
            max_cols = 3
            
            for order in orders:
                self.create_order_card(order, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            # Configure column weights
            for i in range(max_cols):
                self.orders_scrollable_frame.columnconfigure(i, weight=1)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load orders: {str(e)}")
    
    def create_order_card(self, order: Dict, row: int, col: int):
        """Create an order card widget"""
        # Order card frame
        card_frame = ttk.LabelFrame(self.orders_scrollable_frame, 
                                   text=f"Order #{order['order_number']}")
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Order info
        info_frame = ttk.Frame(card_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Customer and time
        customer_text = order['customer_name'] or 'Walk-in'
        order_time = POSUtils.format_time(order['created_at'])
        
        ttk.Label(info_frame, text=f"Customer: {customer_text}", 
                 font=("Arial", 10, "bold")).pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Time: {order_time}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Type: {order['order_type'].replace('_', ' ').title()}").pack(anchor=tk.W)
        
        # Order items
        items_frame = ttk.Frame(card_frame)
        items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        try:
            order_items = OrderManager.get_order_items(order['id'])
            
            # Items listbox
            items_listbox = tk.Listbox(items_frame, height=6, font=("Arial", 10))
            items_listbox.pack(fill=tk.BOTH, expand=True)
            
            for item in order_items:
                item_text = f"{item['quantity']}x {item['item_name']}"
                if item['special_instructions']:
                    item_text += f" - {item['special_instructions']}"
                items_listbox.insert(tk.END, item_text)
            
        except Exception as e:
            ttk.Label(items_frame, text=f"Error loading items: {str(e)}").pack()
        
        # Status and buttons
        status_frame = ttk.Frame(card_frame)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Current status
        status_text = order['status'].replace('_', ' ').title()
        status_color = self.get_status_color(order['status'])
        
        status_label = ttk.Label(status_frame, text=f"Status: {status_text}", 
                                font=("Arial", 10, "bold"))
        status_label.pack(anchor=tk.W)
        
        # Action buttons
        buttons_frame = ttk.Frame(card_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        if order['status'] == 'pending':
            start_btn = ttk.Button(buttons_frame, text="Start Preparing",
                                 command=lambda o=order: self.update_order_status(o['id'], 'preparing'))
            start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        if order['status'] == 'preparing':
            ready_btn = ttk.Button(buttons_frame, text="Mark Ready",
                                 command=lambda o=order: self.update_order_status(o['id'], 'ready'))
            ready_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        if order['status'] == 'ready':
            complete_btn = ttk.Button(buttons_frame, text="Complete",
                                    command=lambda o=order: self.update_order_status(o['id'], 'completed'))
            complete_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Cancel button (always available)
        cancel_btn = ttk.Button(buttons_frame, text="Cancel",
                              command=lambda o=order: self.cancel_order(o['id']))
        cancel_btn.pack(side=tk.RIGHT)
    
    def get_status_color(self, status: str) -> str:
        """Get color for order status"""
        colors = {
            'pending': 'red',
            'preparing': 'orange', 
            'ready': 'green',
            'completed': 'blue'
        }
        return colors.get(status, 'black')
    
    def update_order_status(self, order_id: int, new_status: str):
        """Update order status"""
        try:
            if OrderManager.update_order_status(order_id, new_status):
                self.load_orders()  # Refresh display
            else:
                messagebox.showerror("Error", "Failed to update order status")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update order status: {str(e)}")
    
    def cancel_order(self, order_id: int):
        """Cancel an order"""
        if messagebox.askyesno("Confirm", "Are you sure you want to cancel this order?"):
            try:
                if OrderManager.update_order_status(order_id, 'cancelled'):
                    self.load_orders()  # Refresh display
                else:
                    messagebox.showerror("Error", "Failed to cancel order")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to cancel order: {str(e)}")
    
    def start_auto_refresh(self):
        """Start auto-refresh timer"""
        def refresh_loop():
            while True:
                time.sleep(30)  # Refresh every 30 seconds
                try:
                    # Use after() to run in main thread
                    self.parent.after(0, self.load_orders)
                except:
                    break  # Exit if window is closed
        
        # Start refresh thread
        refresh_thread = threading.Thread(target=refresh_loop, daemon=True)
        refresh_thread.start()


class KitchenDisplayWindow:
    """Standalone kitchen display window"""
    def __init__(self, parent: tk.Toplevel):
        self.parent = parent
        self.setup_window()
        
        # Create kitchen display tab
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.kitchen_tab = KitchenDisplayTab(main_frame)
    
    def setup_window(self):
        """Setup the kitchen display window"""
        self.parent.title("Kitchen Display")
        self.parent.geometry("1000x700")
        self.parent.resizable(True, True)
