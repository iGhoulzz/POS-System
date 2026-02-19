import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import sqlite3
from logic.utils import validate_number

class ExpensesScreen:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        
        self.create_widgets()
        self.load_expenses()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Expense Management", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Add expense frame
        add_frame = ttk.LabelFrame(main_frame, text="Add New Expense", padding=15)
        add_frame.pack(fill='x', pady=(0, 20))
        
        # Expense form
        form_frame = ttk.Frame(add_frame)
        form_frame.pack(fill='x')
        
        # Description
        ttk.Label(form_frame, text="Description:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.description_var = tk.StringVar()
        description_entry = ttk.Entry(form_frame, textvariable=self.description_var, width=30)
        description_entry.grid(row=0, column=1, padx=(0, 20))
        
        # Amount
        ttk.Label(form_frame, text="Amount:").grid(row=0, column=2, sticky='w', padx=(0, 10))
        self.amount_var = tk.StringVar()
        amount_entry = ttk.Entry(form_frame, textvariable=self.amount_var, width=15)
        amount_entry.grid(row=0, column=3, padx=(0, 20))
        
        # Category
        ttk.Label(form_frame, text="Category:").grid(row=1, column=0, sticky='w', pady=(10, 0), padx=(0, 10))
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, width=27)
        category_combo['values'] = ('Inventory', 'Utilities', 'Rent', 'Salaries', 'Marketing', 'Maintenance', 'Other')
        category_combo.grid(row=1, column=1, pady=(10, 0), padx=(0, 20))
        
        # Date
        ttk.Label(form_frame, text="Date:").grid(row=1, column=2, sticky='w', pady=(10, 0), padx=(0, 10))
        self.date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        date_entry = ttk.Entry(form_frame, textvariable=self.date_var, width=12)
        date_entry.grid(row=1, column=3, pady=(10, 0), padx=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(add_frame)
        button_frame.pack(fill='x', pady=(15, 0))
        
        add_btn = ttk.Button(button_frame, text="Add Expense", command=self.add_expense)
        add_btn.pack(side='left', padx=(0, 10))
        
        clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_form)
        clear_btn.pack(side='left')
        
        # Expenses list frame
        list_frame = ttk.LabelFrame(main_frame, text="Expense History", padding=15)
        list_frame.pack(fill='both', expand=True)
        
        # Filter frame
        filter_frame = ttk.Frame(list_frame)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter by Category:").pack(side='left', padx=(0, 10))
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, width=20)
        filter_combo['values'] = ('All', 'Inventory', 'Utilities', 'Rent', 'Salaries', 'Marketing', 'Maintenance', 'Other')
        filter_combo.pack(side='left', padx=(0, 10))
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.load_expenses())
        
        ttk.Label(filter_frame, text="Date From:").pack(side='left', padx=(20, 10))
        self.date_from_var = tk.StringVar()
        date_from_entry = ttk.Entry(filter_frame, textvariable=self.date_from_var, width=12)
        date_from_entry.pack(side='left', padx=(0, 10))
        
        ttk.Label(filter_frame, text="To:").pack(side='left', padx=(0, 10))
        self.date_to_var = tk.StringVar()
        date_to_entry = ttk.Entry(filter_frame, textvariable=self.date_to_var, width=12)
        date_to_entry.pack(side='left', padx=(0, 10))
        
        filter_btn = ttk.Button(filter_frame, text="Filter", command=self.load_expenses)
        filter_btn.pack(side='left', padx=(10, 0))
        
        # Treeview
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill='both', expand=True)
        
        columns = ('ID', 'Date', 'Description', 'Category', 'Amount')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        self.tree.heading('ID', text='ID')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Description', text='Description')
        self.tree.heading('Category', text='Category')
        self.tree.heading('Amount', text='Amount')
        
        # Configure columns
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Date', width=100, anchor='center')
        self.tree.column('Description', width=300, anchor='w')
        self.tree.column('Category', width=120, anchor='center')
        self.tree.column('Amount', width=100, anchor='e')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Expense actions frame
        actions_frame = ttk.Frame(list_frame)
        actions_frame.pack(fill='x', pady=(10, 0))
        
        edit_btn = ttk.Button(actions_frame, text="Edit Selected", command=self.edit_expense)
        edit_btn.pack(side='left', padx=(0, 10))
        
        delete_btn = ttk.Button(actions_frame, text="Delete Selected", command=self.delete_expense)
        delete_btn.pack(side='left', padx=(0, 10))
        
        # Total amount label
        self.total_label = ttk.Label(actions_frame, text="Total: $0.00", font=('Arial', 12, 'bold'))
        self.total_label.pack(side='right')
        
    def add_expense(self):
        """Add a new expense"""
        description = self.description_var.get().strip()
        amount_str = self.amount_var.get().strip()
        category = self.category_var.get().strip()
        date_str = self.date_var.get().strip()
        
        if not all([description, amount_str, category, date_str]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
            
        if not validate_number(amount_str):
            messagebox.showerror("Error", "Please enter a valid amount")
            return
            
        amount = float(amount_str)
        
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Please enter date in YYYY-MM-DD format")
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO expenses (description, amount, category, date, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (description, amount, category, date_str, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Expense added successfully")
            self.clear_form()
            self.load_expenses()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add expense: {str(e)}")
            
    def clear_form(self):
        """Clear the expense form"""
        self.description_var.set("")
        self.amount_var.set("")
        self.category_var.set("")
        self.date_var.set(date.today().strftime('%Y-%m-%d'))
        
    def load_expenses(self):
        """Load expenses from database"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query with filters
            query = "SELECT id, date, description, category, amount FROM expenses WHERE 1=1"
            params = []
            
            # Category filter
            if self.filter_var.get() != "All":
                query += " AND category = ?"
                params.append(self.filter_var.get())
                
            # Date filters
            if self.date_from_var.get().strip():
                query += " AND date >= ?"
                params.append(self.date_from_var.get().strip())
                
            if self.date_to_var.get().strip():
                query += " AND date <= ?"
                params.append(self.date_to_var.get().strip())
                
            query += " ORDER BY date DESC, id DESC"
            
            cursor.execute(query, params)
            expenses = cursor.fetchall()
            
            total = 0
            for expense in expenses:
                expense_id, date_str, description, category, amount = expense
                total += amount
                
                # Format amount
                amount_formatted = f"${amount:.2f}"
                
                self.tree.insert('', 'end', values=(expense_id, date_str, description, category, amount_formatted))
                
            # Update total label
            self.total_label.config(text=f"Total: ${total:.2f}")
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load expenses: {str(e)}")
            
    def edit_expense(self):
        """Edit selected expense"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an expense to edit")
            return
            
        item_values = self.tree.item(selected_item[0])['values']
        expense_id = item_values[0]
        
        # Create edit window
        edit_window = tk.Toplevel(self.parent)
        edit_window.title("Edit Expense")
        edit_window.geometry("400x300")
        edit_window.transient(self.parent)
        edit_window.grab_set()
        
        # Center the window
        edit_window.geometry("+%d+%d" % (self.parent.winfo_rootx() + 50, self.parent.winfo_rooty() + 50))
        
        # Get current expense data
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT description, amount, category, date FROM expenses WHERE id = ?", (expense_id,))
            expense_data = cursor.fetchone()
            conn.close()
            
            if not expense_data:
                messagebox.showerror("Error", "Expense not found")
                edit_window.destroy()
                return
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load expense data: {str(e)}")
            edit_window.destroy()
            return
            
        # Create form
        ttk.Label(edit_window, text="Edit Expense", font=('Arial', 14, 'bold')).pack(pady=10)
        
        form_frame = ttk.Frame(edit_window)
        form_frame.pack(padx=20, pady=10, fill='x')
        
        # Description
        ttk.Label(form_frame, text="Description:").grid(row=0, column=0, sticky='w', pady=5)
        edit_description_var = tk.StringVar(value=expense_data[0])
        ttk.Entry(form_frame, textvariable=edit_description_var, width=30).grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Amount
        ttk.Label(form_frame, text="Amount:").grid(row=1, column=0, sticky='w', pady=5)
        edit_amount_var = tk.StringVar(value=str(expense_data[1]))
        ttk.Entry(form_frame, textvariable=edit_amount_var, width=30).grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Category
        ttk.Label(form_frame, text="Category:").grid(row=2, column=0, sticky='w', pady=5)
        edit_category_var = tk.StringVar(value=expense_data[2])
        category_combo = ttk.Combobox(form_frame, textvariable=edit_category_var, width=27)
        category_combo['values'] = ('Inventory', 'Utilities', 'Rent', 'Salaries', 'Marketing', 'Maintenance', 'Other')
        category_combo.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Date
        ttk.Label(form_frame, text="Date:").grid(row=3, column=0, sticky='w', pady=5)
        edit_date_var = tk.StringVar(value=expense_data[3])
        ttk.Entry(form_frame, textvariable=edit_date_var, width=30).grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(pady=20)
        
        def save_changes():
            description = edit_description_var.get().strip()
            amount_str = edit_amount_var.get().strip()
            category = edit_category_var.get().strip()
            date_str = edit_date_var.get().strip()
            
            if not all([description, amount_str, category, date_str]):
                messagebox.showerror("Error", "Please fill in all fields")
                return
                
            if not validate_number(amount_str):
                messagebox.showerror("Error", "Please enter a valid amount")
                return
                
            amount = float(amount_str)
            
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Please enter date in YYYY-MM-DD format")
                return
                
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE expenses 
                    SET description = ?, amount = ?, category = ?, date = ?
                    WHERE id = ?
                ''', (description, amount, category, date_str, expense_id))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Expense updated successfully")
                edit_window.destroy()
                self.load_expenses()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update expense: {str(e)}")
                
        ttk.Button(button_frame, text="Save Changes", command=save_changes).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side='left')
        
    def delete_expense(self):
        """Delete selected expense"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an expense to delete")
            return
            
        item_values = self.tree.item(selected_item[0])['values']
        expense_id = item_values[0]
        description = item_values[2]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the expense '{description}'?"):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Expense deleted successfully")
                self.load_expenses()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete expense: {str(e)}")
