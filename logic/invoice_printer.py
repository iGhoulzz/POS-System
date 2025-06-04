"""
Invoice/Receipt printing functionality
"""

from datetime import datetime
from typing import Dict, List
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import os
from config import COMPANY_NAME, COMPANY_ADDRESS, COMPANY_PHONE

class InvoicePrinter:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.black,
            alignment=1  # Center alignment
        )
        
    def generate_receipt_pdf(self, order: Dict, order_items: List[Dict], output_path: str) -> bool:
        """
        Generate a PDF receipt for an order
        
        Args:
            order: Order dictionary
            order_items: List of order items
            output_path: Path to save the PDF
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            story = []
            
            # Company header
            title = Paragraph(COMPANY_NAME, self.title_style)
            story.append(title)
            story.append(Spacer(1, 12))
            
            address = Paragraph(f"{COMPANY_ADDRESS}<br/>{COMPANY_PHONE}", self.styles['Normal'])
            story.append(address)
            story.append(Spacer(1, 12))
            
            # Receipt title
            receipt_title = Paragraph("RECEIPT", self.title_style)
            story.append(receipt_title)
            story.append(Spacer(1, 12))
            
            # Order information
            order_info = [
                ['Order Number:', order['order_number']],
                ['Date:', order['created_at']],
                ['Customer:', order['customer_name'] or 'Walk-in'],
                ['Order Type:', order['order_type'].replace('_', ' ').title()],
                ['Payment Method:', order['payment_method']],
            ]
            
            order_table = Table(order_info, colWidths=[2*inch, 3*inch])
            order_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(order_table)
            story.append(Spacer(1, 12))
            
            # Items table
            items_data = [['Item', 'Qty', 'Price', 'Total']]
            for item in order_items:
                items_data.append([
                    item['item_name'],
                    str(item['quantity']),
                    f"${item['unit_price']:.2f}",
                    f"${item['total_price']:.2f}"
                ])
            
            items_table = Table(items_data, colWidths=[3*inch, 0.7*inch, 1*inch, 1*inch])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Item names left-aligned
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(items_table)
            story.append(Spacer(1, 12))
            
            # Totals
            subtotal = order['total_amount'] - order['tax_amount']
            totals_data = [
                ['Subtotal:', f"${subtotal:.2f}"],
                ['Tax:', f"${order['tax_amount']:.2f}"],
                ['Total:', f"${order['total_amount']:.2f}"],
            ]
            
            totals_table = Table(totals_data, colWidths=[4*inch, 1.5*inch])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
            ]))
            story.append(totals_table)
            story.append(Spacer(1, 24))
            
            # Footer
            footer = Paragraph("Thank you for your business!", self.styles['Normal'])
            story.append(footer)
            
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error generating receipt PDF: {e}")
            return False
    
    def print_receipt_text(self, order: Dict, order_items: List[Dict]) -> str:
        """
        Generate a text-based receipt (for thermal printers)
        
        Args:
            order: Order dictionary
            order_items: List of order items
            
        Returns:
            Formatted receipt text
        """
        receipt = []
        width = 40  # Character width for thermal printer
        
        # Header
        receipt.append(COMPANY_NAME.center(width))
        receipt.append(COMPANY_ADDRESS.center(width))
        receipt.append(COMPANY_PHONE.center(width))
        receipt.append("=" * width)
        receipt.append("RECEIPT".center(width))
        receipt.append("=" * width)
        receipt.append("")
        
        # Order info
        receipt.append(f"Order #: {order['order_number']}")
        receipt.append(f"Date: {order['created_at']}")
        receipt.append(f"Customer: {order['customer_name'] or 'Walk-in'}")
        receipt.append(f"Type: {order['order_type'].replace('_', ' ').title()}")
        receipt.append(f"Payment: {order['payment_method']}")
        receipt.append("-" * width)
        
        # Items
        for item in order_items:
            name = item['item_name']
            qty = item['quantity']
            price = item['total_price']
            
            # Truncate name if too long
            if len(name) > 25:
                name = name[:22] + "..."
            
            line = f"{name:<25} {qty:>3} ${price:>8.2f}"
            receipt.append(line)
            
            if item.get('special_instructions'):
                receipt.append(f"  Note: {item['special_instructions']}")
        
        receipt.append("-" * width)
        
        # Totals
        subtotal = order['total_amount'] - order['tax_amount']
        receipt.append(f"{'Subtotal:':<25} ${subtotal:>12.2f}")
        receipt.append(f"{'Tax:':<25} ${order['tax_amount']:>12.2f}")
        receipt.append("=" * width)
        receipt.append(f"{'TOTAL:':<25} ${order['total_amount']:>12.2f}")
        receipt.append("=" * width)
        receipt.append("")
        receipt.append("Thank you for your business!".center(width))
        receipt.append("")
        
        return "\n".join(receipt)
    
    def save_receipt_text(self, order: Dict, order_items: List[Dict], output_path: str) -> bool:
        """
        Save text receipt to file
        
        Args:
            order: Order dictionary
            order_items: List of order items
            output_path: Path to save the text file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            receipt_text = self.print_receipt_text(order, order_items)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(receipt_text)
            return True
        except Exception as e:
            print(f"Error saving receipt text: {e}")
            return False
