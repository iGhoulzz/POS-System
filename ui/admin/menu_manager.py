"""
Enhanced Menu Manager with proper delete functionality, foreign key constraints, and syntax fixes
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import logging
from datetime import datetime
from PIL import Image, ImageTk
import shutil

class MenuManagerTab:
    def __init__(self, parent):
        self.parent = parent
        self.current_item = None
        self.current_category = None
        self.image_path = None
        self.image_preview = None
        
        # Create main container
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create paned window for left and right panels
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create panels
        self.create_left_panel(self.paned_window)
        self.create_right_panel(self.paned_window)
        
        # Load initial data
        self.load_categories()
        self.load_menu_items()
    
    def create_left_panel(self, parent):
        """Create the left panel with categories and menu items"""
        left_frame = ttk.Frame(parent, width=400)
        parent.add(left_frame, weight=1)
        
        # Categories section
        categories_frame = ttk.LabelFrame(left_frame, text="📂 Categories", padding=10)
        categories_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Categories listbox with scrollbar
        categories_scroll_frame = ttk.Frame(categories_frame)
        categories_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        self.categories_listbox = tk.Listbox(categories_scroll_frame, font=('Segoe UI', 10))
        categories_scrollbar = ttk.Scrollbar(categories_scroll_frame, orient=tk.VERTICAL, 
                                           command=self.categories_listbox.yview)
        self.categories_listbox.configure(yscrollcommand=categories_scrollbar.set)
        
        self.categories_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        categories_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.categories_listbox.bind('<<ListboxSelect>>', self.on_category_select)
        
        # Category buttons
        cat_buttons_frame = ttk.Frame(categories_frame)
        cat_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(cat_buttons_frame, text="➕ Add", command=self.add_category).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cat_buttons_frame, text="✏️ Edit", command=self.edit_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(cat_buttons_frame, text="🗑️ Delete", command=self.delete_category).pack(side=tk.LEFT, padx=5)
        
        # Menu items section
        items_frame = ttk.LabelFrame(left_frame, text="🍕 Menu Items", padding=10)
        items_frame.pack(fill=tk.BOTH, expand=True)
        
        # Items treeview
        columns = ('Name', 'Category', 'Price', 'Status')
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=10)
        
        # Configure columns
        self.items_tree.heading('Name', text='Name')
        self.items_tree.heading('Category', text='Category')
        self.items_tree.heading('Price', text='Price')
        self.items_tree.heading('Status', text='Status')
        
        self.items_tree.column('Name', width=150)
        self.items_tree.column('Category', width=100)
        self.items_tree.column('Price', width=70)
        self.items_tree.column('Status', width=70)
        
        # Items scrollbar
        items_scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=items_scrollbar.set)
        
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        items_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.items_tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
        # Item buttons
        item_buttons_frame = ttk.Frame(items_frame)
        item_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(item_buttons_frame, text="➕ Add", command=self.add_menu_item).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(item_buttons_frame, text="✏️ Edit", command=self.edit_menu_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(item_buttons_frame, text="🗑️ Delete", command=self.delete_menu_item).pack(side=tk.LEFT, padx=5)
    
    def create_right_panel(self, parent):
        """Create the right panel with item form"""
        right_frame = ttk.Frame(parent, width=500)
        parent.add(right_frame, weight=1)
        
        # Form header
        header_frame = ttk.Frame(right_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="🍽️ Menu Item Details", 
                 font=('Segoe UI', 14, 'bold')).pack(side=tk.LEFT)
        
        # Form buttons
        buttons_frame = ttk.Frame(header_frame)
        buttons_frame.pack(side=tk.RIGHT)
        
        ttk.Button(buttons_frame, text="💾 Save", command=self.save_item).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="🔄 Reset", command=self.reset_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🆕 Clear", command=self.clear_form).pack(side=tk.LEFT, padx=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_basic_info_tab(self.notebook)
        self.create_pricing_tab(self.notebook)
        self.create_image_tab(self.notebook)
    
    def create_basic_info_tab(self, notebook):
        """Create the basic info tab"""
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="📝 Basic Info")
        
        # Item name
        ttk.Label(basic_frame, text="Item Name:", font=('Segoe UI', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=10, padx=(0, 10))
        self.name_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=self.name_var, font=('Segoe UI', 10), width=30).grid(
            row=0, column=1, sticky='ew', pady=10)
        
        # Description
        ttk.Label(basic_frame, text="Description:", font=('Segoe UI', 10, 'bold')).grid(
            row=1, column=0, sticky='nw', pady=10, padx=(0, 10))
        self.description_text = tk.Text(basic_frame, height=4, width=30, font=('Segoe UI', 10))
        self.description_text.grid(row=1, column=1, sticky='ew', pady=10)
        
        # Category
        ttk.Label(basic_frame, text="Category:", font=('Segoe UI', 10, 'bold')).grid(
            row=2, column=0, sticky='w', pady=10, padx=(0, 10))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(basic_frame, textvariable=self.category_var, 
                                          state='readonly', font=('Segoe UI', 10), width=27)
        self.category_combo.grid(row=2, column=1, sticky='ew', pady=10)
        
        # Active status
        self.is_active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(basic_frame, text="Item is active", 
                       variable=self.is_active_var, 
                       style='Switch.TCheckbutton').grid(row=3, column=0, columnspan=2, sticky='w', pady=10)
        
        # Preparation time
        ttk.Label(basic_frame, text="Prep Time (min):", font=('Segoe UI', 10, 'bold')).grid(
            row=4, column=0, sticky='w', pady=10, padx=(0, 10))
        self.prep_time_var = tk.StringVar(value="0")
        prep_time_spin = ttk.Spinbox(basic_frame, from_=0, to=120, 
                                    textvariable=self.prep_time_var, width=27)
        prep_time_spin.grid(row=4, column=1, sticky='ew', pady=5)
        
        # Configure grid weights
        basic_frame.grid_columnconfigure(1, weight=1)
    
    def create_pricing_tab(self, notebook):
        """Create the pricing tab"""
        pricing_frame = ttk.Frame(notebook)
        notebook.add(pricing_frame, text="💰 Pricing")
        
        # Cost price
        ttk.Label(pricing_frame, text="Cost Price ($):", font=('Segoe UI', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=10, padx=(0, 10))
        self.cost_price_var = tk.StringVar(value="0.00")
        self.cost_price_entry = ttk.Entry(pricing_frame, textvariable=self.cost_price_var, 
                                         font=('Segoe UI', 10), width=15)
        self.cost_price_entry.grid(row=0, column=1, sticky='w', pady=10)
        self.cost_price_entry.bind('<KeyRelease>', self.calculate_profit)
        
        # Sell price
        ttk.Label(pricing_frame, text="Sell Price ($):", font=('Segoe UI', 10, 'bold')).grid(
            row=1, column=0, sticky='w', pady=10, padx=(0, 10))
        self.sell_price_var = tk.StringVar(value="0.00")
        self.sell_price_entry = ttk.Entry(pricing_frame, textvariable=self.sell_price_var, 
                                         font=('Segoe UI', 10), width=15)
        self.sell_price_entry.grid(row=1, column=1, sticky='w', pady=10)
        self.sell_price_entry.bind('<KeyRelease>', self.calculate_profit)
        
        # Profit calculation
        profit_frame = ttk.LabelFrame(pricing_frame, text="💡 Profit Analysis", padding=10)
        profit_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=20)
        
        self.profit_amount_label = ttk.Label(profit_frame, text="Profit: $0.00", 
                                           font=('Segoe UI', 12, 'bold'))
        self.profit_amount_label.pack()
        
        self.profit_margin_label = ttk.Label(profit_frame, text="Margin: 0%", 
                                           font=('Segoe UI', 10))
        self.profit_margin_label.pack()
        
        # Pricing suggestions
        suggestions_frame = ttk.LabelFrame(pricing_frame, text="💡 Pricing Suggestions", 
                                          padding=10)
        suggestions_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=10)
        
        ttk.Button(suggestions_frame, text="50% Margin", 
                  command=lambda: self.set_margin(0.5)).pack(side=tk.LEFT, padx=5)
        ttk.Button(suggestions_frame, text="100% Margin", 
                  command=lambda: self.set_margin(1.0)).pack(side=tk.LEFT, padx=5)
        ttk.Button(suggestions_frame, text="200% Margin", 
                  command=lambda: self.set_margin(2.0)).pack(side=tk.LEFT, padx=5)
        
        pricing_frame.grid_columnconfigure(1, weight=1)
    
    def create_image_tab(self, notebook):
        """Create the image tab"""
        image_frame = ttk.Frame(notebook)
        notebook.add(image_frame, text="🖼️ Image")
        
        # Image preview
        preview_frame = ttk.LabelFrame(image_frame, text="Image Preview", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.image_label = ttk.Label(preview_frame, text="No image selected", 
                                    background='#f0f0f0', anchor='center')
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Image buttons
        image_buttons_frame = ttk.Frame(image_frame)
        image_buttons_frame.pack(fill=tk.X)
        
        ttk.Button(image_buttons_frame, text="📁 Select Image", 
                  command=self.select_image).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(image_buttons_frame, text="🗑️ Remove Image", 
                  command=self.remove_image).pack(side=tk.LEFT)
    
    def load_categories(self):
        """Load categories from database"""
        print("📂 Loading categories...")
        logging.info("MenuManager: Loading categories from database")
        
        try:
            from db.db_utils import execute_query_dict
            categories = execute_query_dict("SELECT name FROM categories ORDER BY name", fetch='all')
            
            # Clear listbox
            self.categories_listbox.delete(0, tk.END)
            
            # Add categories to listbox
            for cat in categories:
                self.categories_listbox.insert(tk.END, cat['name'])
            
            # Update combobox
            if hasattr(self, 'category_combo'):
                category_names = [cat['name'] for cat in categories]
                self.category_combo['values'] = category_names
            
            print(f"✅ Loaded {len(categories)} categories")
            logging.info(f"MenuManager: Successfully loaded {len(categories)} categories")
                
        except Exception as e:
            error_msg = f"Failed to load categories: {str(e)}"
            print(f"❌ {error_msg}")
            logging.error(f"MenuManager: {error_msg}")
            messagebox.showerror("Error", error_msg)
    
    def load_menu_items(self):
        """Load menu items from database"""
        print("🍕 Loading menu items...")
        logging.info("MenuManager: Loading menu items from database")
        
        try:
            from db.db_utils import execute_query_dict
            query = """
                SELECT mi.*, c.name as category_name 
                FROM menu_items mi 
                LEFT JOIN categories c ON mi.category_id = c.id 
                ORDER BY c.name, mi.name
            """
            items = execute_query_dict(query, fetch='all')
            
            # Clear treeview
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
            
            # Add items to treeview
            for item in items:
                status = "Active" if item.get('is_active', 1) else "Inactive"
                price = f"${item.get('price', 0):.2f}"
                self.items_tree.insert('', tk.END, 
                                     values=(item.get('name', ''), 
                                           item.get('category_name', ''), 
                                           price, status),
                                     tags=(item.get('id', ''),))
            
            print(f"✅ Loaded {len(items)} menu items")
            logging.info(f"MenuManager: Successfully loaded {len(items)} menu items")
                
        except Exception as e:
            error_msg = f"Failed to load menu items: {str(e)}"
            print(f"❌ {error_msg}")
            logging.error(f"MenuManager: {error_msg}")
            messagebox.showerror("Error", error_msg)
    
    def on_category_select(self, event):
        """Handle category selection"""
        selection = self.categories_listbox.curselection()
        if selection:
            category_name = self.categories_listbox.get(selection[0])
            self.current_category = category_name
    
    def on_item_select(self, event):
        """Handle item selection"""
        selection = self.items_tree.selection()
        if selection:
            item = self.items_tree.item(selection[0])
            item_id = item['tags'][0] if item['tags'] else None
            if item_id:
                self.load_item_details(item_id)
    
    # ... truncated for brevity - rest of methods would continue here ...
    
    def delete_category(self):
        """Delete selected category with proper FK constraint handling"""
        selection = self.categories_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a category to delete")
            return
        
        category_name = self.categories_listbox.get(selection[0])
        
        try:
            from db.db_utils import execute_query_dict, execute_query
            
            # Get category data
            category_data = execute_query_dict("SELECT id FROM categories WHERE name = ?", 
                                             (category_name,), fetch='one')
            
            if not category_data:
                messagebox.showerror("Error", f"Category '{category_name}' not found")
                return
            
            category_id = category_data['id']
            
            # Check if category has menu items
            items = execute_query_dict("SELECT COUNT(*) as count FROM menu_items WHERE category_id = ?", 
                                     (category_id,), fetch='one')
            
            item_count = items['count'] if items else 0
            
            # Confirm deletion
            if item_count > 0:
                confirm_msg = (f"Are you sure you want to delete category '{category_name}'?\n\n"
                             f"This category contains {item_count} menu item(s) which will also be deleted.")
            else:
                confirm_msg = f"Are you sure you want to delete category '{category_name}'?"
            
            if messagebox.askyesno("Confirm Delete", confirm_msg):
                items_deleted = 0
                if item_count > 0:
                    # Delete items in category first
                    items_deleted = execute_query("DELETE FROM menu_items WHERE category_id = ?", (category_id,))
                
                # Delete category
                rows_affected = execute_query("DELETE FROM categories WHERE id = ?", (category_id,))
                
                if rows_affected > 0:
                    success_msg = f"Category '{category_name}' deleted successfully"
                    if items_deleted > 0:
                        success_msg += f"\n{items_deleted} menu items were also deleted"
                    messagebox.showinfo("Success", success_msg)
                    
                    # Refresh the displays
                    self.load_categories()
                    self.load_menu_items()
                else:
                    messagebox.showerror("Error", f"Failed to delete category '{category_name}'. It may have already been deleted.")
                    
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                error_msg = f"Cannot delete category '{category_name}' because it contains menu items."
                messagebox.showerror("Foreign Key Constraint", error_msg)
            else:
                messagebox.showerror("Database Error", f"Database integrity error: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete category: {str(e)}")
    
    def delete_menu_item(self):
        """Delete selected menu item with proper FK constraint handling"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        item = self.items_tree.item(selection[0])
        item_name = item['values'][0]
        item_id = item['tags'][0] if item['tags'] else None
        
        if not item_id:
            return
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item_name}'?"):
            try:
                from db.db_utils import execute_query
                
                rows_affected = execute_query("DELETE FROM menu_items WHERE id = ?", (item_id,))
                
                if rows_affected > 0:
                    messagebox.showinfo("Success", f"Item '{item_name}' deleted successfully")
                    self.load_menu_items()
                    self.clear_form()
                else:
                    messagebox.showerror("Error", f"Failed to delete '{item_name}'. It may have already been deleted.")
                
            except sqlite3.IntegrityError as e:
                if "FOREIGN KEY constraint failed" in str(e):
                    error_msg = f"Cannot delete menu item '{item_name}' because it is referenced by existing orders."
                    messagebox.showerror("Foreign Key Constraint", error_msg)
                else:
                    messagebox.showerror("Database Error", f"Database integrity error: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete item: {str(e)}")
    
    # Add remaining methods as needed...
    def load_item_details(self, item_id):
        """Load item details into the form"""
        try:
            from db.db_utils import execute_query_dict
            items = execute_query_dict("SELECT * FROM menu_items WHERE id = ?", (item_id,), fetch='all')
            
            if items:
                item = items[0]
                self.current_item = item
                
                # Load basic info
                self.name_var.set(item.get('name', ''))
                self.description_text.delete(1.0, tk.END)
                self.description_text.insert(1.0, item.get('description', ''))
                
                # Load category
                category_query = "SELECT name FROM categories WHERE id = ?"
                cat_result = execute_query_dict(category_query, (item.get('category_id'),), fetch='one')
                if cat_result:
                    self.category_var.set(cat_result['name'])
                
                # Load pricing
                self.cost_price_var.set(str(item.get('cost_price', 0)))
                self.sell_price_var.set(str(item.get('price', 0)))
                
                # Load other fields
                self.is_active_var.set(bool(item.get('is_active', 1)))
                self.prep_time_var.set(str(item.get('preparation_time', 0)))
                
                # Load image if exists
                if item.get('image_path'):
                    self.load_item_image(item['image_path'])
                else:
                    self.remove_image()
                
                self.calculate_profit()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load item details: {str(e)}")
    
    def load_item_image(self, image_path):
        """Load and display item image"""
        if image_path and os.path.exists(image_path):
            try:
                # Load and resize image
                image = Image.open(image_path)
                image.thumbnail((200, 200), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                self.image_preview = ImageTk.PhotoImage(image)
                self.image_label.configure(image=self.image_preview, text="")
                self.image_path = image_path
                
            except Exception as e:
                print(f"Error loading image: {e}")
                self.image_label.configure(image="", text="Error loading image")
                self.image_path = None
        else:
            self.image_label.configure(image="", text="No image selected")
            self.image_path = None
    
    def calculate_profit(self, event=None):
        """Calculate and display profit information"""
        try:
            cost = float(self.cost_price_var.get() or 0)
            price = float(self.sell_price_var.get() or 0)
            
            profit = price - cost
            margin = (profit / price * 100) if price > 0 else 0
            
            self.profit_amount_label.configure(text=f"Profit: ${profit:.2f}")
            self.profit_margin_label.configure(text=f"Margin: {margin:.1f}%")
            
            # Color coding
            if profit > 0:
                self.profit_amount_label.configure(foreground='green')
            elif profit < 0:
                self.profit_amount_label.configure(foreground='red')
            else:
                self.profit_amount_label.configure(foreground='black')
                
        except ValueError:
            self.profit_amount_label.configure(text="Profit: $0.00", foreground='black')
            self.profit_margin_label.configure(text="Margin: 0%")
    
    def set_margin(self, margin_multiplier):
        """Set sell price based on margin multiplier"""
        try:
            cost = float(self.cost_price_var.get() or 0)
            if cost > 0:
                sell_price = cost * (1 + margin_multiplier)
                self.sell_price_var.set(f"{sell_price:.2f}")
                self.calculate_profit()
        except ValueError:
            pass
    
    def select_image(self):
        """Select an image file for the menu item"""
        file_path = filedialog.askopenfilename(
            title="Select Image",        filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
        )
        if file_path:
            self.load_item_image(file_path)
    
    def remove_image(self):
        """Remove the current image"""
        self.image_label.configure(image="", text="No image selected")
        self.image_path = None
        self.image_preview = None
    
    def add_category(self):
        """Add a new category"""
        CategoryDialog(self.parent, self, mode='add')
    
    def edit_category(self):
        """Edit selected category"""
        selection = self.categories_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a category to edit")
            return
        
        category_name = self.categories_listbox.get(selection[0])
        CategoryDialog(self.parent, self, mode='edit', category_name=category_name)
    
    def add_menu_item(self):
        """Add a new menu item"""
        self.clear_form()
        self.current_item = None
    
    def edit_menu_item(self):
        """Edit selected menu item"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
    
    def save_item(self):
        """Save the current item"""
        item_name = self.name_var.get().strip()
        action = "update" if self.current_item else "create"
        print(f"💾 Starting {action} operation for menu item: {item_name}")
        logging.info(f"MenuManager: Starting {action} operation for menu item: {item_name}")
        
        # Validate required fields
        if not item_name:
            print("❌ Validation failed: Item name is required")
            logging.error("MenuManager: Validation failed - Item name is required")
            messagebox.showerror("Error", "Item name is required")
            return
        
        if not self.category_var.get():
            print("❌ Validation failed: Category is required")
            logging.error("MenuManager: Validation failed - Category is required")
            messagebox.showerror("Error", "Please select a category")
            return
        
        try:
            cost_price = float(self.cost_price_var.get() or 0)
            sell_price = float(self.sell_price_var.get() or 0)
            print(f"💰 Parsed prices - Cost: ${cost_price:.2f}, Sell: ${sell_price:.2f}")
            logging.info(f"MenuManager: Parsed prices for {item_name} - Cost: ${cost_price:.2f}, Sell: ${sell_price:.2f}")
        except ValueError:
            print("❌ Validation failed: Invalid price format")
            logging.error("MenuManager: Validation failed - Invalid price format")
            messagebox.showerror("Error", "Please enter valid prices")
            return
        
        if sell_price <= 0:
            print("❌ Validation failed: Sell price must be greater than 0")
            logging.error("MenuManager: Validation failed - Sell price must be greater than 0")
            messagebox.showerror("Error", "Sell price must be greater than 0")
            return
        
        print(f"🔍 Looking up category ID for: {self.category_var.get()}")
        logging.info(f"MenuManager: Looking up category ID for: {self.category_var.get()}")
        
        try:
            from db.db_utils import execute_query, execute_query_dict
            
            # Get category ID
            categories = execute_query_dict("SELECT id FROM categories WHERE name = ?", 
                                           (self.category_var.get(),), fetch='all')
            if not categories:
                print("❌ Category not found in database")
                logging.error("MenuManager: Selected category not found in database")
                messagebox.showerror("Error", "Selected category not found")
                return
            
            category_id = categories[0]['id']
            print(f"✅ Found category ID: {category_id}")
            logging.info(f"MenuManager: Found category ID: {category_id}")
            
            # Prepare data
            name = item_name
            description = self.description_text.get(1.0, tk.END).strip()
            is_active = 1 if self.is_active_var.get() else 0
            prep_time = int(self.prep_time_var.get() or 0)
            
            print(f"📝 Prepared item data - Name: {name}, Description: {description[:50]}{'...' if len(description) > 50 else ''}, Active: {bool(is_active)}, Prep Time: {prep_time}min")
            logging.info(f"MenuManager: Prepared item data - Name: {name}, Active: {bool(is_active)}, Prep Time: {prep_time}min")
            
            # Handle image
            image_path = None
            if self.image_path:
                print(f"🖼️ Processing image upload from: {self.image_path}")
                logging.info(f"MenuManager: Processing image upload from: {self.image_path}")
                
                # Create images directory if it doesn't exist
                images_dir = "static/images/menu_items"
                os.makedirs(images_dir, exist_ok=True)
                
                # Copy image to images directory
                filename = f"{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                dest_path = os.path.join(images_dir, filename)
                shutil.copy2(self.image_path, dest_path)
                image_path = dest_path
                print(f"✅ Image copied to: {image_path}")
                logging.info(f"MenuManager: Image copied to: {image_path}")
            
            if self.current_item:
                # Update existing item
                print(f"🔄 Updating existing menu item ID: {self.current_item['id']}")
                logging.info(f"MenuManager: Updating existing menu item ID: {self.current_item['id']}")
                
                query = """UPDATE menu_items SET 
                          name=?, description=?, category_id=?, cost_price=?, price=?, 
                          is_active=?, preparation_time=?, image_path=? 
                          WHERE id=?"""
                params = (name, description, category_id, cost_price, sell_price, 
                         is_active, prep_time, image_path, self.current_item['id'])
                
                rows_affected = execute_query(query, params)
                
                if rows_affected > 0:
                    print(f"✅ Menu item '{name}' updated successfully")
                    logging.info(f"MenuManager: Menu item '{name}' updated successfully")
                    messagebox.showinfo("Success", f"Menu item '{name}' updated successfully")
                else:
                    print(f"❌ Failed to update menu item '{name}' - no rows affected")
                    logging.error(f"MenuManager: Failed to update menu item '{name}' - no rows affected")
                    messagebox.showerror("Error", f"Failed to update '{name}'. The item may have been deleted.")
                    
            else:
                # Create new item
                print(f"➕ Creating new menu item: {name}")
                logging.info(f"MenuManager: Creating new menu item: {name}")
                
                query = """INSERT INTO menu_items 
                          (name, description, category_id, cost_price, price, is_active, preparation_time, image_path) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
                params = (name, description, category_id, cost_price, sell_price, 
                         is_active, prep_time, image_path)
                
                rows_affected = execute_query(query, params)
                
                if rows_affected > 0:
                    print(f"✅ Menu item '{name}' created successfully")
                    logging.info(f"MenuManager: Menu item '{name}' created successfully")
                    messagebox.showinfo("Success", f"Menu item '{name}' created successfully")
                else:
                    print(f"❌ Failed to create menu item '{name}' - no rows affected")
                    logging.error(f"MenuManager: Failed to create menu item '{name}' - no rows affected")
                    messagebox.showerror("Error", f"Failed to create '{name}'.")
            
            # Refresh the menu items list
            self.load_menu_items()
            
        except Exception as e:
            error_msg = f"Failed to save item: {str(e)}"
            print(f"❌ {error_msg}")
            logging.error(f"MenuManager: {error_msg}")
            messagebox.showerror("Error", error_msg)
    
    def reset_form(self):
        """Reset form to last loaded values"""
        if self.current_item:
            self.load_item_details(self.current_item['id'])
        else:
            self.clear_form()
    
    def clear_form(self):
        """Clear all form fields"""
        self.current_item = None
        self.name_var.set("")
        self.description_text.delete(1.0, tk.END)
        self.category_var.set("")
        self.cost_price_var.set("0.00")
        self.sell_price_var.set("0.00")
        self.is_active_var.set(True)
        self.prep_time_var.set("0")
        self.remove_image()
        self.calculate_profit()


class CategoryDialog:
    def __init__(self, parent, menu_manager, mode='add', category_name=None):
        self.parent = parent
        self.menu_manager = menu_manager
        self.mode = mode
        self.category_name = category_name
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{'Edit' if mode == 'edit' else 'Add'} Category")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
        
        if mode == 'edit' and category_name:
            self.name_var.set(category_name)
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Category name
        ttk.Label(main_frame, text="Category Name:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, font=('Segoe UI', 10), width=30)
        name_entry.pack(fill=tk.X, pady=(0, 20))
        name_entry.focus()
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Save", command=self.save_category).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(buttons_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)
        
        # Bind Enter key to save
        self.dialog.bind('<Return>', lambda e: self.save_category())
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
    
    def save_category(self):
        """Save the category"""
        name = self.name_var.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Category name is required")
            return
        
        try:
            from db.db_utils import execute_query
            
            if self.mode == 'add':
                # Check if category already exists
                from db.db_utils import execute_query_dict
                existing = execute_query_dict("SELECT id FROM categories WHERE name = ?", (name,), fetch='one')
                if existing:
                    messagebox.showerror("Error", "Category already exists")
                    return
                
                # Add new category
                rows_affected = execute_query("INSERT INTO categories (name) VALUES (?)", (name,))
                if rows_affected > 0:
                    messagebox.showinfo("Success", f"Category '{name}' added successfully")
                    self.menu_manager.load_categories()
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to add category")
                    
            elif self.mode == 'edit':
                # Update existing category
                rows_affected = execute_query("UPDATE categories SET name = ? WHERE name = ?", 
                                            (name, self.category_name))
                if rows_affected > 0:
                    messagebox.showinfo("Success", f"Category updated successfully")
                    self.menu_manager.load_categories()
                    self.menu_manager.load_menu_items()  # Refresh items to show new category name
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to update category")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save category: {str(e)}")