"""
Smart Inventory & Expiry Management System
FILE: gui/sales_tab.py
PURPOSE: Process FIFO sales and view sales history.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from modules.sales_manager import process_sale, get_sales_history, get_today_sales_summary
from modules.stock_manager import get_all_products, get_product_stock


class SalesTab(ttk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent)
        self.colors = colors
        self.configure(style='TFrame')
        self._build()
        self.refresh()

    def _build(self):
        C = self.colors

        # ── Split: left = form, right = today summary ─────────
        top = tk.Frame(self, bg=C['bg'])
        top.pack(fill='x', padx=24, pady=12)

        # Page title
        tk.Label(top, text="Sales", bg=C['bg'], fg=C['accent'],
                 font=('Segoe UI', 16, 'bold')).pack(side='left')
        ttk.Button(top, text="🔄 Refresh", style='Accent.TButton',
                   command=self.refresh).pack(side='right')

        # ── Sale form card ────────────────────────────────────
        form_card = tk.Frame(self, bg=C['card'], padx=20, pady=16)
        form_card.pack(fill='x', padx=24, pady=(0, 12))

        tk.Label(form_card, text="Process New Sale (FIFO)",
                 bg=C['card'], fg=C['accent'],
                 font=('Segoe UI', 12, 'bold')).grid(row=0, column=0, columnspan=4,
                                                      sticky='w', pady=(0, 12))

        # Product selector
        tk.Label(form_card, text="Product", bg=C['card'],
                 fg=C['text_dim'], font=('Segoe UI', 9)).grid(row=1, column=0, sticky='w', padx=(0, 8))
        self.product_combo = ttk.Combobox(form_card, state='readonly',
                                          font=('Segoe UI', 10), width=28)
        self.product_combo.grid(row=2, column=0, padx=(0, 12), ipady=4)
        self.product_combo.bind('<<ComboboxSelected>>', self._on_product_select)

        # Available stock label
        tk.Label(form_card, text="Available Stock", bg=C['card'],
                 fg=C['text_dim'], font=('Segoe UI', 9)).grid(row=1, column=1, sticky='w', padx=(0, 8))
        self.stock_var = tk.StringVar(value='—')
        tk.Label(form_card, textvariable=self.stock_var, bg=C['card'],
                 fg=C['accent2'], font=('Segoe UI', 14, 'bold')).grid(row=2, column=1, padx=(0, 12))

        # Quantity
        tk.Label(form_card, text="Quantity", bg=C['card'],
                 fg=C['text_dim'], font=('Segoe UI', 9)).grid(row=1, column=2, sticky='w', padx=(0, 8))
        self.qty_entry = ttk.Entry(form_card, font=('Segoe UI', 10), width=10)
        self.qty_entry.grid(row=2, column=2, padx=(0, 12), ipady=4)

        # Selling price
        tk.Label(form_card, text="Selling Price (₹/unit)", bg=C['card'],
                 fg=C['text_dim'], font=('Segoe UI', 9)).grid(row=1, column=3, sticky='w')
        self.price_entry = ttk.Entry(form_card, font=('Segoe UI', 10), width=12)
        self.price_entry.grid(row=2, column=3, padx=(0, 12), ipady=4)

        ttk.Button(form_card, text="✅  Process Sale (FIFO)",
                   style='Accent.TButton',
                   command=self._process_sale).grid(row=2, column=4, padx=(12, 0))

        # Today summary
        self.summary_var = tk.StringVar(value="")
        tk.Label(form_card, textvariable=self.summary_var,
                 bg=C['card'], fg=C['text_dim'],
                 font=('Segoe UI', 9)).grid(row=3, column=0, columnspan=5,
                                             sticky='w', pady=(10, 0))

        # ── Sales history table ───────────────────────────────
        tk.Label(self, text="Sales History",
                 bg=C['bg'], fg=C['accent'],
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w', padx=24, pady=(4, 4))

        table_frame = tk.Frame(self, bg=C['bg'])
        table_frame.pack(fill='both', expand=True, padx=24, pady=(0, 16))

        cols = ('Sale ID', 'Product', 'Category', 'Batch ID',
                'Qty Sold', 'Sale Date', 'Price/Unit', 'Revenue', 'Cost', 'Profit')
        self.tree = ttk.Treeview(table_frame, columns=cols, show='headings')
        widths = [60, 160, 110, 70, 80, 100, 90, 90, 90, 90]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor='center')

        vsb = ttk.Scrollbar(table_frame, orient='vertical',   command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.tree.tag_configure('profit', background=C['card'],  foreground=C['accent2'])
        self.tree.tag_configure('loss',   background='#3b1e2e', foreground=C['danger'])

        self._load_products()

    def _load_products(self, preserve=None):
        try:
            products = get_all_products()
            self._product_map = {p['product_name']: p['product_id'] for p in products}
            self.product_combo['values'] = list(self._product_map.keys())
            if self._product_map:
                if preserve and preserve in self._product_map:
                    self.product_combo.set(preserve)
                else:
                    self.product_combo.current(0)
                self._on_product_select()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load products:\n{e}")

    def _on_product_select(self, event=None):
        name = self.product_combo.get()
        if name and name in self._product_map:
            try:
                stock = get_product_stock(self._product_map[name])
                self.stock_var.set(str(stock))
            except Exception:
                self.stock_var.set('?')

    def _process_sale(self):
        try:
            name  = self.product_combo.get()
            pid   = self._product_map[name]
            qty   = int(self.qty_entry.get().strip())
            price = float(self.price_entry.get().strip())
            result = process_sale(pid, qty, price)
            messagebox.showinfo("Sale Processed",
                f"✅  Sold {result['total_sold']} unit(s) of '{name}' using FIFO.")
            self.qty_entry.delete(0, 'end')
            self.price_entry.delete(0, 'end')
            self._on_product_select()
            self.refresh()
        except Exception as e:
            messagebox.showerror("Sale Failed", str(e))

    def refresh(self):
        # Refresh products to catch any new products added from Inventory tab
        current_sel = self.product_combo.get() if hasattr(self, 'product_combo') else None
        self._load_products(preserve=current_sel)

        # Today summary
        try:
            s = get_today_sales_summary()
            if s:
                self.summary_var.set(
                    f"Today:  {s['transactions']} transaction(s)  |  "
                    f"{s['units_sold']} units sold  |  Revenue: ₹{s['revenue']:,.2f}"
                )
        except Exception:
            pass

        # Sales history
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            rows = get_sales_history()
            for r in rows:
                profit = float(r['profit'] or 0)
                tag = 'profit' if profit >= 0 else 'loss'
                self.tree.insert('', 'end', values=(
                    r['sale_id'], r['product_name'], r['category_name'],
                    r['batch_id'], r['quantity_sold'], str(r['sale_date']),
                    f"₹{r['selling_price']}", f"₹{r['revenue']}",
                    f"₹{r['cost']}", f"₹{profit}"
                ), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load sales:\n{e}")
