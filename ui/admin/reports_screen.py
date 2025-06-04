"""
Reports Screen Interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict
from logic.report_generator import ReportGenerator
from logic.utils import POSUtils
from datetime import datetime, timedelta
import os

class ReportsTab:
    def __init__(self, parent: ttk.Frame):
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the reports interface"""
        # Main notebook for different report types
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Daily Sales Report
        self.create_daily_report_tab()
        
        # Weekly Sales Report
        self.create_weekly_report_tab()
        
        # Monthly Sales Report
        self.create_monthly_report_tab()
        
        # Expense Report
        self.create_expense_report_tab()
    
    def create_daily_report_tab(self):
        """Create daily sales report tab"""
        daily_frame = ttk.Frame(self.notebook)
        self.notebook.add(daily_frame, text="Daily Sales")
        
        # Controls frame
        controls_frame = ttk.LabelFrame(daily_frame, text="Report Parameters")
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        params_frame = ttk.Frame(controls_frame)
        params_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Date selection
        ttk.Label(params_frame, text="Date:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.daily_date_var = tk.StringVar(value=POSUtils.get_current_date())
        daily_date_entry = ttk.Entry(params_frame, textvariable=self.daily_date_var, width=12)
        daily_date_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 10))
        
        # Buttons
        ttk.Button(params_frame, text="Generate Report", 
                  command=self.generate_daily_report).grid(row=0, column=2, padx=5)
        ttk.Button(params_frame, text="Export CSV", 
                  command=self.export_daily_csv).grid(row=0, column=3, padx=5)
        
        # Report display frame
        report_frame = ttk.LabelFrame(daily_frame, text="Report Results")
        report_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(report_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.daily_text = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10))
        daily_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.daily_text.yview)
        self.daily_text.configure(yscrollcommand=daily_scrollbar.set)
        
        self.daily_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        daily_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Generate today's report by default
        self.generate_daily_report()
    
    def create_weekly_report_tab(self):
        """Create weekly sales report tab"""
        weekly_frame = ttk.Frame(self.notebook)
        self.notebook.add(weekly_frame, text="Weekly Sales")
        
        # Controls frame
        controls_frame = ttk.LabelFrame(weekly_frame, text="Report Parameters")
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        params_frame = ttk.Frame(controls_frame)
        params_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Week start date
        ttk.Label(params_frame, text="Week Start (Monday):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.weekly_date_var = tk.StringVar(value=POSUtils.get_week_start_date())
        weekly_date_entry = ttk.Entry(params_frame, textvariable=self.weekly_date_var, width=12)
        weekly_date_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 10))
        
        # Buttons
        ttk.Button(params_frame, text="Generate Report", 
                  command=self.generate_weekly_report).grid(row=0, column=2, padx=5)
        ttk.Button(params_frame, text="Export CSV", 
                  command=self.export_weekly_csv).grid(row=0, column=3, padx=5)
        
        # Report display
        report_frame = ttk.LabelFrame(weekly_frame, text="Report Results")
        report_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_frame = ttk.Frame(report_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.weekly_text = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10))
        weekly_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.weekly_text.yview)
        self.weekly_text.configure(yscrollcommand=weekly_scrollbar.set)
        
        self.weekly_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        weekly_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_monthly_report_tab(self):
        """Create monthly sales report tab"""
        monthly_frame = ttk.Frame(self.notebook)
        self.notebook.add(monthly_frame, text="Monthly Sales")
        
        # Controls frame
        controls_frame = ttk.LabelFrame(monthly_frame, text="Report Parameters")
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        params_frame = ttk.Frame(controls_frame)
        params_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Month and year selection
        ttk.Label(params_frame, text="Month:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        current_date = datetime.now()
        self.monthly_month_var = tk.IntVar(value=current_date.month)
        self.monthly_year_var = tk.IntVar(value=current_date.year)
        
        month_combo = ttk.Combobox(params_frame, textvariable=self.monthly_month_var,
                                  values=list(range(1, 13)), width=5, state="readonly")
        month_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 5))
        
        ttk.Label(params_frame, text="Year:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(10, 5))
        year_entry = ttk.Entry(params_frame, textvariable=self.monthly_year_var, width=8)
        year_entry.grid(row=0, column=3, sticky=tk.W, pady=5, padx=(5, 10))
        
        # Buttons
        ttk.Button(params_frame, text="Generate Report", 
                  command=self.generate_monthly_report).grid(row=0, column=4, padx=5)
        ttk.Button(params_frame, text="Export CSV", 
                  command=self.export_monthly_csv).grid(row=0, column=5, padx=5)
        
        # Report display
        report_frame = ttk.LabelFrame(monthly_frame, text="Report Results")
        report_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_frame = ttk.Frame(report_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.monthly_text = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10))
        monthly_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.monthly_text.yview)
        self.monthly_text.configure(yscrollcommand=monthly_scrollbar.set)
        
        self.monthly_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        monthly_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_expense_report_tab(self):
        """Create expense report tab"""
        expense_frame = ttk.Frame(self.notebook)
        self.notebook.add(expense_frame, text="Expenses")
        
        # Controls frame
        controls_frame = ttk.LabelFrame(expense_frame, text="Report Parameters")
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        params_frame = ttk.Frame(controls_frame)
        params_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Date range selection
        ttk.Label(params_frame, text="From:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.expense_start_var = tk.StringVar(value=POSUtils.get_current_date())
        expense_start_entry = ttk.Entry(params_frame, textvariable=self.expense_start_var, width=12)
        expense_start_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 10))
        
        ttk.Label(params_frame, text="To:").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.expense_end_var = tk.StringVar(value=POSUtils.get_current_date())
        expense_end_entry = ttk.Entry(params_frame, textvariable=self.expense_end_var, width=12)
        expense_end_entry.grid(row=0, column=3, sticky=tk.W, pady=5, padx=(5, 10))
        
        # Buttons
        ttk.Button(params_frame, text="Generate Report", 
                  command=self.generate_expense_report).grid(row=0, column=4, padx=5)
        
        # Report display
        report_frame = ttk.LabelFrame(expense_frame, text="Report Results")
        report_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_frame = ttk.Frame(report_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.expense_text = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10))
        expense_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.expense_text.yview)
        self.expense_text.configure(yscrollcommand=expense_scrollbar.set)
        
        self.expense_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        expense_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def generate_daily_report(self):
        """Generate daily sales report"""
        try:
            date = self.daily_date_var.get()
            report_data = ReportGenerator.get_daily_sales_report(date)
            
            if not report_data:
                self.daily_text.delete(1.0, tk.END)
                self.daily_text.insert(tk.END, "No data available for the selected date.")
                return
            
            # Format report
            report_text = self.format_daily_report(report_data)
            
            # Display report
            self.daily_text.delete(1.0, tk.END)
            self.daily_text.insert(tk.END, report_text)
            
            # Store report data for export
            self.current_daily_report = report_data
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate daily report: {str(e)}")
    
    def generate_weekly_report(self):
        """Generate weekly sales report"""
        try:
            start_date = self.weekly_date_var.get()
            report_data = ReportGenerator.get_weekly_sales_report(start_date)
            
            if not report_data:
                self.weekly_text.delete(1.0, tk.END)
                self.weekly_text.insert(tk.END, "No data available for the selected week.")
                return
            
            # Format report
            report_text = self.format_weekly_report(report_data)
            
            # Display report
            self.weekly_text.delete(1.0, tk.END)
            self.weekly_text.insert(tk.END, report_text)
            
            # Store report data for export
            self.current_weekly_report = report_data
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate weekly report: {str(e)}")
    
    def generate_monthly_report(self):
        """Generate monthly sales report"""
        try:
            year = self.monthly_year_var.get()
            month = self.monthly_month_var.get()
            report_data = ReportGenerator.get_monthly_sales_report(year, month)
            
            if not report_data:
                self.monthly_text.delete(1.0, tk.END)
                self.monthly_text.insert(tk.END, "No data available for the selected month.")
                return
            
            # Format report
            report_text = self.format_monthly_report(report_data)
            
            # Display report
            self.monthly_text.delete(1.0, tk.END)
            self.monthly_text.insert(tk.END, report_text)
            
            # Store report data for export
            self.current_monthly_report = report_data
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate monthly report: {str(e)}")
    
    def generate_expense_report(self):
        """Generate expense report"""
        try:
            start_date = self.expense_start_var.get()
            end_date = self.expense_end_var.get()
            report_data = ReportGenerator.get_expense_report(start_date, end_date)
            
            if not report_data:
                self.expense_text.delete(1.0, tk.END)
                self.expense_text.insert(tk.END, "No expense data available for the selected period.")
                return
            
            # Format report
            report_text = self.format_expense_report(report_data)
            
            # Display report
            self.expense_text.delete(1.0, tk.END)
            self.expense_text.insert(tk.END, report_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate expense report: {str(e)}")
    
    def format_daily_report(self, data: Dict) -> str:
        """Format daily report for display"""
        report = []
        report.append("=" * 60)
        report.append(f"DAILY SALES REPORT - {data['date']}")
        report.append("=" * 60)
        report.append("")
        
        # Sales summary
        summary = data['sales_summary']
        report.append("SALES SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Orders:     {summary['total_orders']}")
        report.append(f"Total Sales:      {POSUtils.format_currency(summary['total_sales'])}")
        report.append(f"Total Tax:        {POSUtils.format_currency(summary['total_tax'])}")
        report.append(f"Average Order:    {POSUtils.format_currency(summary['average_order'])}")
        report.append("")
        
        # Payment methods
        if data['payment_methods']:
            report.append("PAYMENT METHODS")
            report.append("-" * 40)
            for payment in data['payment_methods']:
                report.append(f"{payment['payment_method'].title():<15} {payment['count']} orders   {POSUtils.format_currency(payment['total'])}")
            report.append("")
        
        # Top items
        if data['top_items']:
            report.append("TOP SELLING ITEMS")
            report.append("-" * 40)
            for i, item in enumerate(data['top_items'][:10], 1):
                report.append(f"{i:2}. {item['name']:<20} Qty: {item['total_quantity']:<5} Revenue: {POSUtils.format_currency(item['total_revenue'])}")
            report.append("")
        
        # Hourly breakdown
        if data['hourly_breakdown']:
            report.append("HOURLY BREAKDOWN")
            report.append("-" * 40)
            for hour in data['hourly_breakdown']:
                hour_12 = int(hour['hour'])
                ampm = "AM" if hour_12 < 12 else "PM"
                if hour_12 == 0:
                    hour_12 = 12
                elif hour_12 > 12:
                    hour_12 -= 12
                
                report.append(f"{hour_12:2}:00 {ampm}   {hour['orders']} orders   {POSUtils.format_currency(hour['sales'])}")
        
        return "\n".join(report)
    
    def format_weekly_report(self, data: Dict) -> str:
        """Format weekly report for display"""
        report = []
        report.append("=" * 60)
        report.append(f"WEEKLY SALES REPORT")
        report.append(f"Week of {data['week_start']} to {data['week_end']}")
        report.append("=" * 60)
        report.append("")
        
        # Week totals
        totals = data['week_totals']
        report.append("WEEK SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Orders:     {totals['total_orders']}")
        report.append(f"Total Sales:      {POSUtils.format_currency(totals['total_sales'])}")
        report.append(f"Total Tax:        {POSUtils.format_currency(totals['total_tax'])}")
        report.append(f"Average Order:    {POSUtils.format_currency(totals['average_order'])}")
        report.append("")
        
        # Daily breakdown
        if data['daily_breakdown']:
            report.append("DAILY BREAKDOWN")
            report.append("-" * 40)
            for day in data['daily_breakdown']:
                day_name = datetime.strptime(day['date'], '%Y-%m-%d').strftime('%A')
                report.append(f"{day['date']} ({day_name})   {day['orders']} orders   {POSUtils.format_currency(day['sales'])}")
        
        return "\n".join(report)
    
    def format_monthly_report(self, data: Dict) -> str:
        """Format monthly report for display"""
        report = []
        month_name = datetime(data['year'], data['month'], 1).strftime('%B')
        report.append("=" * 60)
        report.append(f"MONTHLY SALES REPORT - {month_name} {data['year']}")
        report.append("=" * 60)
        report.append("")
        
        # Month totals
        totals = data['month_totals']
        report.append("MONTH SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Orders:     {totals['total_orders']}")
        report.append(f"Total Sales:      {POSUtils.format_currency(totals['total_sales'])}")
        report.append(f"Total Tax:        {POSUtils.format_currency(totals['total_tax'])}")
        report.append(f"Average Order:    {POSUtils.format_currency(totals['average_order'])}")
        report.append("")
        
        # Category performance
        if data['category_performance']:
            report.append("CATEGORY PERFORMANCE")
            report.append("-" * 40)
            for cat in data['category_performance']:
                report.append(f"{cat['category']:<20} Qty: {cat['total_quantity']:<8} Revenue: {POSUtils.format_currency(cat['total_revenue'])}")
            report.append("")
        
        # Note about daily breakdown
        if data['daily_breakdown']:
            report.append(f"Daily data available for {len(data['daily_breakdown'])} days this month.")
        
        return "\n".join(report)
    
    def format_expense_report(self, data: Dict) -> str:
        """Format expense report for display"""
        report = []
        report.append("=" * 60)
        report.append(f"EXPENSE REPORT")
        report.append(f"Period: {data['start_date']} to {data['end_date']}")
        report.append("=" * 60)
        report.append("")
        
        # Totals
        totals = data['totals']
        report.append("EXPENSE SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Expenses:   {totals['total_count']}")
        report.append(f"Total Amount:     {POSUtils.format_currency(totals['total_amount'])}")
        report.append("")
        
        # By category
        if data['by_category']:
            report.append("BY CATEGORY")
            report.append("-" * 40)
            for cat in data['by_category']:
                report.append(f"{cat['category']:<20} {cat['count']} items   {POSUtils.format_currency(cat['total'])}")
            report.append("")
        
        # Daily breakdown
        if data['daily_breakdown']:
            report.append("DAILY BREAKDOWN")
            report.append("-" * 40)
            for day in data['daily_breakdown']:
                report.append(f"{day['date']}   {day['count']} items   {POSUtils.format_currency(day['total'])}")
        
        return "\n".join(report)
    
    def export_daily_csv(self):
        """Export daily report to CSV"""
        if not hasattr(self, 'current_daily_report'):
            messagebox.showwarning("Warning", "Please generate a report first")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Daily Report"
        )
        
        if file_path:
            try:
                if ReportGenerator.export_sales_report_csv(self.current_daily_report, file_path):
                    messagebox.showinfo("Success", f"Report exported to {file_path}")
                else:
                    messagebox.showerror("Error", "Failed to export report")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {str(e)}")
    
    def export_weekly_csv(self):
        """Export weekly report to CSV"""
        if not hasattr(self, 'current_weekly_report'):
            messagebox.showwarning("Warning", "Please generate a report first")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Weekly Report"
        )
        
        if file_path:
            try:
                if ReportGenerator.export_sales_report_csv(self.current_weekly_report, file_path):
                    messagebox.showinfo("Success", f"Report exported to {file_path}")
                else:
                    messagebox.showerror("Error", "Failed to export report")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {str(e)}")
    
    def export_monthly_csv(self):
        """Export monthly report to CSV"""
        if not hasattr(self, 'current_monthly_report'):
            messagebox.showwarning("Warning", "Please generate a report first")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Monthly Report"
        )
        
        if file_path:
            try:
                if ReportGenerator.export_sales_report_csv(self.current_monthly_report, file_path):
                    messagebox.showinfo("Success", f"Report exported to {file_path}")
                else:
                    messagebox.showerror("Error", "Failed to export report")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {str(e)}")
