"""
Smart Inventory & Expiry Management System
FILE: gui/reports_tab.py
PURPOSE: All reports — low stock, inventory valuation, sales summary, waste.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from modules.reports import (
    get_low_stock_report, get_inventory_valuation,
    get_sales_summary, get_waste_report
)


class ReportsTab(ttk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent)
        self.colors = colors
        self.configure(style='TFrame')
        self._build()
        self.refresh()

    def _build(self):
        C = self.colors

        # ── Header ────────────────────────────────────────────
        header = tk.Frame(self, bg=C['bg'], pady=12)
        header.pack(fill='x', padx=24)
        tk.Label(header, text="Reports", bg=C['bg'], fg=C['accent'],
                 font=('Segoe UI', 16, 'bold')).pack(side='left')
        ttk.Button(header, text="🔄 Refresh All",
                   style='Accent.TButton', command=self.refresh).pack(side='right')

        # ── Report selector tabs ──────────────────────────────
        self.inner_nb = ttk.Notebook(self)
        self.inner_nb.pack(fill='both', expand=True, padx=24, pady=(0, 16))

        # 1. Low Stock
        self._low_frame = ttk.Frame(self.inner_nb)
        self.inner_nb.add(self._low_frame, text='  🔴  Low Stock  ')
        self._low_tree = self._make_table(self._low_frame,
            ('Product', 'Category', 'Reorder Level', 'Current Stock', 'Shortage'),
            (180, 120, 120, 120, 100))

        # 2. Inventory Valuation
        self._val_frame = ttk.Frame(self.inner_nb)
        self.inner_nb.add(self._val_frame, text='  💰  Valuation  ')
        self._val_tree = self._make_table(self._val_frame,
            ('Product', 'Category', 'Total Units', 'Stock Value (₹)'),
            (200, 140, 120, 140))

        # 3. Sales Summary
        self._sales_frame = ttk.Frame(self.inner_nb)
        self.inner_nb.add(self._sales_frame, text='  📈  Sales Summary  ')
        self._sales_tree = self._make_table(self._sales_frame,
            ('Product', 'Category', 'Units Sold', 'Revenue (₹)', 'Cost (₹)', 'Profit (₹)'),
            (180, 120, 100, 120, 120, 120))

        # 4. Waste Report
        self._waste_frame = ttk.Frame(self.inner_nb)
        self.inner_nb.add(self._waste_frame, text='  🗑️  Waste  ')
        self._waste_tree = self._make_table(self._waste_frame,
            ('Product', 'Category', 'Total Wasted', 'Waste Value (₹)'),
            (200, 140, 120, 140))

        # Colour tags
        for tree in [self._low_tree, self._val_tree, self._sales_tree, self._waste_tree]:
            tree.tag_configure('highlight', background='#2a2a3e', foreground=self.colors['accent'])
            tree.tag_configure('danger',    background='#3b1e2e', foreground=self.colors['danger'])

    def _make_table(self, parent, cols, widths):
        frame = tk.Frame(parent, bg=self.colors['bg'])
        frame.pack(fill='both', expand=True, padx=8, pady=8)

        tree = ttk.Treeview(frame, columns=cols, show='headings')
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor='center')

        vsb = ttk.Scrollbar(frame, orient='vertical',   command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        return tree

    def refresh(self):
        self._load_low_stock()
        self._load_valuation()
        self._load_sales_summary()
        self._load_waste()

    def _load_low_stock(self):
        for row in self._low_tree.get_children():
            self._low_tree.delete(row)
        try:
            rows = get_low_stock_report()
            for r in rows:
                tag = 'danger' if r['current_stock'] == 0 else 'highlight'
                self._low_tree.insert('', 'end', values=(
                    r['product_name'], r['category_name'],
                    r['reorder_level'], r['current_stock'], r['shortage']
                ), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Error", f"Low stock report failed:\n{e}")

    def _load_valuation(self):
        for row in self._val_tree.get_children():
            self._val_tree.delete(row)
        try:
            rows = get_inventory_valuation()
            for i, r in enumerate(rows):
                tag = 'highlight' if i % 2 == 0 else ''
                self._val_tree.insert('', 'end', values=(
                    r['product_name'], r['category_name'],
                    r['total_units'], f"₹{r['stock_value']:,.2f}"
                ), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Error", f"Valuation report failed:\n{e}")

    def _load_sales_summary(self):
        for row in self._sales_tree.get_children():
            self._sales_tree.delete(row)
        try:
            rows = get_sales_summary()
            for r in rows:
                profit = float(r['profit'] or 0)
                tag = 'highlight' if profit >= 0 else 'danger'
                self._sales_tree.insert('', 'end', values=(
                    r['product_name'], r['category_name'],
                    r['units_sold'],
                    f"₹{r['revenue']:,.2f}",
                    f"₹{r['cost']:,.2f}",
                    f"₹{profit:,.2f}"
                ), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Error", f"Sales summary failed:\n{e}")

    def _load_waste(self):
        for row in self._waste_tree.get_children():
            self._waste_tree.delete(row)
        try:
            rows = get_waste_report()
            for r in rows:
                self._waste_tree.insert('', 'end', values=(
                    r['product_name'], r['category_name'],
                    r['total_wasted'], f"₹{r['waste_value']:,.2f}"
                ), tags=('danger',))
        except Exception as e:
            messagebox.showerror("Error", f"Waste report failed:\n{e}")
