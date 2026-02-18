"""
Smart Inventory & Expiry Management System
FILE: gui/inventory_tab.py
PURPOSE: View all inventory, add batches, add products/suppliers/categories.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from modules.stock_manager import (
    get_all_inventory, add_batch, get_all_products,
    get_all_suppliers, get_all_categories,
    add_product, add_supplier, add_category
)


class InventoryTab(ttk.Frame):
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
        tk.Label(header, text="Inventory", bg=C['bg'], fg=C['accent'],
                 font=('Segoe UI', 16, 'bold')).pack(side='left')
        ttk.Button(header, text="🔄 Refresh",
                   style='Accent.TButton', command=self.refresh).pack(side='right')
        ttk.Button(header, text="+ Add Batch",
                   style='Accent.TButton', command=self._open_add_batch).pack(side='right', padx=(0, 8))
        ttk.Button(header, text="+ Add Product",
                   style='Accent.TButton', command=self._open_add_product).pack(side='right', padx=(0, 8))
        ttk.Button(header, text="+ Add Supplier",
                   style='Accent.TButton', command=self._open_add_supplier).pack(side='right', padx=(0, 8))
        ttk.Button(header, text="+ Add Category",
                   style='Accent.TButton', command=self._open_add_category).pack(side='right', padx=(0, 8))

        # ── Inventory table ───────────────────────────────────
        table_frame = tk.Frame(self, bg=C['bg'])
        table_frame.pack(fill='both', expand=True, padx=24, pady=(0, 16))

        cols = ('Inv ID', 'Batch', 'Product', 'Category', 'Supplier',
                'Mfg Date', 'Expiry Date', 'Cost/Unit', 'Qty Available', 'Status')
        self.tree = ttk.Treeview(table_frame, columns=cols, show='headings')
        widths = [55, 55, 160, 110, 140, 100, 100, 80, 110, 110]
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

        self.tree.tag_configure('expired',  background='#3b1e2e', foreground=C['danger'])
        self.tree.tag_configure('expiring', background='#3b3120', foreground=C['warning'])
        self.tree.tag_configure('ok',       background=C['card'],  foreground=C['text'])

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            rows = get_all_inventory()
            for r in rows:
                status = r['expiry_status']
                tag = 'expired' if status == 'Expired' else \
                      ('expiring' if status == 'Expiring Soon' else 'ok')
                self.tree.insert('', 'end', values=(
                    r['inventory_id'], r['batch_id'], r['product_name'],
                    r['category_name'], r['supplier_name'],
                    str(r['manufacture_date']), str(r['expiry_date']),
                    f"₹{r['cost_price']}", r['quantity_available'], status
                ), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load inventory:\n{e}")

    # ── Add Batch Dialog ──────────────────────────────────────
    def _open_add_batch(self):
        win = _Dialog(self, self.colors, title="Add Stock Batch")
        C = self.colors

        try:
            products  = get_all_products()
            suppliers = get_all_suppliers()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load data:\n{e}")
            win.destroy()
            return

        product_map  = {p['product_name']: p['product_id'] for p in products}
        supplier_map = {s['supplier_name']: s['supplier_id'] for s in suppliers}

        fields = {}
        _form_label(win.body, C, "Product")
        fields['product'] = _form_combo(win.body, C, list(product_map.keys()))
        _form_label(win.body, C, "Supplier")
        fields['supplier'] = _form_combo(win.body, C, list(supplier_map.keys()))
        _form_label(win.body, C, "Manufacture Date (YYYY-MM-DD)")
        fields['mfg'] = _form_entry(win.body, C, placeholder=str(date.today()))
        _form_label(win.body, C, "Expiry Date (YYYY-MM-DD)")
        fields['exp'] = _form_entry(win.body, C)
        _form_label(win.body, C, "Cost Price per Unit (₹)")
        fields['cost'] = _form_entry(win.body, C, placeholder="0.00")
        _form_label(win.body, C, "Quantity Received")
        fields['qty'] = _form_entry(win.body, C, placeholder="0")

        def submit():
            try:
                pid  = product_map[fields['product'].get()]
                sid  = supplier_map[fields['supplier'].get()]
                mfg  = fields['mfg'].get().strip()
                exp  = fields['exp'].get().strip()
                cost = float(fields['cost'].get().strip())
                qty  = int(fields['qty'].get().strip())
                result = add_batch(pid, sid, mfg, exp, cost, qty)
                messagebox.showinfo("Success",
                    f"✅ Batch #{result['batch_id']} added with {result['quantity_added']} units.")
                win.destroy()
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(win.body, text="Add Batch", style='Accent.TButton',
                   command=submit).pack(pady=16)

    # ── Add Product Dialog ────────────────────────────────────
    def _open_add_product(self):
        win = _Dialog(self, self.colors, title="Add New Product")
        C = self.colors

        try:
            categories = get_all_categories()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            win.destroy()
            return

        cat_map = {c['category_name']: c['category_id'] for c in categories}

        fields = {}
        _form_label(win.body, C, "Product Name")
        fields['name'] = _form_entry(win.body, C)
        _form_label(win.body, C, "Category")
        fields['cat'] = _form_combo(win.body, C, list(cat_map.keys()))
        _form_label(win.body, C, "Reorder Level")
        fields['reorder'] = _form_entry(win.body, C, placeholder="10")

        def submit():
            try:
                name    = fields['name'].get().strip()
                cat_id  = cat_map[fields['cat'].get()]
                reorder = int(fields['reorder'].get().strip() or 10)
                if not name:
                    raise ValueError("Product name cannot be empty.")
                pid = add_product(name, cat_id, reorder)
                messagebox.showinfo("Success", f"✅ Product '{name}' added (ID: {pid}).")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(win.body, text="Add Product", style='Accent.TButton',
                   command=submit).pack(pady=16)

    # ── Add Supplier Dialog ───────────────────────────────────
    def _open_add_supplier(self):
        win = _Dialog(self, self.colors, title="Add New Supplier")
        C = self.colors

        fields = {}
        _form_label(win.body, C, "Supplier Name")
        fields['name']  = _form_entry(win.body, C)
        _form_label(win.body, C, "Phone")
        fields['phone'] = _form_entry(win.body, C)
        _form_label(win.body, C, "Email")
        fields['email'] = _form_entry(win.body, C)

        def submit():
            try:
                name  = fields['name'].get().strip()
                phone = fields['phone'].get().strip()
                email = fields['email'].get().strip()
                if not name:
                    raise ValueError("Supplier name cannot be empty.")
                sid = add_supplier(name, phone, email)
                messagebox.showinfo("Success", f"✅ Supplier '{name}' added (ID: {sid}).")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(win.body, text="Add Supplier", style='Accent.TButton',
                   command=submit).pack(pady=16)

    # ── Add Category Dialog ───────────────────────────────────
    def _open_add_category(self):
        win = _Dialog(self, self.colors, title="Add New Category")
        C = self.colors

        fields = {}
        _form_label(win.body, C, "Category Name")
        fields['name'] = _form_entry(win.body, C)

        def submit():
            try:
                name = fields['name'].get().strip()
                if not name:
                    raise ValueError("Category name cannot be empty.")
                cid = add_category(name)
                messagebox.showinfo("Success", f"✅ Category '{name}' added (ID: {cid}).")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(win.body, text="Add Category", style='Accent.TButton',
                   command=submit).pack(pady=16)


# ─────────────────────────────────────────────────────────────
# Shared dialog and form helpers
# ─────────────────────────────────────────────────────────────

class _Dialog(tk.Toplevel):
    def __init__(self, parent, colors, title="Dialog"):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=colors['bg'])
        self.resizable(False, False)
        self.grab_set()
        # Centre on parent
        self.geometry("420x520")
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width()  - 420) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 520) // 2
        self.geometry(f"+{x}+{y}")

        tk.Label(self, text=title, bg=colors['bg'], fg=colors['accent'],
                 font=('Segoe UI', 13, 'bold')).pack(pady=(16, 8))

        self.body = tk.Frame(self, bg=colors['bg'])
        self.body.pack(fill='both', expand=True, padx=24)


def _form_label(parent, C, text):
    tk.Label(parent, text=text, bg=C['bg'], fg=C['text_dim'],
             font=('Segoe UI', 9)).pack(anchor='w', pady=(8, 1))


def _form_entry(parent, C, placeholder=''):
    e = ttk.Entry(parent, font=('Segoe UI', 10))
    e.pack(fill='x', ipady=4)
    if placeholder:
        e.insert(0, placeholder)
    return e


def _form_combo(parent, C, values):
    cb = ttk.Combobox(parent, values=values, state='readonly',
                      font=('Segoe UI', 10))
    cb.pack(fill='x', ipady=4)
    if values:
        cb.current(0)
    return cb
