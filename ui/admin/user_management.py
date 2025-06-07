import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from logic.user_manager import UserManager
from logic.utils import hash_password

class UserManagement:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        # UserManager is a static class, no need to instantiate
        
        self.create_widgets()
        self.load_users()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="User Management", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Add user frame
        add_frame = ttk.LabelFrame(main_frame, text="Add New User", padding=15)
        add_frame.pack(fill='x', pady=(0, 20))
        
        # User form
        form_frame = ttk.Frame(add_frame)
        form_frame.pack(fill='x')
        
        # Username
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(form_frame, textvariable=self.username_var, width=20)
        username_entry.grid(row=0, column=1, padx=(0, 20))
        
        # Password
        ttk.Label(form_frame, text="Password:").grid(row=0, column=2, sticky='w', padx=(0, 10))
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(form_frame, textvariable=self.password_var, show='*', width=20)
        password_entry.grid(row=0, column=3, padx=(0, 20))
        
        # Full Name
        ttk.Label(form_frame, text="Full Name:").grid(row=1, column=0, sticky='w', pady=(10, 0), padx=(0, 10))
        self.fullname_var = tk.StringVar()
        fullname_entry = ttk.Entry(form_frame, textvariable=self.fullname_var, width=20)
        fullname_entry.grid(row=1, column=1, pady=(10, 0), padx=(0, 20))
        
        # Role
        ttk.Label(form_frame, text="Role:").grid(row=1, column=2, sticky='w', pady=(10, 0), padx=(0, 10))
        self.role_var = tk.StringVar()
        role_combo = ttk.Combobox(form_frame, textvariable=self.role_var, width=17)
        role_combo['values'] = ('admin', 'cashier', 'kitchen')
        role_combo.grid(row=1, column=3, pady=(10, 0), padx=(0, 20))
        
        # Email
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky='w', pady=(10, 0), padx=(0, 10))
        self.email_var = tk.StringVar()
        email_entry = ttk.Entry(form_frame, textvariable=self.email_var, width=30)
        email_entry.grid(row=2, column=1, columnspan=2, pady=(10, 0), padx=(0, 20), sticky='ew')
        
        # Active status
        self.active_var = tk.BooleanVar(value=True)
        active_check = ttk.Checkbutton(form_frame, text="Active User", variable=self.active_var)
        active_check.grid(row=2, column=3, pady=(10, 0), sticky='w')
        
        # Buttons
        button_frame = ttk.Frame(add_frame)
        button_frame.pack(fill='x', pady=(15, 0))
        
        add_btn = ttk.Button(button_frame, text="Add User", command=self.add_user)
        add_btn.pack(side='left', padx=(0, 10))
        
        clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_form)
        clear_btn.pack(side='left')
        
        # Users list frame
        list_frame = ttk.LabelFrame(main_frame, text="User List", padding=15)
        list_frame.pack(fill='both', expand=True)
        
        # Filter frame
        filter_frame = ttk.Frame(list_frame)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter by Role:").pack(side='left', padx=(0, 10))
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, width=15)
        filter_combo['values'] = ('All', 'admin', 'cashier', 'kitchen')
        filter_combo.pack(side='left', padx=(0, 10))
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.load_users())
        
        ttk.Label(filter_frame, text="Status:").pack(side='left', padx=(20, 10))
        self.status_filter_var = tk.StringVar(value="All")
        status_filter_combo = ttk.Combobox(filter_frame, textvariable=self.status_filter_var, width=15)
        status_filter_combo['values'] = ('All', 'Active', 'Inactive')
        status_filter_combo.pack(side='left', padx=(0, 10))
        status_filter_combo.bind('<<ComboboxSelected>>', lambda e: self.load_users())
        
        # Treeview
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill='both', expand=True)
        
        columns = ('ID', 'Username', 'Full Name', 'Email', 'Role', 'Status', 'Last Login')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        
        # Define headings
        self.tree.heading('ID', text='ID')
        self.tree.heading('Username', text='Username')
        self.tree.heading('Full Name', text='Full Name')
        self.tree.heading('Email', text='Email')
        self.tree.heading('Role', text='Role')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Last Login', text='Last Login')
        
        # Configure columns
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Username', width=120, anchor='w')
        self.tree.column('Full Name', width=180, anchor='w')
        self.tree.column('Email', width=200, anchor='w')
        self.tree.column('Role', width=80, anchor='center')
        self.tree.column('Status', width=80, anchor='center')
        self.tree.column('Last Login', width=150, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # User actions frame
        actions_frame = ttk.Frame(list_frame)
        actions_frame.pack(fill='x', pady=(10, 0))
        
        edit_btn = ttk.Button(actions_frame, text="Edit Selected", command=self.edit_user)
        edit_btn.pack(side='left', padx=(0, 10))
        
        toggle_btn = ttk.Button(actions_frame, text="Toggle Status", command=self.toggle_user_status)
        toggle_btn.pack(side='left', padx=(0, 10))
        
        password_btn = ttk.Button(actions_frame, text="Change Password", command=self.change_password)
        password_btn.pack(side='left', padx=(0, 10))
        
        delete_btn = ttk.Button(actions_frame, text="Delete Selected", command=self.delete_user)
        delete_btn.pack(side='left')
        
        # User count label
        self.count_label = ttk.Label(actions_frame, text="Total Users: 0", font=('Arial', 10))
        self.count_label.pack(side='right')
        
    def add_user(self):
        """Add a new user"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        fullname = self.fullname_var.get().strip()
        role = self.role_var.get().strip()
        email = self.email_var.get().strip()
        is_active = self.active_var.get()
        
        if not all([username, password, fullname, role]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return
            
        if len(password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters long")
            return
            
        if role not in ['admin', 'cashier', 'kitchen']:
            messagebox.showerror("Error", "Please select a valid role")
            return
            
        # Check if username already exists
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                conn.close()
                messagebox.showerror("Error", "Username already exists")
                return
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")
            return
            
        # Add user
        if UserManager.create_user(username, password, role, fullname, email if email else None, is_active):
            messagebox.showinfo("Success", "User added successfully")
            self.clear_form()
            self.load_users()
        else:
            messagebox.showerror("Error", "Failed to add user")
            
    def clear_form(self):
        """Clear the user form"""
        self.username_var.set("")
        self.password_var.set("")
        self.fullname_var.set("")
        self.role_var.set("")
        self.email_var.set("")
        self.active_var.set(True)
        
    def load_users(self):
        """Load users from database"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query with filters
            query = "SELECT id, username, full_name, email, role, is_active, last_login FROM users WHERE 1=1"
            params = []
            
            # Role filter
            if self.filter_var.get() != "All":
                query += " AND role = ?"
                params.append(self.filter_var.get())
                
            # Status filter
            if self.status_filter_var.get() == "Active":
                query += " AND is_active = 1"
            elif self.status_filter_var.get() == "Inactive":
                query += " AND is_active = 0"
                
            query += " ORDER BY username"
            
            cursor.execute(query, params)
            users = cursor.fetchall()
            
            for user in users:
                user_id, username, full_name, email, role, is_active, last_login = user
                
                status = "Active" if is_active else "Inactive"
                last_login_str = last_login if last_login else "Never"
                
                self.tree.insert('', 'end', values=(user_id, username, full_name or "", email or "", role, status, last_login_str))
                
            # Update count label
            self.count_label.config(text=f"Total Users: {len(users)}")
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users: {str(e)}")
            
    def edit_user(self):
        """Edit selected user"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a user to edit")
            return
            
        item_values = self.tree.item(selected_item[0])['values']
        user_id = item_values[0]
        
        # Create edit window
        edit_window = tk.Toplevel(self.parent)
        edit_window.title("Edit User")
        edit_window.geometry("450x350")
        edit_window.transient(self.parent)
        edit_window.grab_set()
        
        # Center the window
        edit_window.geometry("+%d+%d" % (self.parent.winfo_rootx() + 50, self.parent.winfo_rooty() + 50))
        
        # Get current user data
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT username, full_name, email, role, is_active FROM users WHERE id = ?", (user_id,))
            user_data = cursor.fetchone()
            conn.close()
            
            if not user_data:
                messagebox.showerror("Error", "User not found")
                edit_window.destroy()
                return
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load user data: {str(e)}")
            edit_window.destroy()
            return
            
        # Create form
        ttk.Label(edit_window, text="Edit User", font=('Arial', 14, 'bold')).pack(pady=10)
        
        form_frame = ttk.Frame(edit_window)
        form_frame.pack(padx=20, pady=10, fill='both', expand=True)
        
        # Username (read-only)
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky='w', pady=5)
        username_label = ttk.Label(form_frame, text=user_data[0], font=('Arial', 10, 'bold'))
        username_label.grid(row=0, column=1, pady=5, padx=(10, 0), sticky='w')
        
        # Full Name
        ttk.Label(form_frame, text="Full Name:").grid(row=1, column=0, sticky='w', pady=5)
        edit_fullname_var = tk.StringVar(value=user_data[1] or "")
        ttk.Entry(form_frame, textvariable=edit_fullname_var, width=30).grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Email
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky='w', pady=5)
        edit_email_var = tk.StringVar(value=user_data[2] or "")
        ttk.Entry(form_frame, textvariable=edit_email_var, width=30).grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Role
        ttk.Label(form_frame, text="Role:").grid(row=3, column=0, sticky='w', pady=5)
        edit_role_var = tk.StringVar(value=user_data[3])
        role_combo = ttk.Combobox(form_frame, textvariable=edit_role_var, width=27)
        role_combo['values'] = ('admin', 'cashier', 'kitchen')
        role_combo.grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # Active status
        edit_active_var = tk.BooleanVar(value=bool(user_data[4]))
        active_check = ttk.Checkbutton(form_frame, text="Active User", variable=edit_active_var)
        active_check.grid(row=4, column=1, pady=10, sticky='w', padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(pady=20)
        
        def save_changes():
            fullname = edit_fullname_var.get().strip()
            email = edit_email_var.get().strip()
            role = edit_role_var.get().strip()
            is_active = edit_active_var.get()
            
            if not fullname:
                messagebox.showerror("Error", "Please enter a full name")
                return
                
            if role not in ['admin', 'cashier', 'kitchen']:
                messagebox.showerror("Error", "Please select a valid role")
                return
                
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE users 
                    SET full_name = ?, email = ?, role = ?, is_active = ?
                    WHERE id = ?
                ''', (fullname, email, role, is_active, user_id))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "User updated successfully")
                edit_window.destroy()
                self.load_users()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update user: {str(e)}")
                
        ttk.Button(button_frame, text="Save Changes", command=save_changes).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side='left')
        
    def toggle_user_status(self):
        """Toggle user active status"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a user to toggle status")
            return
            
        item_values = self.tree.item(selected_item[0])['values']
        user_id = item_values[0]
        username = item_values[1]
        current_status = item_values[5]
        
        new_status = "Inactive" if current_status == "Active" else "Active"
        
        if messagebox.askyesno("Confirm", f"Change {username}'s status to {new_status}?"):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                new_active = 1 if new_status == "Active" else 0
                cursor.execute("UPDATE users SET is_active = ? WHERE id = ?", (new_active, user_id))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", f"User status changed to {new_status}")
                self.load_users()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update user status: {str(e)}")
                
    def change_password(self):
        """Change user password"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a user to change password")
            return
            
        item_values = self.tree.item(selected_item[0])['values']
        user_id = item_values[0]
        username = item_values[1]
        
        # Create password change window
        pwd_window = tk.Toplevel(self.parent)
        pwd_window.title("Change Password")
        pwd_window.geometry("350x200")
        pwd_window.transient(self.parent)
        pwd_window.grab_set()
        
        # Center the window
        pwd_window.geometry("+%d+%d" % (self.parent.winfo_rootx() + 100, self.parent.winfo_rooty() + 100))
        
        # Create form
        ttk.Label(pwd_window, text=f"Change Password for: {username}", font=('Arial', 12, 'bold')).pack(pady=15)
        
        form_frame = ttk.Frame(pwd_window)
        form_frame.pack(padx=20, pady=10)
        
        ttk.Label(form_frame, text="New Password:").grid(row=0, column=0, sticky='w', pady=5)
        new_password_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=new_password_var, show='*', width=25).grid(row=0, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(form_frame, text="Confirm Password:").grid(row=1, column=0, sticky='w', pady=5)
        confirm_password_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=confirm_password_var, show='*', width=25).grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(pwd_window)
        button_frame.pack(pady=20)
        
        def save_password():
            new_password = new_password_var.get().strip()
            confirm_password = confirm_password_var.get().strip()
            
            if not new_password:
                messagebox.showerror("Error", "Please enter a new password")
                return
                
            if len(new_password) < 4:
                messagebox.showerror("Error", "Password must be at least 4 characters long")
                return
                
            if new_password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match")
                return
                
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                hashed_password = hash_password(new_password)
                cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed_password, user_id))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Password changed successfully")
                pwd_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to change password: {str(e)}")
                
        ttk.Button(button_frame, text="Change Password", command=save_password).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=pwd_window.destroy).pack(side='left')
        
    def delete_user(self):
        """Delete selected user"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a user to delete")
            return
            
        item_values = self.tree.item(selected_item[0])['values']
        user_id = item_values[0]
        username = item_values[1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{username}'?\n\nThis action cannot be undone."):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Check if this is the last admin user
                cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = 1")
                admin_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
                user_role = cursor.fetchone()[0]
                
                if user_role == 'admin' and admin_count <= 1:
                    conn.close()
                    messagebox.showerror("Error", "Cannot delete the last active admin user")
                    return
                
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "User deleted successfully")
                self.load_users()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete user: {str(e)}")
